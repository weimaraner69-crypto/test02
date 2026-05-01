"""
権限管理（ロール・パーミッション）雛形
"""

from enum import Enum, auto


class Permission(Enum):
    VIEW_KNOWLEDGE = auto()
    MANAGE_KNOWLEDGE = auto()
    VIEW_ALL_HISTORY = auto()
    VIEW_OWN_HISTORY = auto()
    MANAGE_FAMILY = auto()
    MANAGE_API_KEY = auto()


RolePermissions = {
    "admin": [
        Permission.VIEW_KNOWLEDGE,
        Permission.MANAGE_KNOWLEDGE,
        Permission.VIEW_ALL_HISTORY,
        Permission.VIEW_OWN_HISTORY,
        Permission.MANAGE_FAMILY,
        Permission.MANAGE_API_KEY,
    ],
    "student": [Permission.VIEW_KNOWLEDGE, Permission.VIEW_OWN_HISTORY],
    # 保護者ロール: 自分の履歴閲覧と家族管理のみ許可（知識共有フォルダへのアクセスは不可）
    "parent": [Permission.VIEW_OWN_HISTORY, Permission.MANAGE_FAMILY],
}


def has_permission(user_role: str, permission: Permission) -> bool:
    """
    ロールに応じた権限判定。
    user_role が str 以外（None 等）の場合は防御的に False を返す。
    """
    if not isinstance(user_role, str):
        return False
    return permission in RolePermissions.get(user_role, [])
