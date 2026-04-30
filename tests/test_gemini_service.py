"""
src/gemini/service.py のGemini API連携サービス雛形テスト
"""

from src.gemini.service import GeminiService


def test_generate_question():
    gemini = GeminiService(api_key="dummy-key")
    result = gemini.generate_question("PDFコンテキスト", "算数", 3)
    assert result is not None
    assert "question" in result
    assert "answer" in result
    assert result["question"]["type"] == "choice"
    assert result["answer"]["correct"] == "A"
    assert "hints" in result
    assert "curriculum_reference" in result
