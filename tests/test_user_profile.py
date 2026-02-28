"""
src/user/profile.py のユーザープロファイル管理テスト
"""
import pytest
from src.user.profile import UserProfileService

def test_set_and_get_profile():
    service = UserProfileService()
    uid = "user1"
    profile = {"displayName": "テストユーザー", "role": "student"}
    assert service.set_profile(uid, profile) is True
    result = service.get_profile(uid)
    assert result == profile

def test_list_family_members():
    service = UserProfileService()
    admin_uid = "admin1"
    admin_profile = {"displayName": "管理者", "role": "admin", "familyMembers": ["user1", "user2"]}
    service.set_profile(admin_uid, admin_profile)
    members = service.list_family_members(admin_uid)
    assert members == ["user1", "user2"]
