"""
サンプルドメインロジック
"""
from src.core.types import Question, Answer, CurriculumReference

def generate_sample_question() -> Question:
    """
    サンプル問題生成
    """
    return {
        "text": "2 + 2 = ?",
        "type": "choice",
        "options": ["3", "4", "5"]
    }

def get_sample_answer() -> Answer:
    """
    サンプル回答生成
    """
    return {
        "correct": "4",
        "explanation": "2 と 2 を足すと 4 になります。"
    }

def get_sample_curriculum_reference() -> CurriculumReference:
    """
    サンプル出典情報
    """
    return {
        "chapter": "第1章",
        "section": "計算の基礎",
        "pages": [10, 11]
    }
