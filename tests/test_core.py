"""
src/core/exceptions.py と src/core/utils.py のユニットテスト
"""

import pytest

from core.exceptions import AuthenticationError, AuthorizationError, DomainError, ValidationError
from core.utils import safe_get

# ------------------------------------------------------------------
# exceptions.py
# ------------------------------------------------------------------


def test_domain_error_is_exception():
    err = DomainError("汎用エラー")
    assert isinstance(err, Exception)
    assert str(err) == "汎用エラー"


def test_authentication_error_is_domain_error():
    err = AuthenticationError("認証失敗")
    assert isinstance(err, DomainError)


def test_authorization_error_is_domain_error():
    err = AuthorizationError("権限不足")
    assert isinstance(err, DomainError)


def test_validation_error_is_domain_error():
    err = ValidationError("入力値不正")
    assert isinstance(err, DomainError)


def test_exceptions_are_raiseable():
    with pytest.raises(AuthenticationError):
        raise AuthenticationError("テスト")

    with pytest.raises(AuthorizationError):
        raise AuthorizationError("テスト")

    with pytest.raises(ValidationError):
        raise ValidationError("テスト")


# ------------------------------------------------------------------
# utils.py
# ------------------------------------------------------------------


def test_safe_get_existing_key():
    assert safe_get({"a": 1}, "a") == 1


def test_safe_get_missing_key_returns_default():
    assert safe_get({"a": 1}, "b") is None


def test_safe_get_missing_key_with_custom_default():
    assert safe_get({"a": 1}, "b", 99) == 99
