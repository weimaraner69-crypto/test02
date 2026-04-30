"""ドメインモデルの不変条件テスト。"""

import pytest

from mirastudy.core.models import (
    PerformanceRecord,
    Question,
    Stage,
    Subject,
    UserRole,
)


class TestPerformanceRecord:
    """PerformanceRecord の不変条件テスト。"""

    def test_valid_performance(self) -> None:
        """有効なパフォーマンス記録は作成できる。"""
        perf = PerformanceRecord(attempted=5, correct=4, hints_used=2)
        assert perf.attempted == 5
        assert perf.correct == 4
        assert perf.hints_used == 2

    def test_negative_attempted_rejected(self) -> None:
        """試行回数が負の場合はエラー。"""
        with pytest.raises(AssertionError):
            PerformanceRecord(attempted=-1, correct=0, hints_used=0)

    def test_negative_correct_rejected(self) -> None:
        """正解数が負の場合はエラー。"""
        with pytest.raises(AssertionError):
            PerformanceRecord(attempted=5, correct=-1, hints_used=0)

    def test_correct_exceeds_attempted_rejected(self) -> None:
        """正解数が試行回数を超える場合はエラー。"""
        with pytest.raises(AssertionError):
            PerformanceRecord(attempted=3, correct=5, hints_used=0)

    def test_zero_performance(self) -> None:
        """すべてゼロは有効（まだ試行していない）。"""
        perf = PerformanceRecord(attempted=0, correct=0, hints_used=0)
        assert perf.attempted == 0


class TestQuestion:
    """Question の不変条件テスト。"""

    def test_valid_question(self) -> None:
        """有効な問題は作成できる。"""
        q = Question(text="1 + 1 = ?", question_type="choice", options=["1", "2", "3"])
        assert q.text == "1 + 1 = ?"

    def test_empty_text_rejected(self) -> None:
        """空の問題文はエラー。"""
        with pytest.raises(AssertionError):
            Question(text="", question_type="choice", options=None)


class TestEnums:
    """列挙型の値テスト。"""

    def test_stage_values(self) -> None:
        """Stage 列挙型の値が正しい。"""
        assert Stage.ES.value == "ES"
        assert Stage.JHS.value == "JHS"
        assert Stage.HS.value == "HS"

    def test_user_role_values(self) -> None:
        """UserRole 列挙型の値が正しい。"""
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.STUDENT.value == "student"

    def test_subject_values(self) -> None:
        """Subject 列挙型の値が正しい。"""
        assert Subject.MATH.value == "math"
        assert Subject.JAPANESE.value == "japanese"
