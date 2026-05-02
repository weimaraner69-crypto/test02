"""
学習ドメイン：科目・学年・コンテンツカタログ・クイズ結果の定義
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from src.core.exceptions import ValidationError


class Subject(Enum):
    """学習科目"""

    MATH = "算数"
    JAPANESE = "国語"
    SCIENCE = "理科"
    SOCIAL = "社会"
    ENGLISH = "英語"


def validate_grade(grade: int) -> int:
    """学年を検証する（1〜6）。範囲外は ValidationError を送出する。"""
    if not isinstance(grade, int) or grade < 1 or grade > 6:
        raise ValidationError(f"学年は 1〜6 の整数で指定してください: {grade!r}")
    return grade


@dataclass
class LearningContent:
    """学年・科目に対応する学習コンテンツ"""

    subject: Subject
    grade: int
    title: str
    description: str
    sample_topics: list[str] = field(default_factory=list)


# -----------------------------------------------------------------
# コンテンツカタログ（算数・国語 各6学年、小学校学習指導要領準拠）
# -----------------------------------------------------------------
CONTENT_CATALOG: dict[tuple[Subject, int], LearningContent] = {
    # ── 算数 ──
    (Subject.MATH, 1): LearningContent(
        subject=Subject.MATH,
        grade=1,
        title="数と計算の基礎",
        description="10 までの数の読み書きとたし算・ひき算の基礎を学ぶ。",
        sample_topics=["1〜10 の数", "たし算", "ひき算", "大きさくらべ"],
    ),
    (Subject.MATH, 2): LearningContent(
        subject=Subject.MATH,
        grade=2,
        title="かけ算と図形",
        description="九九のかけ算を習得し、三角形・四角形などの図形を学ぶ。",
        sample_topics=["九九", "かけ算", "三角形", "四角形", "長さの単位"],
    ),
    (Subject.MATH, 3): LearningContent(
        subject=Subject.MATH,
        grade=3,
        title="わり算と小数・分数入門",
        description="わり算の意味を理解し、小数と分数の初歩を学ぶ。",
        sample_topics=["わり算", "小数", "分数", "円と球", "重さの単位"],
    ),
    (Subject.MATH, 4): LearningContent(
        subject=Subject.MATH,
        grade=4,
        title="大きな数・面積と図形",
        description="億や兆の大きな数、面積の計算、垂直・平行などの図形を学ぶ。",
        sample_topics=["億・兆", "面積", "垂直と平行", "四角形の種類", "折れ線グラフ"],
    ),
    (Subject.MATH, 5): LearningContent(
        subject=Subject.MATH,
        grade=5,
        title="分数の計算と割合",
        description="分数のたし算・ひき算・かけ算、割合・百分率を学ぶ。",
        sample_topics=["分数のたし算", "分数のひき算", "割合", "百分率", "単位量あたり"],
    ),
    (Subject.MATH, 6): LearningContent(
        subject=Subject.MATH,
        grade=6,
        title="比と速さ・文字式入門",
        description="比・速さ・文字を使った式など中学数学への橋渡しを学ぶ。",
        sample_topics=["比", "速さ", "文字と式", "円の面積", "体積"],
    ),
    # ── 国語 ──
    (Subject.JAPANESE, 1): LearningContent(
        subject=Subject.JAPANESE,
        grade=1,
        title="ひらがな・カタカナと読み書き",
        description="ひらがな・カタカナの読み書き、基本的な漢字 80 字を学ぶ。",
        sample_topics=["ひらがな", "カタカナ", "漢字80字", "文の組み立て", "音読"],
    ),
    (Subject.JAPANESE, 2): LearningContent(
        subject=Subject.JAPANESE,
        grade=2,
        title="漢字と文章読解の基礎",
        description="漢字 160 字の習得と、短い文章の読解・作文を学ぶ。",
        sample_topics=["漢字160字", "文章読解", "作文", "主語・述語", "句読点"],
    ),
    (Subject.JAPANESE, 3): LearningContent(
        subject=Subject.JAPANESE,
        grade=3,
        title="物語・説明文の読解",
        description="物語文・説明文を読み、段落・要約の方法を学ぶ。",
        sample_topics=["物語文", "説明文", "段落", "要約", "漢字200字"],
    ),
    (Subject.JAPANESE, 4): LearningContent(
        subject=Subject.JAPANESE,
        grade=4,
        title="ことわざ・慣用句と文法基礎",
        description="ことわざ・慣用句を習得し、修飾語・接続語などの文法を学ぶ。",
        sample_topics=["ことわざ", "慣用句", "修飾語", "接続語", "漢字200字"],
    ),
    (Subject.JAPANESE, 5): LearningContent(
        subject=Subject.JAPANESE,
        grade=5,
        title="敬語と文学・報告文",
        description="敬語の使い方、文学的文章の読解、報告文・意見文の書き方を学ぶ。",
        sample_topics=["敬語", "詩・俳句", "報告文", "意見文", "漢字185字"],
    ),
    (Subject.JAPANESE, 6): LearningContent(
        subject=Subject.JAPANESE,
        grade=6,
        title="論説文・古典入門と表現技法",
        description="論説文の読解、古文・漢文の入門、表現技法を学ぶ。",
        sample_topics=["論説文", "古文入門", "漢文入門", "表現技法", "漢字181字"],
    ),
}


def get_content(subject: Subject, grade: int) -> LearningContent | None:
    """科目と学年に対応する LearningContent を返す。存在しない場合は None。"""
    return CONTENT_CATALOG.get((subject, grade))


@dataclass
class QuizResult:
    """クイズ回答結果"""

    uid: str
    subject: Subject
    topic: str
    is_correct: bool
    answered_at: str  # ISO 8601 UTC（例: "2026-05-02T10:00:00Z"）
