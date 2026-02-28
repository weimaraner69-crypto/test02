"""
型定義（ドメインオブジェクト）
"""
from typing import TypedDict, List, Optional

class UserProfile(TypedDict):
    uid: str
    email: str
    displayName: str
    role: str
    stage: Optional[str]
    grade: Optional[int]
    managedBy: Optional[str]
    birthYear: Optional[int]

class Question(TypedDict):
    text: str
    type: str
    options: List[str]

class Answer(TypedDict):
    correct: str
    explanation: str

class CurriculumReference(TypedDict):
    chapter: str
    section: str
    pages: List[int]
