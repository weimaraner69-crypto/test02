"""
Gemini API連携サービス雛形
"""

from __future__ import annotations

from typing import Dict


class GeminiService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # 実際はGoogle Generative AI SDK初期化

    def generate_question(self, context: str, topic: str, grade: int) -> Dict | None:
        """
        Gemini APIで問題生成（雛形）
        """
        # 実際はAPI呼び出し
        return {
            "question": {
                "text": f"{topic}に関する問題（{grade}年）",
                "type": "choice",
                "options": ["A", "B", "C"],
            },
            "answer": {"correct": "A", "explanation": "Aが正解です。"},
            "hints": {"level1": "ヒント1", "level2": "ヒント2", "level3": "ヒント3"},
            "curriculum_reference": {"chapter": "第1章", "section": "1節", "page": 10},
        }
