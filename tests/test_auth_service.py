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
    auth = AuthService(mode="google")
    with (
        patch.dict(
            os.environ,
            {"GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": ""},
        ),
        pytest.raises(ValueError),
    ):
        auth.sign_in_with_google()


def test_invalid_mode_raises_value_error() -> None:
    """不正なモード文字列を渡すと ValueError が送出される。"""
    with pytest.raises(ValueError):
        AuthService(mode="invalid_mode")


# ---- N-011 Google OAuth テスト ----


def test_google_mode_returns_credentials_cached(tmp_path: Path) -> None:
    """
    GOOGLE モードで認証成功時に _token_cache が設定されることを確認する。
    """
    import sys

    token_file = tmp_path / "token.json"

    mock_creds = MagicMock()
    mock_creds.valid = True
    mock_creds.to_json.return_value = json.dumps({"token": "dummy"})

    mock_user_info = {
        "id": "google_uid_cache",
        "email": "cache@example.com",
        "name": "キャッシュ確認",
    }
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
        user = auth.sign_in_with_google()

    assert user is not None
    assert user["uid"] == "google_uid_cache"
    assert auth._token_cache is mock_creds


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


def test_google_mode_import_error_raises_runtime_error() -> None:
    """google_auth_oauthlib が未インストールの場合に RuntimeError を送出する。"""
    import builtins

    original_import = builtins.__import__

    with (
        patch.dict(
            os.environ,
            {"GOOGLE_CLIENT_ID": "dummy_id", "GOOGLE_CLIENT_SECRET": "dummy_secret"},
        ),
        patch("builtins.__import__") as mock_import,
    ):

        def _import_side_effect(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "google_auth_oauthlib.flow":
                raise ImportError("missing google_auth_oauthlib")
            return original_import(name, globals, locals, fromlist, level)

        mock_import.side_effect = _import_side_effect
        auth = AuthService(mode="google")
        with pytest.raises(RuntimeError, match="未インストール"):
            auth.sign_in_with_google()


def test_google_mode_invalid_token_file_falls_back_to_browser_auth(tmp_path: Path) -> None:
    """トークン読込失敗時は警告後に再認証へフォールバックする。"""
    import sys

    token_file = tmp_path / "token.json"
    token_file.write_text("invalid", encoding="utf-8")

    mock_creds = MagicMock()
    mock_creds.valid = True
    mock_creds.to_json.return_value = json.dumps({"token": "dummy"})

    mock_user_info = {"id": "google_uid_002", "email": "user@example.com", "name": "再認証"}
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
        patch(
            "google.oauth2.credentials.Credentials.from_authorized_user_file",
            side_effect=Exception("broken token"),
        ),
    ):
        auth = AuthService(mode="google", token_path=str(token_file))
        result = auth.sign_in_with_google()

    mock_flow.run_local_server.assert_called_once()
    assert result is not None
    assert result["uid"] == "google_uid_002"


def test_google_mode_run_local_server_oserror_raises_runtime_error() -> None:
    """ローカルサーバー起動失敗（OSError）時に RuntimeError を送出する。"""
    mock_flow = MagicMock()
    mock_flow.run_local_server.side_effect = OSError("port in use")

    with (
        patch.dict(
            os.environ,
            {"GOOGLE_CLIENT_ID": "dummy_id", "GOOGLE_CLIENT_SECRET": "dummy_secret"},
        ),
        patch(
            "google_auth_oauthlib.flow.InstalledAppFlow.from_client_config", return_value=mock_flow
        ),
    ):
        auth = AuthService(mode="google", token_path="/tmp/not-used-token.json")
        with pytest.raises(RuntimeError, match="ローカル web サーバー起動失敗"):
            auth.sign_in_with_google()


def test_google_mode_token_save_failure_continues(tmp_path: Path) -> None:
    """トークン保存失敗時も処理継続し、ユーザー情報を返す。"""
    import sys

    token_file = tmp_path / "token.json"
    mock_creds = MagicMock()
    mock_creds.valid = True
    mock_creds.to_json.return_value = json.dumps({"token": "dummy"})

    mock_user_info = {
        "id": "google_uid_003",
        "email": "user@example.com",
        "name": "保存失敗継続",
    }
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
        patch("pathlib.Path.write_text", side_effect=OSError("disk full")),
    ):
        auth = AuthService(mode="google", token_path=str(token_file))
        result = auth.sign_in_with_google()

    assert result is not None
    assert result["uid"] == "google_uid_003"


def test_google_mode_user_info_fetch_failure_raises_runtime_error(tmp_path: Path) -> None:
    """googleapiclient でユーザー情報取得失敗時に RuntimeError を送出する。"""
    import sys

    token_file = tmp_path / "token.json"
    mock_creds = MagicMock()
    mock_creds.valid = True
    mock_creds.to_json.return_value = json.dumps({"token": "dummy"})

    mock_googleapiclient = MagicMock()
    mock_googleapiclient.discovery.build.side_effect = Exception("userinfo failed")

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
        with pytest.raises(RuntimeError, match="ユーザー情報取得失敗"):
            auth.sign_in_with_google()
