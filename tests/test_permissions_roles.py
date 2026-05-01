"""
src/permissions/roles.py の権限管理テスト
各ロールのパーミッション付与・拒否を検証する。
"""

from __future__ import annotations

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


# ---- N-005 拡充テスト ----


def test_parent_has_manage_family() -> None:
    """parent ロールは MANAGE_FAMILY 権限を持つ。"""
    assert has_permission("parent", Permission.MANAGE_FAMILY)


def test_parent_has_view_own_history() -> None:
    """parent ロールは VIEW_OWN_HISTORY 権限を持つ。"""
    assert has_permission("parent", Permission.VIEW_OWN_HISTORY)


def test_parent_cannot_view_knowledge() -> None:
    """parent ロールは VIEW_KNOWLEDGE 権限を持たない（知識共有フォルダ閲覧不可）。"""
    assert not has_permission("parent", Permission.VIEW_KNOWLEDGE)


def test_parent_cannot_manage_knowledge() -> None:
    """parent ロールは MANAGE_KNOWLEDGE 権限を持たない。"""
    assert not has_permission("parent", Permission.MANAGE_KNOWLEDGE)


def test_admin_has_all_permissions() -> None:
    """admin ロールはすべての Permission を持つ。"""
    for perm in Permission:
        assert has_permission("admin", perm), f"admin が {perm} を持っていない"


def test_student_only_view() -> None:
    """student ロールは VIEW_KNOWLEDGE と VIEW_OWN_HISTORY のみ持つ。"""
    assert has_permission("student", Permission.VIEW_KNOWLEDGE)
    assert has_permission("student", Permission.VIEW_OWN_HISTORY)
    # 上記以外は持たない
    assert not has_permission("student", Permission.MANAGE_KNOWLEDGE)
    assert not has_permission("student", Permission.VIEW_ALL_HISTORY)
    assert not has_permission("student", Permission.MANAGE_FAMILY)
    assert not has_permission("student", Permission.MANAGE_API_KEY)


def test_unknown_role_has_no_permissions() -> None:
    """存在しないロールはいかなる権限も持たない。"""
    for perm in Permission:
        assert not has_permission("unknown_role", perm), f"未知ロールが {perm} を持っている"
