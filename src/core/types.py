"""
型定義（ドメインオブジェクト）
"""

from __future__ import annotations

from typing import TypedDict


class UserProfile(TypedDict):
    uid: str
    email: str
    displayName: str
    role: str
    stage: str | None
    grade: int | None
    managedBy: str | None
    birthYear: int | None


class Question(TypedDict):
    text: str
    type: str
    options: list[str]


class Answer(TypedDict):
    correct: str
    explanation: str


class CurriculumReference(TypedDict):
    chapter: str
    section: str
    pages: list[int]
