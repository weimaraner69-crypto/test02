"""
学習サービス：コンテンツ配信・問題生成・回答記録・進捗集計
"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from src.core.exceptions import RateLimitError, ValidationError
from src.domain.learning import LearningContent, Subject, get_content, validate_grade
from src.observability.tracing import trace_llm_call

if TYPE_CHECKING:
    from src.gemini.service import GeminiService
    from src.user.profile import UserProfileService


def _topic_key(subject: Subject, topic: str) -> str:
    """UserProfileService に渡すトピックキーを生成する。"""
    return f"{subject.value}:{topic}"


class LearningService:
    """学習機能の統合サービス。"""

    _RATE_LIMIT_WINDOW_SECONDS = 60
    _USER_RATE_LIMIT_PER_MIN = 10
    _GLOBAL_RATE_LIMIT_PER_MIN = 50
    _SESSION_WARN_SECONDS = 3600
    _SESSION_FORCE_STOP_SECONDS = 7200

    def __init__(
        self,
        profile_service: UserProfileService,
        gemini_service: GeminiService,
    ) -> None:
        self._profile = profile_service
        self._gemini = gemini_service
        self._user_call_timestamps: dict[str, list[float]] = {}
        self._global_call_timestamps: list[float] = []
        self._session_started_at: dict[str, float] = {}

    @staticmethod
    def _prune_old_timestamps(timestamps: list[float], now: float, window: int) -> list[float]:
        """ウィンドウ外のタイムスタンプを除外する。"""
        return [ts for ts in timestamps if now - ts <= window]

    def _check_rate_limit(self, uid: str, now: float) -> None:
        """C-003: ユーザー単位/全体単位のレート制限を検証する。"""
        user_calls = self._prune_old_timestamps(
            self._user_call_timestamps.get(uid, []),
            now,
            self._RATE_LIMIT_WINDOW_SECONDS,
        )
        global_calls = self._prune_old_timestamps(
            self._global_call_timestamps,
            now,
            self._RATE_LIMIT_WINDOW_SECONDS,
        )

        self._user_call_timestamps[uid] = user_calls
        self._global_call_timestamps = global_calls

        if len(user_calls) >= self._USER_RATE_LIMIT_PER_MIN:
            raise RateLimitError(
                "レート制限に達しました。しばらく時間をおいてから再試行してください。",
                reason_code="C003_rate_limit_exceeded",
            )
        if len(global_calls) >= self._GLOBAL_RATE_LIMIT_PER_MIN:
            raise RateLimitError(
                "現在アクセスが集中しています。しばらく時間をおいてから再試行してください。",
                reason_code="C003_rate_limit_exceeded",
            )

        self._user_call_timestamps[uid].append(now)
        self._global_call_timestamps.append(now)

    def _check_session_duration(self, uid: str, now: float) -> None:
        """C-004: セッション継続時間を検証する。"""
        started_at = self._session_started_at.setdefault(uid, now)
        elapsed_seconds = now - started_at

        if elapsed_seconds > self._SESSION_FORCE_STOP_SECONDS:
            raise ValidationError(
                "学習セッションが120分を超えました。進捗を保存して再開してください。",
                reason_code="C004_session_timeout",
            )
        if elapsed_seconds > self._SESSION_WARN_SECONDS:
            raise ValidationError(
                "学習セッションが60分を超えました。休憩してから再開してください。",
                reason_code="C004_session_timeout",
            )

    def get_content_for_grade(self, grade: int, subject: Subject) -> LearningContent | None:
        """学年と科目に対応するコンテンツを返す。"""
        return get_content(subject, grade)

    @trace_llm_call(model_name="gemini")
    def generate_question(
        self, uid: str, grade: int, subject: Subject, topic: str
    ) -> dict[str, Any]:
        """Gemini で問題を生成して返す。
        生成結果が None の場合は ValidationError を送出する。
        """
        # 学年バリデーション（1〜6 の整数以外は ValidationError）
        validate_grade(grade)
        # subject バリデーション
        if not isinstance(subject, Subject):
            raise ValidationError(f"subject は Subject 型で指定してください: {subject!r}")
        now = time.time()
        self._check_session_duration(uid, now)
        self._check_rate_limit(uid, now)
        result = self._gemini.generate_question(
            context=f"{subject.value} {topic}",
            topic=topic,
            grade=grade,
        )
        if result is None:
            raise ValidationError(
                f"Gemini から問題を取得できませんでした: "
                f"subject={subject.value}, grade={grade}, topic={topic}"
            )
        return result

    def record_answer(self, uid: str, subject: Subject, topic: str, is_correct: bool) -> None:
        """回答結果を学習進捗として保存する。
        既存進捗がある場合は total/correct をインクリメントし、
        ない場合は新規エントリを作成する。
        保存失敗（False 返却）時は ValidationError を送出する。
        """
        # subject バリデーション
        if not isinstance(subject, Subject):
            raise ValidationError(f"subject は Subject 型で指定してください: {subject!r}")
        key = _topic_key(subject, topic)
        existing = self._profile.get_learning_progress(uid, key)

        answered_at = datetime.now(tz=UTC).isoformat().replace("+00:00", "Z")

        if existing is not None:
            progress = dict(existing)
            progress["total"] = existing.get("total", 0) + 1
            progress["correct"] = existing.get("correct", 0) + (1 if is_correct else 0)
            progress["last_answered_at"] = answered_at
        else:
            progress = {
                "subject": subject.value,
                "topic": topic,
                "total": 1,
                "correct": 1 if is_correct else 0,
                "last_answered_at": answered_at,
            }

        ok = self._profile.set_learning_progress(uid, key, progress)
        if not ok:
            raise ValidationError(
                f"学習進捗の保存に失敗しました: uid={uid}, subject={subject.value}, topic={topic}"
            )

    def get_progress_summary(self, uid: str, subject: Subject) -> dict[str, Any]:
        """科目全体の進捗サマリーを返す。
        対象科目のすべての topic を取得し、正答率・総問題数・正解数を集計する。
        """
        # subject バリデーション
        if not isinstance(subject, Subject):
            raise ValidationError(f"subject は Subject 型で指定してください: {subject!r}")
        total = 0
        correct = 0

        # UserProfileService の公開 API 経由で全件取得する
        all_progress = self._profile.list_all_learning_progress(uid)

        for progress in all_progress:
            # subject フィールドで対象科目のみに絞り込む
            if progress.get("subject") == subject.value:
                total += progress.get("total", 0)
                correct += progress.get("correct", 0)

        accuracy = correct / total if total > 0 else 0.0
        return {
            "subject": subject.value,
            "total": total,
            "correct": correct,
            "accuracy": accuracy,
        }
