"""
web/app.py の Flask アプリテスト
Flask テストクライアントを用いて主要エンドポイントを検証する。
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from src.core.exceptions import RateLimitError, ValidationError

# create_app のモジュール初期化用。テスト専用のダミー値を設定する。
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from web.app import app as flask_app
from web.app import create_app


@pytest.fixture()
def client():
    with patch.dict(
        os.environ,
        {
            "AUTH_MODE": "mock",
            "DATABASE_PATH": ":memory:",
            "SECRET_KEY": "test-secret-key",
        },
    ):
        # 元の設定を保存
        original_testing = flask_app.config.get("TESTING", False)
        original_secure = flask_app.config.get("SESSION_COOKIE_SECURE", True)
        try:
            flask_app.config["TESTING"] = True
            # テストクライアントは HTTP 扱いのため Secure Cookie は無効化して検証する
            flask_app.config["SESSION_COOKIE_SECURE"] = False
            with flask_app.test_client() as client:
                yield client
        finally:
            # 設定をリセットして副作用を防ぐ
            flask_app.config["TESTING"] = original_testing
            flask_app.config["SESSION_COOKIE_SECURE"] = original_secure


def test_health_endpoint(client) -> None:
    """/health が 200 を返すことを確認する。"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"


def test_startup_raises_when_secret_key_missing() -> None:
    """SECRET_KEY 未設定時は起動エラーになることを確認する。"""
    with (
        patch.dict(os.environ, {"SECRET_KEY": ""}),
        pytest.raises(RuntimeError, match="SECRET_KEY"),
    ):
        create_app()


def test_unauthenticated_index_redirects_to_login(client) -> None:
    """未ログインで / にアクセスした場合は /login へリダイレクトする。"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_login_page_returns_form(client) -> None:
    """GET /login でログイン画面を表示する。"""
    response = client.get("/login", follow_redirects=False)
    assert response.status_code == 200
    assert "<h1>" in response.data.decode("utf-8")


def test_login_creates_session_and_index_returns_200(client) -> None:
    """POST /login でログイン後はセッションが維持され、/ で 200 を返す。"""
    with patch("web.app.LearningService") as mock_learning_cls:
        mock_learning_cls.return_value.generate_question.return_value = {
            "question": {"text": "dummy"}
        }
        login_response = client.post("/login", follow_redirects=False)
        assert login_response.status_code == 302
        assert "/" in login_response.headers["Location"]

        with client.session_transaction() as sess:
            assert "uid" in sess

        response = client.get("/", follow_redirects=False)
        assert response.status_code == 200
        assert b"MiraStudy Web" in response.data


def test_index_returns_429_on_rate_limit_error(client) -> None:
    """C-003 の RateLimitError 発生時は 429 を返す。"""
    client.post("/login", follow_redirects=False)
    with patch("web.app.LearningService") as mock_learning_cls:
        mock_learning_cls.return_value.generate_question.side_effect = RateLimitError(
            "rate limit",
            reason_code="C003_rate_limit_exceeded",
        )
        response = client.get("/", follow_redirects=False)
    assert response.status_code == 429
    assert "アクセス制限" in response.data.decode("utf-8")


def test_index_returns_429_on_session_timeout_validation_error(client) -> None:
    """C-004 の ValidationError(reason_code) 発生時は 429 を返す。"""
    client.post("/login", follow_redirects=False)
    with patch("web.app.LearningService") as mock_learning_cls:
        mock_learning_cls.return_value.generate_question.side_effect = ValidationError(
            "session timeout",
            reason_code="C004_session_timeout",
        )
        response = client.get("/", follow_redirects=False)
    assert response.status_code == 429
    assert "休憩のお願い" in response.data.decode("utf-8")


def test_logout_clears_session_and_redirects_to_login(client) -> None:
    """ログアウトでセッションを破棄し、再度 / は /login へリダイレクトする。"""
    client.post("/login", follow_redirects=False)
    with client.session_transaction() as sess:
        assert "uid" in sess

    logout_response = client.post("/logout", follow_redirects=False)
    assert logout_response.status_code == 303
    assert "/login" in logout_response.headers["Location"]

    with client.session_transaction() as sess:
        assert "uid" not in sess

    response_after_logout = client.get("/", follow_redirects=False)
    assert response_after_logout.status_code == 302
    assert "/login" in response_after_logout.headers["Location"]


def test_session_cookie_security_flags_enabled() -> None:
    """セッション Cookie のセキュリティ設定が有効であることを確認する。"""
    assert flask_app.config["SESSION_COOKIE_HTTPONLY"] is True
    # テスト fixture で False に上書きされる可能性があるため create_app の既定値を検証する
    with patch.dict(os.environ, {"SECRET_KEY": "test-secret-key"}):
        tmp_app = create_app()
    assert tmp_app.config["SESSION_COOKIE_SECURE"] is True
    assert tmp_app.config["SESSION_COOKIE_SAMESITE"] == "Lax"


def test_login_returns_500_on_auth_failure(client) -> None:
    """POST /login で sign_in_with_google が None の場合は 500 を返す。"""
    with patch("web.app.AuthService") as mock_auth_cls:
        mock_auth = mock_auth_cls.return_value
        mock_auth.sign_in_with_google.return_value = None
        response = client.post("/login")
    assert response.status_code == 500
