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
    # ── 理科 ──
    (Subject.SCIENCE, 1): LearningContent(
        subject=Subject.SCIENCE,
        grade=1,
        title="いきものとしぜん",
        description="身近な生き物や自然の観察",
        sample_topics=["花の観察", "昆虫のからだ", "季節と生き物"],
    ),
    (Subject.SCIENCE, 2): LearningContent(
        subject=Subject.SCIENCE,
        grade=2,
        title="じしゃくとあかり",
        description="磁石の性質と電気の基礎",
        sample_topics=["磁石の引き合い", "豆電球の回路", "光の進み方"],
    ),
    (Subject.SCIENCE, 3): LearningContent(
        subject=Subject.SCIENCE,
        grade=3,
        title="こんちゅうとしょくぶつ",
        description="昆虫の成長と植物の育ち",
        sample_topics=["アゲハの成長", "ひまわりの成長", "土の中の生き物"],
    ),
    (Subject.SCIENCE, 4): LearningContent(
        subject=Subject.SCIENCE,
        grade=4,
        title="てんきとじょうはつ",
        description="天気の変化と水の状態変化",
        sample_topics=["雲の種類", "水のすがたの変化", "気温の変化"],
    ),
    (Subject.SCIENCE, 5): LearningContent(
        subject=Subject.SCIENCE,
        grade=5,
        title="うごきとちから",
        description="物体の運動とエネルギー",
        sample_topics=["ふりこの運動", "電磁石の働き", "流れる水の働き"],
    ),
    (Subject.SCIENCE, 6): LearningContent(
        subject=Subject.SCIENCE,
        grade=6,
        title="いのちとかんきょう",
        description="生命の連続性と環境問題",
        sample_topics=["人体の仕組み", "生物と環境", "地球と宇宙"],
    ),
    # ── 社会 ──
    (Subject.SOCIAL, 1): LearningContent(
        subject=Subject.SOCIAL,
        grade=1,
        title="がっこうとまち",
        description="学校や町の施設と人々の働き",
        sample_topics=["学校のまわり", "駅や商店街", "働く人たち"],
    ),
    (Subject.SOCIAL, 2): LearningContent(
        subject=Subject.SOCIAL,
        grade=2,
        title="まちのようすとへんか",
        description="町の様子と人々の生活の変化",
        sample_topics=["公共施設", "昔と今の道具", "地域の行事"],
    ),
    (Subject.SOCIAL, 3): LearningContent(
        subject=Subject.SOCIAL,
        grade=3,
        title="わたしたちのまち",
        description="地域の地図と産業・文化",
        sample_topics=["地図の見方", "農家の仕事", "お祭りと文化"],
    ),
    (Subject.SOCIAL, 4): LearningContent(
        subject=Subject.SOCIAL,
        grade=4,
        title="わたしたちのけん",
        description="都道府県の特色と産業",
        sample_topics=["都道府県の地形", "農業と漁業", "伝統工業"],
    ),
    (Subject.SOCIAL, 5): LearningContent(
        subject=Subject.SOCIAL,
        grade=5,
        title="にほんのさんぎょうとくらし",
        description="日本の産業と国際関係",
        sample_topics=["食料生産", "工業生産", "情報化社会"],
    ),
    (Subject.SOCIAL, 6): LearningContent(
        subject=Subject.SOCIAL,
        grade=6,
        title="にほんのれきしとせかい",
        description="日本の歴史と世界との関わり",
        sample_topics=["縄文・弥生時代", "江戸時代", "明治維新と現代"],
    ),
    # ── 英語 ──
    (Subject.ENGLISH, 1): LearningContent(
        subject=Subject.ENGLISH,
        grade=1,
        title="あいさつとかず",
        description="挨拶・数字・色などの基本表現",
        sample_topics=["Hello / Goodbye", "Numbers 1-20", "Colors and Shapes"],
    ),
    (Subject.ENGLISH, 2): LearningContent(
        subject=Subject.ENGLISH,
        grade=2,
        title="すきなものとあそび",
        description="好き嫌いや遊びに関する表現",
        sample_topics=["I like / I don't like", "Let's play", "Fruits and Animals"],
    ),
    (Subject.ENGLISH, 3): LearningContent(
        subject=Subject.ENGLISH,
        grade=3,
        title="じぶんのことをつたえる",
        description="自己紹介・家族・曜日の表現",
        sample_topics=["My name is", "Days of the week", "My family"],
    ),
    (Subject.ENGLISH, 4): LearningContent(
        subject=Subject.ENGLISH,
        grade=4,
        title="まちとじかん",
        description="時刻・場所・道案内の表現",
        sample_topics=["What time is it?", "Turn left / right", "Places in town"],
    ),
    (Subject.ENGLISH, 5): LearningContent(
        subject=Subject.ENGLISH,
        grade=5,
        title="することとできること",
        description="can / want to を使った表現",
        sample_topics=["I can swim", "I want to be", "Daily routine"],
    ),
    (Subject.ENGLISH, 6): LearningContent(
        subject=Subject.ENGLISH,
        grade=6,
        title="せかいとのつながり",
        description="過去形・未来形・世界の文化",
        sample_topics=["Past tense", "Future plans", "World cultures"],
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
