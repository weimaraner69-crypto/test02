"""observability/tracing モジュールのテスト。

OTel SDK 未インストール環境（_HAS_OTEL = False）でも全テストが通過することを確認する。
"""

from __future__ import annotations

import pytest


def test_init_tracer_no_exception() -> None:
    """init_tracer() が OTel 未インストール時に例外を出さないことを確認する。"""
    from src.observability.tracing import init_tracer

    # OTel 未インストールでも例外が発生しないこと（no-op 動作）
    init_tracer()
    init_tracer(service_name="test-service")
    init_tracer(service_name="test-service", enable_console_export=False)


def test_get_tracer_returns_none_without_otel() -> None:
    """get_tracer() が OTel 未インストール時に None を返すことを確認する。"""
    from src.observability.tracing import _HAS_OTEL, get_tracer

    if not _HAS_OTEL:
        assert get_tracer() is None


def test_trace_agent_operation_passthrough() -> None:
    # OTel 未インストール時にパススルー動作することを確認する
    """trace_agent_operation パススルー動作テスト。"""
    from src.observability.tracing import trace_agent_operation

    @trace_agent_operation("test.operation")
    def sample_func(x: int, y: int) -> int:
        return x + y

    result = sample_func(2, 3)
    assert result == 5


def test_trace_agent_operation_passthrough_no_name() -> None:
    """trace_agent_operation をデコレータ名なしで使用した場合もパススルーすることを確認する。"""
    from src.observability.tracing import trace_agent_operation

    @trace_agent_operation()
    def add(a: int, b: int) -> int:
        return a + b

    assert add(10, 20) == 30


def test_trace_llm_call_passthrough() -> None:
    """trace_llm_call デコレータが OTel 未インストール時にパススルー動作することを確認する。"""
    from src.observability.tracing import trace_llm_call

    @trace_llm_call(model_name="gemini")
    def fake_llm(prompt: str) -> str:
        return f"response:{prompt}"

    result = fake_llm("hello")
    assert result == "response:hello"


def test_trace_llm_call_passthrough_no_model() -> None:
    """trace_llm_call をモデル名なしで使用した場合もパススルーすることを確認する。"""
    from src.observability.tracing import trace_llm_call

    @trace_llm_call()
    def fake_llm_no_model(value: int) -> int:
        return value * 2

    assert fake_llm_no_model(5) == 10


def test_trace_tool_execution_passthrough() -> None:
    # OTel 未インストール時にパススルー動作することを確認する
    """trace_tool_execution パススルー動作テスト。"""
    from src.observability.tracing import trace_tool_execution

    @trace_tool_execution("test.tool")
    def sample_tool(data: list[int]) -> int:
        return sum(data)

    assert sample_tool([1, 2, 3]) == 6


def test_trace_tool_execution_passthrough_no_name() -> None:
    """trace_tool_execution をツール名なしで使用した場合もパススルーすることを確認する。"""
    from src.observability.tracing import trace_tool_execution

    @trace_tool_execution()
    def another_tool() -> str:
        return "ok"

    assert another_tool() == "ok"


def test_trace_llm_call_preserves_exception() -> None:
    """trace_llm_call デコレータが例外を透過的に再送出することを確認する。"""
    from src.observability.tracing import trace_llm_call

    @trace_llm_call(model_name="gemini")
    def failing_llm() -> str:
        raise ValueError("LLM エラー")

    with pytest.raises(ValueError, match="LLM エラー"):
        failing_llm()


# ---------------------------------------------------------------------------
# 統合テスト: 各サービスへのデコレータ適用確認（OTel 未インストール時のパススルー）
# ---------------------------------------------------------------------------


def test_auth_service_sign_in_works_with_decorator() -> None:
    """AuthService.sign_in_with_google が @trace_agent_operation 適用後も正常動作するか確認。"""
    from src.auth.service import AuthService

    svc = AuthService(mode="mock")
    result = svc.sign_in_with_google()
    assert result is not None
    assert result["uid"] == "mock_uid_001"


def test_gemini_service_generate_question_works_with_decorator() -> None:
    """GeminiService.generate_question が @trace_llm_call 適用後も正常動作することを確認する。"""
    from unittest.mock import patch

    from src.gemini.service import GeminiService

    svc = GeminiService(api_key="test-key")
    mock_response = {
        "question": {"text": "テスト問題"},
        "answer": "テスト答え",
        "hints": [],
        "curriculum_reference": "テスト",
    }
    with patch.object(svc, "generate_question", return_value=mock_response):
        result = svc.generate_question("context", "topic", 3)
    assert result is not None
    assert result["question"]["text"] == "テスト問題"


def test_learning_service_generate_question_works_with_decorator() -> None:
    """LearningService.generate_question が @trace_llm_call 適用後も正常動作することを確認する。"""
    from unittest.mock import MagicMock, patch

    from src.domain.learning import Subject
    from src.learning.service import LearningService
    from src.user.profile import UserProfileService

    profile = UserProfileService(":memory:")
    gemini = MagicMock()
    svc = LearningService(profile_service=profile, gemini_service=gemini)

    mock_response = {
        "question": {"text": "算数問題"},
        "answer": "42",
        "hints": [],
        "curriculum_reference": "小学1年生算数",
    }
    gemini.generate_question.return_value = mock_response

    with patch.object(profile, "set_learning_progress", return_value=True):
        result = svc.generate_question("uid_001", 1, Subject.MATH, "足し算")
    assert result["question"]["text"] == "算数問題"
    profile.close()
