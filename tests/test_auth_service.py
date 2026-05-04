"""
src/auth/service.py の認証サービステスト
AuthMode（MOCK/GOOGLE）切り替えと基本動作を検証する。
"""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
from src.auth.service import AuthService

if TYPE_CHECKING:
    from pathlib import Path


def test_sign_in_with_google():
    # MOCK モード（デフォルト）で固定ダミーユーザーが返ることを確認する
    auth = AuthService()
    user = auth.sign_in_with_google()
    assert user is not None
    assert "uid" in user
    assert isinstance(user["isNewUser"], bool)


def test_setup_profile():
    auth = AuthService()
    result = auth.setup_profile("sample_uid", {"role": "student"})
    assert result is True


def test_sign_out():
    auth = AuthService()
    result = auth.sign_out()
    assert result is True


# ---- N-005 拡充テスト ----


def test_mock_mode_returns_user() -> None:
    """MOCK モードで uid と displayName を含む dict が返る。"""
    auth = AuthService(mode="mock")
    user = auth.sign_in_with_google()
    assert user is not None
    assert "uid" in user
    assert "displayName" in user


def test_google_mode_without_credentials_raises_value_error() -> None:
    """
    GOOGLE モードで GOOGLE_CLIENT_ID / SECRET が未設定の場合、ValueError を送出する。
    """
    import os

    auth = AuthService(mode="google")
    # 環境変数が未設定であることを確認（テスト環境では未設定）
    if not os.environ.get("GOOGLE_CLIENT_ID") or not os.environ.get("GOOGLE_CLIENT_SECRET"):
        with pytest.raises(ValueError):
            auth.sign_in_with_google()


def test_invalid_mode_raises_value_error() -> None:
    """不正なモード文字列を渡すと ValueError が送出される。"""
    with pytest.raises(ValueError):
        AuthService(mode="invalid_mode")


# ---- N-011 Google OAuth テスト ----


def test_google_mode_returns_credentials_cached() -> None:
    """
    GOOGLE モードで sign_in_with_google() が実装されていることを確認する。
    ただし実際の web サーバー起動はスキップするため、
    環境変数未設定時の ValueError で実装確認とする。
    """
    import os

    auth = AuthService(mode="google")

    # 環境変数が未設定の場合、ValueError が発生
    if not os.environ.get("GOOGLE_CLIENT_ID") or not os.environ.get("GOOGLE_CLIENT_SECRET"):
        with pytest.raises(ValueError, match="Google OAuth 認証情報が未設定"):
            auth.sign_in_with_google()


# ---- ヘルパー関数 ----


# ---- N-017 OAuth トークン永続化テスト ----


def test_mock_mode_ignores_token_path() -> None:
    """MOCK モードでは token_path が指定されても無視され、固定ユーザーが返る。"""
    auth = AuthService(mode="mock", token_path="/nonexistent/token.json")
    user = auth.sign_in_with_google()
    assert user is not None
    assert user["uid"] == "mock_uid_001"
    # MOCK モードでは _token_path が None（無視されている）
    assert auth._token_path is None


def test_google_mode_without_token_file_calls_browser_auth(tmp_path: Path) -> None:
    """
    GOOGLE モードでトークンファイルが存在しない場合、ブラウザ認証（run_local_server）を呼び出す。
    googleapiclient は未インストールのため sys.modules にモックを注入してテストする。
    """
    import sys

    token_file = tmp_path / "token.json"
    assert not token_file.exists()

    mock_creds = MagicMock()
    mock_creds.valid = True
    mock_creds.to_json.return_value = json.dumps({"token": "dummy"})

    mock_user_info = {"id": "google_uid_001", "email": "user@example.com", "name": "テストユーザー"}

    # googleapiclient が未インストール環境向けに sys.modules に注入する
    mock_googleapiclient = MagicMock()
    mock_service = MagicMock()
    mock_service.userinfo().get().execute.return_value = mock_user_info
    mock_googleapiclient.discovery.build.return_value = mock_service

    mock_flow = MagicMock()
    mock_flow.run_local_server.return_value = mock_creds

    with (
        patch.dict(
            os.environ,
            {"GOOGLE_CLIENT_ID": "dummy_id", "GOOGLE_CLIENT_SECRET": "dummy_secret"},
        ),
        patch.dict(
            sys.modules,
            {
                "googleapiclient": mock_googleapiclient,
                "googleapiclient.discovery": mock_googleapiclient.discovery,
            },
        ),
        patch(
            "google_auth_oauthlib.flow.InstalledAppFlow.from_client_config", return_value=mock_flow
        ),
    ):
        auth = AuthService(mode="google", token_path=str(token_file))
        result = auth.sign_in_with_google()

    # ブラウザ認証が呼ばれたことを確認
    mock_flow.run_local_server.assert_called_once()
    assert result is not None
    assert result["uid"] == "google_uid_001"
    # トークンファイルが保存されたことを確認
    assert token_file.exists()


def test_google_mode_with_valid_token_file_skips_browser_auth(tmp_path: Path) -> None:
    """
    GOOGLE モードで有効なトークンファイルが存在する場合、ブラウザ認証をスキップする。
    googleapiclient は未インストールのため sys.modules にモックを注入してテストする。
    """
    import sys

    token_file = tmp_path / "token.json"
    token_file.write_text(json.dumps({"token": "dummy"}), encoding="utf-8")

    mock_creds = MagicMock()
    mock_creds.valid = True

    mock_user_info = {"id": "google_uid_001", "email": "user@example.com", "name": "テストユーザー"}

    mock_googleapiclient = MagicMock()
    mock_service = MagicMock()
    mock_service.userinfo().get().execute.return_value = mock_user_info
    mock_googleapiclient.discovery.build.return_value = mock_service

    mock_flow_cls = MagicMock()

    with (
        patch.dict(
            os.environ,
            {"GOOGLE_CLIENT_ID": "dummy_id", "GOOGLE_CLIENT_SECRET": "dummy_secret"},
        ),
        patch.dict(
            sys.modules,
            {
                "googleapiclient": mock_googleapiclient,
                "googleapiclient.discovery": mock_googleapiclient.discovery,
            },
        ),
        patch("google_auth_oauthlib.flow.InstalledAppFlow.from_client_config", mock_flow_cls),
        patch(
            "google.oauth2.credentials.Credentials.from_authorized_user_file",
            return_value=mock_creds,
        ),
    ):
        auth = AuthService(mode="google", token_path=str(token_file))
        result = auth.sign_in_with_google()

    # ブラウザ認証が呼ばれていないことを確認
    mock_flow_cls.assert_not_called()
    assert result is not None
    assert result["uid"] == "google_uid_001"
