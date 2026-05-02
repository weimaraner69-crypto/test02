"""
ドメイン層の学習モジュール（learning.py）に対する単体テスト
"""

from __future__ import annotations

import pytest
from src.core.exceptions import ValidationError
from src.domain.learning import (
    CONTENT_CATALOG,
    LearningContent,
    Subject,
    get_content,
    validate_grade,
)


# ─────────────────────────────────────────────
# validate_grade: 正常系
# ─────────────────────────────────────────────
@pytest.mark.parametrize("grade", [1, 3, 6])
def test_validate_grade_valid(grade: int) -> None:
    """境界値 1・中間値 3・上限 6 はそのまま返す。"""
    assert validate_grade(grade) == grade


# ─────────────────────────────────────────────
# validate_grade: 異常系
# ─────────────────────────────────────────────
@pytest.mark.parametrize("grade", [0, 7, -1, "3"])
def test_validate_grade_invalid(grade) -> None:
    """0・7・負数・文字列は ValidationError を送出する。"""
    with pytest.raises(ValidationError):
        validate_grade(grade)


# ─────────────────────────────────────────────
# CONTENT_CATALOG: 算数 6 学年すべて存在する
# ─────────────────────────────────────────────
@pytest.mark.parametrize("grade", range(1, 7))
def test_content_catalog_math_all_grades(grade: int) -> None:
    """CONTENT_CATALOG に (Subject.MATH, 1)〜(Subject.MATH, 6) がある。"""
    assert (Subject.MATH, grade) in CONTENT_CATALOG


# ─────────────────────────────────────────────
# CONTENT_CATALOG: 国語 6 学年すべて存在する
# ─────────────────────────────────────────────
@pytest.mark.parametrize("grade", range(1, 7))
def test_content_catalog_japanese_all_grades(grade: int) -> None:
    """CONTENT_CATALOG に (Subject.JAPANESE, 1)〜(Subject.JAPANESE, 6) がある。"""
    assert (Subject.JAPANESE, grade) in CONTENT_CATALOG


# ─────────────────────────────────────────────
# get_content: 登録済みエントリを返す
# ─────────────────────────────────────────────
def test_get_content_math_grade3_returns_content() -> None:
    """算数・3 年は登録済みなので LearningContent インスタンスを返す。"""
    content = get_content(Subject.MATH, 3)
    assert isinstance(content, LearningContent)


# ─────────────────────────────────────────────
# get_content: 未登録エントリは None
# ─────────────────────────────────────────────
def test_get_content_unregistered_returns_none() -> None:
    """理科・1 年はカタログ未登録なので None を返す。"""
    assert get_content(Subject.SCIENCE, 1) is None


# ─────────────────────────────────────────────
# LearningContent: フィールドが空でない
# ─────────────────────────────────────────────
def test_learning_content_fields_are_nonempty() -> None:
    """算数・3 年コンテンツのフィールドがすべて有効な値を持つ。"""
    content = get_content(Subject.MATH, 3)
    assert content is not None
    assert content.grade == 3
    assert content.subject == Subject.MATH
    assert content.title != ""
    assert len(content.sample_topics) > 0


# ─────────────────────────────────────────────
# Subject Enum: value が日本語
# ─────────────────────────────────────────────
@pytest.mark.parametrize(
    "subject, expected_value",
    [
        (Subject.MATH, "算数"),
        (Subject.JAPANESE, "国語"),
        (Subject.SCIENCE, "理科"),
        (Subject.SOCIAL, "社会"),
        (Subject.ENGLISH, "英語"),
    ],
)
def test_subject_enum_value_is_japanese(subject: Subject, expected_value: str) -> None:
    """Subject の value がすべて日本語文字列である。"""
    assert subject.value == expected_value
