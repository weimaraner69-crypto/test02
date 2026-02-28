"""学年バリデーションのテスト（境界値テスト含む）。"""

import pytest
from mirastudy.core.exceptions import InvalidGradeError
from mirastudy.core.models import Stage
from mirastudy.domain.grade_validator import (
    GRADE_RANGES,
    get_grade_label,
    is_valid_grade,
    validate_grade,
)


class TestGradeRanges:
    """GRADE_RANGES 定数のテスト。"""

    def test_es_range(self) -> None:
        """小学校は1〜6年。"""
        assert GRADE_RANGES[Stage.ES] == (1, 6)

    def test_jhs_range(self) -> None:
        """中学校は1〜3年。"""
        assert GRADE_RANGES[Stage.JHS] == (1, 3)

    def test_hs_range(self) -> None:
        """高校は1〜3年。"""
        assert GRADE_RANGES[Stage.HS] == (1, 3)


class TestValidateGrade:
    """validate_grade の境界値テスト。"""

    # 小学校境界値
    @pytest.mark.parametrize("grade", [1, 3, 6])
    def test_es_valid_grades(self, grade: int) -> None:
        """小学校の有効な学年（1〜6）は例外を発生させない。"""
        validate_grade(Stage.ES, grade)  # 例外なし

    def test_es_grade_0_rejected(self) -> None:
        """小学校の学年0は無効（下限未満）。"""
        with pytest.raises(InvalidGradeError):
            validate_grade(Stage.ES, 0)

    def test_es_grade_7_rejected(self) -> None:
        """小学校の学年7は無効（上限超過）。"""
        with pytest.raises(InvalidGradeError):
            validate_grade(Stage.ES, 7)

    # 中学校境界値
    @pytest.mark.parametrize("grade", [1, 2, 3])
    def test_jhs_valid_grades(self, grade: int) -> None:
        """中学校の有効な学年（1〜3）は例外を発生させない。"""
        validate_grade(Stage.JHS, grade)

    def test_jhs_grade_0_rejected(self) -> None:
        """中学校の学年0は無効。"""
        with pytest.raises(InvalidGradeError):
            validate_grade(Stage.JHS, 0)

    def test_jhs_grade_4_rejected(self) -> None:
        """中学校の学年4は無効（上限超過）。"""
        with pytest.raises(InvalidGradeError):
            validate_grade(Stage.JHS, 4)


class TestIsValidGrade:
    """is_valid_grade の真偽値テスト。"""

    def test_es_grade_1_valid(self) -> None:
        """小学校1年は有効。"""
        assert is_valid_grade(Stage.ES, 1) is True

    def test_es_grade_6_valid(self) -> None:
        """小学校6年は有効。"""
        assert is_valid_grade(Stage.ES, 6) is True

    def test_es_grade_0_invalid(self) -> None:
        """小学校0年は無効。"""
        assert is_valid_grade(Stage.ES, 0) is False

    def test_es_grade_7_invalid(self) -> None:
        """小学校7年は無効。"""
        assert is_valid_grade(Stage.ES, 7) is False


class TestGetGradeLabel:
    """get_grade_label のテスト。"""

    @pytest.mark.parametrize("grade,expected", [
        (1, "第1学年"),
        (3, "第3学年"),
        (6, "第6学年"),
    ])
    def test_grade_label_format(self, grade: int, expected: str) -> None:
        """学年ラベルが正しいフォーマットで返される。"""
        assert get_grade_label(grade) == expected
