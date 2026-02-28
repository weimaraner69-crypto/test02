"""学年バリデーション。

学校段階ごとの有効な学年範囲を定義し、バリデーション関数を提供する。
"""

from mirastudy.core.exceptions import InvalidGradeError
from mirastudy.core.models import Stage


# 学校段階ごとの有効学年範囲: {Stage: (最小学年, 最大学年)}
GRADE_RANGES: dict[Stage, tuple[int, int]] = {
    Stage.ES: (1, 6),   # 小学校: 1〜6年
    Stage.JHS: (1, 3),  # 中学校: 1〜3年
    Stage.HS: (1, 3),   # 高校: 1〜3年
}


def validate_grade(stage: Stage, grade: int) -> None:
    """学年が指定された学校段階の有効範囲内かを検証する。

    Args:
        stage: 学校段階。
        grade: 検証する学年。

    Raises:
        InvalidGradeError: 学年が有効範囲外の場合。
    """
    if not is_valid_grade(stage, grade):
        min_grade, max_grade = GRADE_RANGES[stage]
        raise InvalidGradeError(
            f"学年 {grade} は {stage.value} の有効範囲 ({min_grade}〜{max_grade}) 外です"
        )


def get_grade_label(grade: int) -> str:
    """学年のラベル文字列を返す。

    Args:
        grade: 学年番号。

    Returns:
        "第{grade}学年" 形式の文字列。
    """
    return f"第{grade}学年"


def is_valid_grade(stage: Stage, grade: int) -> bool:
    """学年が指定された学校段階の有効範囲内かを返す。

    Args:
        stage: 学校段階。
        grade: 検証する学年。

    Returns:
        学年が有効範囲内の場合は True、範囲外の場合は False。
    """
    min_grade, max_grade = GRADE_RANGES[stage]
    return min_grade <= grade <= max_grade
