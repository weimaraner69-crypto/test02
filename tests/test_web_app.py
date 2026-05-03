"""
web/app.py の Flask アプリテスト
Flask テストクライアントを用いて主要エンドポイントを検証する。
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from web.app import app as flask_app


@pytest.fixture()
def client():
    """Flask テストクライアントを返すフィクスチャ。"""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def test_health_endpoint(client) -> None:
    """/health が 200 を返すことを確認する。"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"


def test_index_with_mock_auth(client) -> None:
    """/index が MOCK 認証で 200 を返すことを確認する。"""
    with patch.dict(os.environ, {"AUTH_MODE": "mock", "DATABASE_PATH": ":memory:"}):
        response = client.get("/")
    assert response.status_code == 200
    # Jinja2 テンプレートで displayName が展開されていること
    assert b"MiraStudy Web" in response.data
    assert b"&#34;" not in response.data  # HTML エスケープ過剰でないこと


def test_index_returns_500_on_auth_failure(client) -> None:
    """sign_in_with_google が None を返した場合に 500 を返すことを確認する。"""
    with (
        patch("web.app.AuthService") as mock_auth_cls,
        patch.dict(os.environ, {"AUTH_MODE": "mock", "DATABASE_PATH": ":memory:"}),
    ):
        mock_auth = mock_auth_cls.return_value
        mock_auth.sign_in_with_google.return_value = None
        response = client.get("/")
    assert response.status_code == 500
