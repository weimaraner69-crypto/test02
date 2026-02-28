"""
src/auth/service.py の認証サービス雛形テスト
"""
import pytest
from src.auth.service import AuthService

def test_sign_in_with_google():
    auth = AuthService()
    user = auth.sign_in_with_google()
    assert user is not None
    assert "uid" in user
    assert user["isNewUser"] is True

def test_setup_profile():
    auth = AuthService()
    result = auth.setup_profile("sample_uid", {"role": "student"})
    assert result is True

def test_sign_out():
    auth = AuthService()
    result = auth.sign_out()
    assert result is True
