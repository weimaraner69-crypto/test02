"""
src/gemini/service.py の Gemini API 連携サービステスト
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from src.core.exceptions import ValidationError
from src.gemini.service import GeminiService

# テスト用の正常レスポンス JSON
_VALID_RESPONSE = {
    "question": {"text": "テスト問題", "type": "choice", "options": ["A", "B", "C"]},
    "answer": {"correct": "A", "explanation": "解説"},
    "hints": {"level1": "H1", "level2": "H2", "level3": "H3"},
    "curriculum_reference": {"chapter": "第1章", "section": "1節", "page": 1},
}


def _make_mock_response(text: str, candidates=None):
    """モックレスポンスを生成するヘルパー。"""
    mock_response = MagicMock()
    mock_response.text = text
    mock_response.candidates = candidates if candidates is not None else []
    return mock_response


def test_generate_question_with_mock_genai():
    """正常系: モック genai でJSONレスポンスが正しくパースされることを確認する。"""
    mock_response = _make_mock_response(json.dumps(_VALID_RESPONSE))

    with (
        patch("src.gemini.service.genai") as mock_genai,
        patch("src.gemini.service._GENAI_AVAILABLE", True),
    ):
        mock_genai.GenerativeModel.return_value.generate_content.return_value = mock_response
        mock_genai.configure = MagicMock()
        service = GeminiService(api_key="test-key")
        result = service.generate_question("PDFコンテキスト", "算数", 3)

    assert result is not None
    assert result["question"]["type"] == "choice"
    assert result["answer"]["correct"] == "A"
    assert "hints" in result
    assert "curriculum_reference" in result


def test_generate_question_safety_filter():
    """安全フィルタ違反時に ValidationError が送出されることを確認する（C-002 準拠）。"""
    mock_candidate = MagicMock()
    mock_candidate.finish_reason = "SAFETY"
    mock_response = _make_mock_response("", candidates=[mock_candidate])

    with (
        patch("src.gemini.service.genai") as mock_genai,
        patch("src.gemini.service._GENAI_AVAILABLE", True),
    ):
        mock_genai.GenerativeModel.return_value.generate_content.return_value = mock_response
        mock_genai.configure = MagicMock()
        service = GeminiService(api_key="test-key")
        with pytest.raises(ValidationError, match="安全フィルタ"):
            service.generate_question("コンテキスト", "国語", 1)


def test_generate_question_json_parse_error():
    """JSONパース失敗時に ValidationError が送出されることを確認する。"""
    mock_response = _make_mock_response("not a json")

    with (
        patch("src.gemini.service.genai") as mock_genai,
        patch("src.gemini.service._GENAI_AVAILABLE", True),
    ):
        mock_genai.GenerativeModel.return_value.generate_content.return_value = mock_response
        mock_genai.configure = MagicMock()
        service = GeminiService(api_key="test-key")
        with pytest.raises(ValidationError, match="JSON パースに失敗"):
            service.generate_question("コンテキスト", "理科", 4)


def test_generate_question_retry_on_runtime_error():
    """RuntimeError 発生時に指数バックオフでリトライされることを確認する。"""
    with (
        patch("src.gemini.service.genai") as mock_genai,
        patch("src.gemini.service._GENAI_AVAILABLE", True),
        patch("src.gemini.service.time.sleep") as mock_sleep,
    ):
        mock_genai.configure = MagicMock()
        mock_genai.GenerativeModel.return_value.generate_content.side_effect = RuntimeError(
            "API 一時エラー"
        )
        service = GeminiService(api_key="test-key")
        with pytest.raises(RuntimeError, match="API 一時エラー"):
            service.generate_question("コンテキスト", "社会", 5)

    # リトライ間隔（1s, 2s, 4s）分だけ sleep が呼ばれることを確認する
    assert mock_sleep.call_count == 3


def test_generate_question_validation_error_no_retry():
    """ValidationError 発生時はリトライなしで即座に再送出されることを確認する。"""
    with (
        patch("src.gemini.service.genai") as mock_genai,
        patch("src.gemini.service._GENAI_AVAILABLE", True),
        patch("src.gemini.service.time.sleep") as mock_sleep,
    ):
        mock_genai.configure = MagicMock()
        mock_genai.GenerativeModel.return_value.generate_content.side_effect = ValidationError(
            "バリデーションエラー"
        )
        service = GeminiService(api_key="test-key")
        with pytest.raises(ValidationError, match="バリデーションエラー"):
            service.generate_question("コンテキスト", "英語", 6)

    # sleep は一切呼ばれないことを確認する
    mock_sleep.assert_not_called()
