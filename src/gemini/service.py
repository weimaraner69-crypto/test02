"""
Gemini API連携サービス
"""

from __future__ import annotations

import json
import logging
import time

from src.core.exceptions import ValidationError
from src.observability.tracing import trace_llm_call

logger = logging.getLogger(__name__)

# リトライ間隔（秒）：指数バックオフ
RETRY_INTERVALS = (1, 2, 4)

# google-generativeai SDK の条件付きインポート
try:
    import google.generativeai as genai

    _GENAI_AVAILABLE = True
except ImportError:
    genai = None  # type: ignore[assignment]
    _GENAI_AVAILABLE = False


class GeminiService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # SDK が利用可能な場合は API キーを設定する
        if _GENAI_AVAILABLE and genai is not None:
            genai.configure(api_key=api_key)

    @trace_llm_call(model_name="gemini")
    def generate_question(self, context: str, topic: str, grade: int) -> dict | None:
        """Gemini APIで問題生成（リトライ付き）。
        RuntimeError / OSError / ConnectionError / TimeoutError 発生時は
        指数バックオフ（1s, 2s, 4s）で最大3回リトライする。
        ValidationError / ValueError は即座に再送出する（リトライしない）。
        """
        # SDK 未インストール時は即座にエラーを送出する
        if not _GENAI_AVAILABLE or genai is None:
            raise RuntimeError("google-generativeai パッケージが未インストールです")

        last_exc: Exception | None = None
        # 初回試行（wait=-1）＋最大3回リトライ
        for attempt, wait in enumerate((-1,) + RETRY_INTERVALS, start=1):
            if wait >= 0:
                logger.warning("Gemini API 再試行 %d回目（待機 %ds）: %s", attempt, wait, last_exc)
                time.sleep(wait)
            try:
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = (
                    f"あなたは日本の小学校の教師です。{grade}年生の{topic}に関する選択式問題を1問作成してください。\n"
                    f"コンテキスト: {context}\n"
                    "以下のJSON形式で回答してください（他のテキストは含めないこと）:\n"
                    '{"question":{"text":"問題文","type":"choice","options":["A","B","C"]},'
                    '"answer":{"correct":"A","explanation":"解説"},'
                    '"hints":{"level1":"ヒント1","level2":"ヒント2","level3":"ヒント3"},'
                    '"curriculum_reference":{"chapter":"第1章","section":"1節","page":1}}'
                )
                response = model.generate_content(prompt)
                # 安全フィルタ違反チェック（C-002 準拠）
                if hasattr(response, "candidates") and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, "finish_reason") and str(candidate.finish_reason) in (
                        "FinishReason.SAFETY",
                        "SAFETY",
                    ):
                        raise ValidationError(
                            "Gemini API: コンテンツ安全フィルタにより生成を拒否しました（C-002）"
                        )
                # レスポンスからテキストを取得して JSON パースする
                text = response.text.strip()
                # Markdown コードブロックを除去する
                if text.startswith("```"):
                    lines = text.split("\n")
                    text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
                return json.loads(text)
            except json.JSONDecodeError as exc:
                # JSONDecodeError は ValueError のサブクラスなので先に捕捉してラップする
                raise ValidationError(f"Gemini API レスポンスの JSON パースに失敗: {exc}") from exc
            except (ValidationError, ValueError):
                # バリデーションエラーはリトライせず即座に再送出する
                raise
            except (RuntimeError, OSError, ConnectionError, TimeoutError) as exc:
                # 上記例外のみリトライ対象とし、それ以外は即座に再送出する
                last_exc = exc
            except Exception:
                raise
        # すべてのリトライが失敗した場合は最後の例外を再送出する
        if last_exc is not None:
            raise last_exc
        return None
