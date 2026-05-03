"""
学習サービス：コンテンツ配信・問題生成・回答記録・進捗集計
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from src.core.exceptions import ValidationError
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

    def __init__(
        self,
        profile_service: UserProfileService,
        gemini_service: GeminiService,
    ) -> None:
        self._profile = profile_service
        self._gemini = gemini_service

    def get_content_for_grade(self, grade: int, subject: Subject) -> LearningContent | None:
        """学年と科目に対応するコンテンツを返す。"""
        return get_content(subject, grade)

    @trace_llm_call(model_name="gemini")
    def generate_question(self, uid: str, grade: int, subject: Subject, topic: str) -> dict:
        """Gemini で問題を生成して返す。
        生成結果が None の場合は ValidationError を送出する。
        """
        # 学年バリデーション（1〜6 の整数以外は ValidationError）
        validate_grade(grade)
        # subject バリデーション
        if not isinstance(subject, Subject):
            raise ValidationError(f"subject は Subject 型で指定してください: {subject!r}")
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

    def get_progress_summary(self, uid: str, subject: Subject) -> dict:
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
