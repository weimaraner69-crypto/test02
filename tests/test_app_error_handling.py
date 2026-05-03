"""app.py のエラーハンドリングテスト。"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from unittest.mock import patch

if TYPE_CHECKING:
    import pytest

from src.app import _setup_logging, main
from src.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DomainError,
    ValidationError,
)


def test_main_none_user_raises_auth_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """sign_in_with_google が None を返した場合、AuthenticationError が送出される。"""
    monkeypatch.setenv("DATABASE_PATH", ":memory:")
    with patch("src.app.AuthService") as mock_auth:
        mock_auth.return_value.sign_in_with_google.return_value = None
        import pytest as _pytest

        with _pytest.raises(AuthenticationError):
            main()


def test_main_auth_error_is_reraised(monkeypatch: pytest.MonkeyPatch) -> None:
    """AuthenticationError が発生した場合、ログ出力して例外を再送出する。"""
    monkeypatch.setenv("DATABASE_PATH", ":memory:")
    with patch("src.app.AuthService") as mock_auth:
        mock_auth.return_value.sign_in_with_google.side_effect = AuthenticationError("認証失敗")
        import pytest as _pytest

        with _pytest.raises(AuthenticationError):
            main()


def test_main_authorization_error_is_reraised(monkeypatch: pytest.MonkeyPatch) -> None:
    """AuthorizationError は再送出される。"""
    monkeypatch.setenv("DATABASE_PATH", ":memory:")
    with patch("src.app.AuthService") as mock_auth:
        mock_auth.return_value.sign_in_with_google.side_effect = AuthorizationError("権限なし")
        import pytest as _pytest

        with _pytest.raises(AuthorizationError):
            main()


def test_main_validation_error_is_reraised(monkeypatch: pytest.MonkeyPatch) -> None:
    """ValidationError は再送出される。"""
    monkeypatch.setenv("DATABASE_PATH", ":memory:")
    with patch("src.app.AuthService") as mock_auth:
        mock_auth.return_value.sign_in_with_google.side_effect = ValidationError("入力値不正")
        import pytest as _pytest

        with _pytest.raises(ValidationError):
            main()


def test_main_domain_error_is_reraised(monkeypatch: pytest.MonkeyPatch) -> None:
    """DomainError（基底クラス）は再送出される。"""
    monkeypatch.setenv("DATABASE_PATH", ":memory:")
    with patch("src.app.AuthService") as mock_auth:
        mock_auth.return_value.sign_in_with_google.side_effect = DomainError("汎用エラー")
        import pytest as _pytest

        with _pytest.raises(DomainError):
            main()


def test_main_success_no_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    """正常系: 例外なく動作する。"""
    monkeypatch.setenv("DATABASE_PATH", ":memory:")
    main()


def test_main_error_is_logged(caplog: pytest.LogCaptureFixture) -> None:
    """AuthenticationError 発生時にエラーログが出力される。"""
    import pytest as _pytest

    caplog.clear()
    with patch("src.app.AuthService") as mock_auth:
        mock_auth.return_value.sign_in_with_google.side_effect = AuthenticationError("ログテスト")
        with _pytest.raises(AuthenticationError):
            main()
    assert any("認証エラー" in record.message for record in caplog.records)


# ---- N-005 拡充テスト ----


def test_main_raises_authorization_error_for_no_permission_role(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # parent ロールは VIEW_KNOWLEDGE 権限を持たないため AuthorizationError が送出される
    import pytest as _pytest

    monkeypatch.setenv("DATABASE_PATH", ":memory:")
    # parent ロールを持つダミーユーザーを返すようにモックする
    dummy_user = {"uid": "u1", "displayName": "Test Parent", "role": "parent"}
    with patch("src.app.AuthService") as mock_auth:
        mock_auth.return_value.sign_in_with_google.return_value = dummy_user
        with _pytest.raises(AuthorizationError):
            main()


def test_main_raises_authorization_error_when_profile_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """プロファイル未取得時はフェイルクローズする。"""
    import pytest as _pytest

    monkeypatch.setenv("DATABASE_PATH", ":memory:")
    with patch("src.app.UserProfileService") as mock_profile_service:
        mock_profile_service.return_value.get_profile.return_value = None
        with _pytest.raises(AuthorizationError):
            main()


# ---- N-014: _setup_logging 専用テスト ----


def test_setup_logging_valid_level() -> None:
    """有効なレベル文字列を渡すと basicConfig が正しいレベルで呼ばれる。"""
    with patch("logging.basicConfig") as mock_basicconfig:
        _setup_logging("DEBUG")
    mock_basicconfig.assert_called_once()
    _, kwargs = mock_basicconfig.call_args
    assert kwargs["level"] == logging.DEBUG


def test_setup_logging_invalid_level_falls_back_to_info() -> None:
    """無効なレベル文字列を渡すと basicConfig が INFO で呼ばれる（フォールバック）。"""
    with patch("logging.basicConfig") as mock_basicconfig:
        _setup_logging("INVALID_LEVEL_XYZ")
    mock_basicconfig.assert_called_once()
    _, kwargs = mock_basicconfig.call_args
    assert kwargs["level"] == logging.INFO


def test_setup_logging_case_insensitive() -> None:
    """レベル文字列は大文字小文字を区別しない。"""
    with patch("logging.basicConfig") as mock_basicconfig:
        _setup_logging("warning")
    mock_basicconfig.assert_called_once()
    _, kwargs = mock_basicconfig.call_args
    assert kwargs["level"] == logging.WARNING
