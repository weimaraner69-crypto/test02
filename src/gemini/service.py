"""
Gemini API連携サービス雛形
"""

from __future__ import annotations

import logging
import time

from src.core.exceptions import ValidationError
from src.observability.tracing import trace_llm_call

logger = logging.getLogger(__name__)

# リトライ間隔（秒）：指数バックオフ
RETRY_INTERVALS = (1, 2, 4)


class GeminiService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # 実際はGoogle Generative AI SDK初期化

    @trace_llm_call(model_name="gemini")
    def generate_question(self, context: str, topic: str, grade: int) -> dict | None:
        """Gemini APIで問題生成（リトライ付き）。
        RuntimeError / OSError / ConnectionError / TimeoutError 発生時は
        指数バックオフ（1s, 2s, 4s）で最大3回リトライする。
        ValidationError / ValueError は即座に再送出する（リトライしない）。
        """
        last_exc: Exception | None = None
        # 初回試行（wait=-1）＋最大3回リトライ
        for attempt, wait in enumerate((-1,) + RETRY_INTERVALS, start=1):
            if wait >= 0:
                logger.warning("Gemini API 再試行 %d回目（待機 %ds）: %s", attempt, wait, last_exc)
                time.sleep(wait)
            try:
                # 実際はAPI呼び出し（将来の実装でリトライが機能する）
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
            except (ValidationError, ValueError):
                # バリデーションエラーはリトライせず即座に再送出する
                raise
            except Exception as exc:
                last_exc = exc
        # すべてのリトライが失敗した場合は最後の例外を再送出する
        if last_exc is not None:
            raise last_exc
        return None
