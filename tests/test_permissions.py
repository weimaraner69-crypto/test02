"""権限管理システムのテスト。

FR: ロールに基づいた権限管理
"""

import pytest
from mirastudy.core.models import UserRole
from mirastudy.domain.permissions import Permission, has_permission


class TestAdminPermissions:
    """管理者（父）の権限テスト。"""

    def test_admin_can_view_knowledge(self) -> None:
        """管理者は知識ベースを閲覧できる。"""
        assert has_permission(UserRole.ADMIN, Permission.VIEW_KNOWLEDGE)

    def test_admin_can_manage_knowledge(self) -> None:
        """管理者は知識ベースを管理できる。"""
        assert has_permission(UserRole.ADMIN, Permission.MANAGE_KNOWLEDGE)

    def test_admin_can_view_all_history(self) -> None:
        """管理者は全員の学習履歴を閲覧できる。"""
        assert has_permission(UserRole.ADMIN, Permission.VIEW_ALL_HISTORY)

    def test_admin_can_manage_api_key(self) -> None:
        """管理者はAPIキーを管理できる。"""
        assert has_permission(UserRole.ADMIN, Permission.MANAGE_API_KEY)

    def test_admin_can_manage_family(self) -> None:
        """管理者は家族メンバーを管理できる。"""
        assert has_permission(UserRole.ADMIN, Permission.MANAGE_FAMILY)


class TestStudentPermissions:
    """学生（子）の権限テスト。"""

    def test_student_can_view_knowledge(self) -> None:
        """学生は知識ベースを閲覧できる。"""
        assert has_permission(UserRole.STUDENT, Permission.VIEW_KNOWLEDGE)

    def test_student_can_view_own_history(self) -> None:
        """学生は自分の学習履歴を閲覧できる。"""
        assert has_permission(UserRole.STUDENT, Permission.VIEW_OWN_HISTORY)

    def test_student_cannot_manage_knowledge(self) -> None:
        """学生は知識ベースを管理できない（権限不足）。"""
        assert not has_permission(UserRole.STUDENT, Permission.MANAGE_KNOWLEDGE)

    def test_student_cannot_view_all_history(self) -> None:
        """学生は他者の学習履歴を閲覧できない。"""
        assert not has_permission(UserRole.STUDENT, Permission.VIEW_ALL_HISTORY)

    def test_student_cannot_manage_api_key(self) -> None:
        """学生はAPIキーを管理できない。"""
        assert not has_permission(UserRole.STUDENT, Permission.MANAGE_API_KEY)

    def test_student_cannot_manage_family(self) -> None:
        """学生は家族メンバーを管理できない。"""
        assert not has_permission(UserRole.STUDENT, Permission.MANAGE_FAMILY)


class TestAllPermissions:
    """全権限の網羅テスト。"""

    @pytest.mark.parametrize("permission", list(Permission))
    def test_admin_has_all_permissions(self, permission: Permission) -> None:
        """管理者はすべての権限を持つ。"""
        assert has_permission(UserRole.ADMIN, permission)

    @pytest.mark.parametrize("permission", [
        Permission.VIEW_KNOWLEDGE,
        Permission.VIEW_OWN_HISTORY,
    ])
    def test_student_has_allowed_permissions(self, permission: Permission) -> None:
        """学生は閲覧系権限を持つ。"""
        assert has_permission(UserRole.STUDENT, permission)

    @pytest.mark.parametrize("permission", [
        Permission.MANAGE_KNOWLEDGE,
        Permission.VIEW_ALL_HISTORY,
        Permission.MANAGE_FAMILY,
        Permission.MANAGE_API_KEY,
    ])
    def test_student_lacks_privileged_permissions(self, permission: Permission) -> None:
        """学生は管理系権限を持たない。"""
        assert not has_permission(UserRole.STUDENT, permission)
