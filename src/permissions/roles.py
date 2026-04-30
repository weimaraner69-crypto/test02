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
}


def has_permission(user_role: str, permission: Permission) -> bool:
    """
    ロールに応じた権限判定
    """
    return permission in RolePermissions.get(user_role, [])
