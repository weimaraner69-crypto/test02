"""pytest 設定。src/ を sys.path に追加してパッケージを解決する。"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent / "src"))

# CI 環境では google-generativeai が未インストールのため、
# 全テストでデフォルトモックを適用する。
# 個別テストで patch(...) を使う場合はそちらが優先される。
_DEFAULT_GENAI_RESPONSE = {
    "question": {
        "text": "算数に関する問題（3年）",
        "type": "choice",
        "options": ["A", "B", "C"],
    },
    "answer": {"correct": "A", "explanation": "Aが正解です。"},
    "hints": {"level1": "ヒント1", "level2": "ヒント2", "level3": "ヒント3"},
    "curriculum_reference": {"chapter": "第1章", "section": "1節", "page": 10},
}


@pytest.fixture(autouse=True)
def _mock_genai_globally(monkeypatch: pytest.MonkeyPatch) -> None:
    """CI で google-generativeai なしに全テストが通るよう genai をモックする。"""
    mock_response = MagicMock()
    mock_response.text = json.dumps(_DEFAULT_GENAI_RESPONSE)
    mock_response.candidates = []

    mock_genai = MagicMock()
    mock_genai.GenerativeModel.return_value.generate_content.return_value = mock_response

    monkeypatch.setattr("src.gemini.service._GENAI_AVAILABLE", True)
    monkeypatch.setattr("src.gemini.service.genai", mock_genai)
