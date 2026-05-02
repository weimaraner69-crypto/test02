"""
学習サービス（learning/service.py）に対する単体テスト
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from src.core.exceptions import ValidationError
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
    """カタログ未登録の理科・1 年は None を返す。"""
    assert svc.get_content_for_grade(1, Subject.SCIENCE) is None


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
