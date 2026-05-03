"""
src/auth/service.py の認証サービステスト
AuthMode（MOCK/GOOGLE）切り替えと基本動作を検証する。
"""

from __future__ import annotations

import pytest
from src.auth.service import AuthService


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
