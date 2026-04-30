"""
src/permissions/roles.py の権限管理テスト
"""

from src.permissions.roles import Permission, has_permission


def test_admin_permissions():
    assert has_permission("admin", Permission.VIEW_KNOWLEDGE)
    assert has_permission("admin", Permission.MANAGE_FAMILY)
    assert has_permission("admin", Permission.MANAGE_API_KEY)
    # 存在しない権限はテストしない（ValueErrorになるため）


def test_student_permissions():
    assert has_permission("student", Permission.VIEW_KNOWLEDGE)
    assert has_permission("student", Permission.VIEW_OWN_HISTORY)
    assert not has_permission("student", Permission.MANAGE_FAMILY)
    assert not has_permission("student", Permission.MANAGE_API_KEY)
