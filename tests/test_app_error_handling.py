"""app.py のエラーハンドリングテスト。"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

if TYPE_CHECKING:
    import pytest

from src.app import main
from src.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DomainError,
    ValidationError,
)


def test_main_none_user_raises_auth_error() -> None:
    """sign_in_with_google が None を返した場合、AuthenticationError が送出される。"""
    with patch("src.app.AuthService") as mock_auth:
        mock_auth.return_value.sign_in_with_google.return_value = None
        import pytest as _pytest

        with _pytest.raises(AuthenticationError):
            main()


def test_main_auth_error_is_reraised() -> None:
    """AuthenticationError が発生した場合、ログ出力して例外を再送出する。"""
    with patch("src.app.AuthService") as mock_auth:
        mock_auth.return_value.sign_in_with_google.side_effect = AuthenticationError("認証失敗")
        import pytest as _pytest

        with _pytest.raises(AuthenticationError):
            main()


def test_main_authorization_error_is_reraised() -> None:
    """AuthorizationError は再送出される。"""
    with patch("src.app.AuthService") as mock_auth:
        mock_auth.return_value.sign_in_with_google.side_effect = AuthorizationError("権限なし")
        import pytest as _pytest

        with _pytest.raises(AuthorizationError):
            main()


def test_main_validation_error_is_reraised() -> None:
    """ValidationError は再送出される。"""
    with patch("src.app.AuthService") as mock_auth:
        mock_auth.return_value.sign_in_with_google.side_effect = ValidationError("入力値不正")
        import pytest as _pytest

        with _pytest.raises(ValidationError):
            main()


def test_main_domain_error_is_reraised() -> None:
    """DomainError（基底クラス）は再送出される。"""
    with patch("src.app.AuthService") as mock_auth:
        mock_auth.return_value.sign_in_with_google.side_effect = DomainError("汎用エラー")
        import pytest as _pytest

        with _pytest.raises(DomainError):
            main()


def test_main_success_no_exception() -> None:
    """正常系: 例外なく動作する。"""
    main()


def test_main_error_is_logged(caplog: pytest.LogCaptureFixture) -> None:
    """AuthenticationError 発生時にエラーログが出力される。"""
    import pytest as _pytest

    with patch("src.app.AuthService") as mock_auth:
        mock_auth.return_value.sign_in_with_google.side_effect = AuthenticationError("ログテスト")
        with _pytest.raises(AuthenticationError):
            main()
    assert any("認証エラー" in record.message for record in caplog.records)
