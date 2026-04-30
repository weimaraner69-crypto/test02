"""MiraStudy v2.0 ドメインモデル定義。

学習セッション・問題・成績などのコアエンティティを定義する。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

# ---------------------------------------------------------------------------
# 列挙型
# ---------------------------------------------------------------------------


class Stage(Enum):
    """学校段階を表す列挙型。"""

    ES = "ES"  # 小学校（Elementary School）
    JHS = "JHS"  # 中学校（Junior High School）
    HS = "HS"  # 高校（High School）


class Subject(Enum):
    """学習科目を表す列挙型。"""

    MATH = "math"
    JAPANESE = "japanese"
    SCIENCE = "science"
    SOCIAL = "social"
    ENGLISH = "english"


class UserRole(Enum):
    """ユーザーロールを表す列挙型。"""

    ADMIN = "admin"  # 管理者（父）
    STUDENT = "student"  # 学生（子）


# ---------------------------------------------------------------------------
# データクラス
# ---------------------------------------------------------------------------


@dataclass
class CurriculumReference:
    """カリキュラム参照情報。

    Google Drive のファイルと教科書の章・ページを紐付ける。

    Attributes:
        drive_file_id: Google Drive ファイル ID。
        chapter: 章番号または章タイトル。
        pages: 対象ページ範囲（例: "12-15"）。
    """

    drive_file_id: str
    chapter: str
    pages: str


@dataclass
class PerformanceRecord:
    """学習セッションのパフォーマンス記録。

    不変条件 (Invariant):
        - ``attempted`` は 0 以上であること
        - ``correct`` は 0 以上であること
        - ``hints_used`` は 0 以上であること
        - ``correct`` は ``attempted`` を超えないこと

    Attributes:
        attempted: 試行回数。
        correct: 正解数。
        hints_used: ヒント使用回数。

    Raises:
        AssertionError: 不変条件に違反した場合。
    """

    attempted: int
    correct: int
    hints_used: int

    def __post_init__(self) -> None:
        """不変条件を検証する。"""
        assert self.attempted >= 0, f"attempted は 0 以上である必要があります: {self.attempted}"
        assert self.correct >= 0, f"correct は 0 以上である必要があります: {self.correct}"
        assert self.hints_used >= 0, f"hints_used は 0 以上である必要があります: {self.hints_used}"
        assert self.correct <= self.attempted, (
            f"correct ({self.correct}) は attempted ({self.attempted}) を超えることはできません"
        )


@dataclass
class Question:
    """学習問題を表すデータクラス。

    不変条件 (Invariant):
        - ``text`` は空文字列ではないこと

    Attributes:
        text: 問題文。空文字列は許可しない。
        question_type: 問題種別。"choice"（選択）・"calculation"（計算）・
            "description"（記述）のいずれか。
        options: 選択問題の選択肢リスト。記述・計算問題の場合は None。

    Raises:
        AssertionError: 不変条件に違反した場合。
    """

    text: str
    question_type: str
    options: list[str] | None

    def __post_init__(self) -> None:
        """不変条件を検証する。"""
        assert self.text, "text は空文字列であってはなりません"


@dataclass
class Answer:
    """問題の正解と解説を保持するデータクラス。

    Attributes:
        correct: 正解テキスト。
        explanation: 解説テキスト。
    """

    correct: str
    explanation: str


@dataclass
class Hints:
    """段階的ヒントを保持するデータクラス。

    Attributes:
        level1: レベル1ヒント（軽いヒント）。
        level2: レベル2ヒント（中程度のヒント）。
        level3: レベル3ヒント（詳細なヒント）。
    """

    level1: str
    level2: str
    level3: str


def _default_performance() -> PerformanceRecord:
    """デフォルトの空パフォーマンス記録を返す。"""
    return PerformanceRecord(attempted=0, correct=0, hints_used=0)


@dataclass
class LearningSession:
    """学習セッションを表すデータクラス。

    1回の学習セッション全体の情報を集約する。

    Attributes:
        session_id: セッションの一意識別子。
        date: セッション実施日（ISO 8601 形式推奨）。
        stage: 学校段階。
        subject: 学習科目。
        topic: 学習トピック名。
        questions: セッション内の問題リスト。
        performance: セッションのパフォーマンス記録。
        curriculum_reference: カリキュラム参照情報（任意）。
    """

    session_id: str
    date: str
    stage: Stage
    subject: Subject
    topic: str
    questions: list[Question] = field(default_factory=list)
    performance: PerformanceRecord = field(default_factory=_default_performance)
    curriculum_reference: CurriculumReference | None = None
