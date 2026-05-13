"""
学習サービス（learning/service.py）に対する単体テスト
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import pytest
from src.core.exceptions import RateLimitError, ValidationError
from src.domain.learning import LearningContent, Subject
from src.gemini.service import GeminiService
from src.learning.service import LearningService
from src.user.profile import UserProfileService

# ─────────────────────────────────────────────
# フィクスチャ
# ─────────────────────────────────────────────


@pytest.fixture
def svc():
    """インメモリ DB + モック GeminiService の LearningService を返す。"""
    profile = UserProfileService(":memory:")
    gemini = GeminiService(api_key="test-key")
    return LearningService(profile_service=profile, gemini_service=gemini)


@pytest.fixture
def svc_with_uid(svc):
    """テスト用 uid に紐づいたプロファイルをセットアップ済みのサービスと uid を返す。"""
    uid = "test-uid-001"
    svc._profile.set_profile(uid, {"uid": uid, "role": "student"})
    return svc, uid


# ─────────────────────────────────────────────
# get_content_for_grade
# ─────────────────────────────────────────────


def test_get_content_for_grade_math_grade3(svc) -> None:
    """登録済みの算数・3 年は LearningContent を返す。"""
    result = svc.get_content_for_grade(3, Subject.MATH)
    assert isinstance(result, LearningContent)


def test_get_content_for_grade_unregistered_returns_none(svc) -> None:
    """カタログ未登録の学年 7（全科目で存在しない）は None を返す。
    N-008 で理科・社会・英語 各6学年がカタログ追加済みのため、
    未登録の検証には範囲外の grade=7 を使用する。
    """
    assert svc.get_content_for_grade(7, Subject.MATH) is None


# ─────────────────────────────────────────────
# generate_question
# ─────────────────────────────────────────────


def test_generate_question_returns_question_key(svc_with_uid) -> None:
    """正常時: 戻り値 dict に "question" キーが含まれる。"""
    service, uid = svc_with_uid
    result = service.generate_question(uid, grade=3, subject=Subject.MATH, topic="わり算")
    assert "question" in result


def test_generate_question_gemini_none_raises(svc_with_uid) -> None:
    """Gemini が None を返す場合は ValidationError を送出する。"""
    service, uid = svc_with_uid
    with (
        patch.object(service._gemini, "generate_question", return_value=None),
        pytest.raises(ValidationError),
    ):
        service.generate_question(uid, grade=3, subject=Subject.MATH, topic="わり算")


# ─────────────────────────────────────────────
# record_answer / get_progress_summary
# ─────────────────────────────────────────────


def test_record_answer_correct_once(svc_with_uid) -> None:
    """正解 1 回記録後: total=1, correct=1。"""
    service, uid = svc_with_uid
    service.record_answer(uid, Subject.MATH, "わり算", is_correct=True)
    summary = service.get_progress_summary(uid, Subject.MATH)
    assert summary["total"] == 1
    assert summary["correct"] == 1


def test_record_answer_incorrect_once(svc_with_uid) -> None:
    """不正解 1 回記録後: total=1, correct=0。"""
    service, uid = svc_with_uid
    service.record_answer(uid, Subject.MATH, "わり算", is_correct=False)
    summary = service.get_progress_summary(uid, Subject.MATH)
    assert summary["total"] == 1
    assert summary["correct"] == 0


def test_record_answer_accuracy_multiple_attempts(svc_with_uid) -> None:
    """正解 2・不正解 1 → total=3, correct=2, accuracy≈0.667。"""
    service, uid = svc_with_uid
    service.record_answer(uid, Subject.MATH, "わり算", is_correct=True)
    service.record_answer(uid, Subject.MATH, "わり算", is_correct=True)
    service.record_answer(uid, Subject.MATH, "わり算", is_correct=False)
    summary = service.get_progress_summary(uid, Subject.MATH)
    assert summary["total"] == 3
    assert summary["correct"] == 2
    assert abs(summary["accuracy"] - 2 / 3) < 1e-6


def test_record_answer_different_topics_independent(svc_with_uid) -> None:
    """別トピックの記録は互いに影響しない。"""
    service, uid = svc_with_uid
    service.record_answer(uid, Subject.MATH, "わり算", is_correct=True)
    service.record_answer(uid, Subject.MATH, "小数", is_correct=False)
    summary = service.get_progress_summary(uid, Subject.MATH)
    assert summary["total"] == 2
    assert summary["correct"] == 1


def test_get_progress_summary_no_data(svc_with_uid) -> None:
    """回答記録がない場合: total=0, correct=0, accuracy=0.0。"""
    service, uid = svc_with_uid
    summary = service.get_progress_summary(uid, Subject.MATH)
    assert summary["total"] == 0
    assert summary["correct"] == 0
    assert summary["accuracy"] == 0.0


def test_get_progress_summary_excludes_other_subjects(svc_with_uid) -> None:
    """算数で記録後、国語のサマリーは total=0 のままである。"""
    service, uid = svc_with_uid
    service.record_answer(uid, Subject.MATH, "わり算", is_correct=True)
    japanese_summary = service.get_progress_summary(uid, Subject.JAPANESE)
    assert japanese_summary["total"] == 0


def test_record_answer_save_failure_raises(svc_with_uid) -> None:
    """set_learning_progress が False を返す場合は ValidationError を送出する。"""
    service, uid = svc_with_uid
    with (
        patch.object(service._profile, "set_learning_progress", return_value=False),
        pytest.raises(ValidationError),
    ):
        service.record_answer(uid, Subject.MATH, "わり算", is_correct=True)


# ─────────────────────────────────────────────
# C-003 API レート制限（境界値）
# ─────────────────────────────────────────────


def test_generate_question_user_rate_limit_at_boundary_allows_10_calls(svc_with_uid) -> None:
    """ユーザー単位しきい値ちょうど（10回/60秒）は許可される。"""
    service, uid = svc_with_uid
    with (
        patch.object(service._gemini, "generate_question", return_value={"question": {}}),
        patch("src.learning.service.time.time", return_value=1000.0),
    ):
        for _ in range(10):
            service.generate_question(uid, grade=3, subject=Subject.MATH, topic="わり算")


def test_generate_question_user_rate_limit_exceeds_rejected_on_11th_call(svc_with_uid) -> None:
    """ユーザー単位しきい値直上（11回目）は RateLimitError で拒否される。"""
    service, uid = svc_with_uid
    with (
        patch.object(service._gemini, "generate_question", return_value={"question": {}}),
        patch("src.learning.service.time.time", return_value=1000.0),
    ):
        for _ in range(10):
            service.generate_question(uid, grade=3, subject=Subject.MATH, topic="わり算")
        with pytest.raises(RateLimitError, match="しばらく時間をおいて") as exc_info:
            service.generate_question(uid, grade=3, subject=Subject.MATH, topic="わり算")
    assert exc_info.value.reason_code == "C003_rate_limit_exceeded"


def test_generate_question_global_rate_limit_exceeds_rejected_on_51st_call(svc) -> None:
    """全体しきい値直上（51回目）は RateLimitError で拒否される。"""
    service = svc
    for i in range(51):
        uid = f"user-{i:02d}"
        service._profile.set_profile(uid, {"uid": uid, "role": "student"})

    with (
        patch.object(service._gemini, "generate_question", return_value={"question": {}}),
        patch("src.learning.service.time.time", return_value=2000.0),
    ):
        for i in range(50):
            uid = f"user-{i:02d}"
            service.generate_question(uid, grade=3, subject=Subject.MATH, topic="わり算")
        with pytest.raises(RateLimitError, match="アクセスが集中") as exc_info:
            service.generate_question("user-50", grade=3, subject=Subject.MATH, topic="わり算")
    assert exc_info.value.reason_code == "C003_rate_limit_exceeded"


# ─────────────────────────────────────────────
# C-004 セッション時間制限（境界値）
# ─────────────────────────────────────────────


def test_generate_question_session_time_at_3600_seconds_allows(svc_with_uid) -> None:
    """警告しきい値ちょうど（3600秒）は許可される。"""
    service, uid = svc_with_uid
    with patch.object(service._gemini, "generate_question", return_value={"question": {}}):
        with patch("src.learning.service.time.time", return_value=1000.0):
            service.generate_question(uid, grade=3, subject=Subject.MATH, topic="わり算")
        with patch("src.learning.service.time.time", return_value=4600.0):
            service.generate_question(uid, grade=3, subject=Subject.MATH, topic="わり算")


def test_generate_question_session_time_warn_over_3600_seconds_rejected(svc_with_uid) -> None:
    """警告しきい値直上（3601秒）は ValidationError で一時停止される。"""
    service, uid = svc_with_uid
    with patch.object(service._gemini, "generate_question", return_value={"question": {}}):
        with patch("src.learning.service.time.time", return_value=1000.0):
            service.generate_question(uid, grade=3, subject=Subject.MATH, topic="わり算")
        with (
            patch("src.learning.service.time.time", return_value=4601.0),
            pytest.raises(ValidationError, match="60分を超えました") as exc_info,
        ):
            service.generate_question(uid, grade=3, subject=Subject.MATH, topic="わり算")
    assert exc_info.value.reason_code == "C004_session_warning"


def test_generate_question_session_time_force_stop_over_7200_seconds_rejected(svc_with_uid) -> None:
    """強制終了しきい値直上（7201秒）は ValidationError で拒否される。"""
    service, uid = svc_with_uid
    with patch.object(service._gemini, "generate_question", return_value={"question": {}}):
        with patch("src.learning.service.time.time", return_value=1000.0):
            service.generate_question(uid, grade=3, subject=Subject.MATH, topic="わり算")
        with (
            patch("src.learning.service.time.time", return_value=8201.0),
            pytest.raises(ValidationError, match="120分を超えました") as exc_info,
        ):
            service.generate_question(uid, grade=3, subject=Subject.MATH, topic="わり算")
    assert exc_info.value.reason_code == "C004_session_forced_stop"


def test_generate_question_rate_limit_persists_after_service_restart() -> None:
    """N-031: サービス再生成後もユーザー単位レート制限が維持される。"""
    db_path = Path("data") / f"learning_runtime_{uuid4().hex}.sqlite"
    uid = "restart-user-001"

    profile1 = UserProfileService(str(db_path))
    profile1.set_profile(uid, {"uid": uid, "role": "student"})
    service1 = LearningService(profile_service=profile1, gemini_service=GeminiService("test-key"))

    with (
        patch.object(service1._gemini, "generate_question", return_value={"question": {}}),
        patch("src.learning.service.time.time", return_value=3000.0),
    ):
        for _ in range(10):
            service1.generate_question(uid, grade=3, subject=Subject.MATH, topic="わり算")
    profile1.close()

    profile2 = UserProfileService(str(db_path))
    service2 = LearningService(profile_service=profile2, gemini_service=GeminiService("test-key"))
    with (
        patch.object(service2._gemini, "generate_question", return_value={"question": {}}),
        patch("src.learning.service.time.time", return_value=3000.0),
        pytest.raises(RateLimitError, match="しばらく時間をおいて") as exc_info,
    ):
        service2.generate_question(uid, grade=3, subject=Subject.MATH, topic="わり算")
    assert exc_info.value.reason_code == "C003_rate_limit_exceeded"
    profile2.close()
    db_path.unlink(missing_ok=True)


def test_generate_question_session_state_persists_after_service_restart() -> None:
    """N-031: サービス再生成後もセッション開始時刻が維持され、警告判定が一貫する。"""
    db_path = Path("data") / f"learning_session_{uuid4().hex}.sqlite"
    uid = "restart-user-002"

    profile1 = UserProfileService(str(db_path))
    profile1.set_profile(uid, {"uid": uid, "role": "student"})
    service1 = LearningService(profile_service=profile1, gemini_service=GeminiService("test-key"))
    with (
        patch.object(service1._gemini, "generate_question", return_value={"question": {}}),
        patch("src.learning.service.time.time", return_value=1000.0),
    ):
        service1.generate_question(uid, grade=3, subject=Subject.MATH, topic="わり算")
    profile1.close()

    profile2 = UserProfileService(str(db_path))
    service2 = LearningService(profile_service=profile2, gemini_service=GeminiService("test-key"))
    with (
        patch.object(service2._gemini, "generate_question", return_value={"question": {}}),
        patch("src.learning.service.time.time", return_value=4601.0),
        pytest.raises(ValidationError, match="60分を超えました") as exc_info,
    ):
        service2.generate_question(uid, grade=3, subject=Subject.MATH, topic="わり算")
    assert exc_info.value.reason_code == "C004_session_warning"
    profile2.close()
    db_path.unlink(missing_ok=True)
