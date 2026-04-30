"""ロールベース権限管理。

イシューの utils/permissions.ts に対応するPython実装。
"""

from enum import Enum

from mirastudy.core.models import UserRole


class Permission(Enum):
    """アプリケーション内の操作権限を表す列挙型。"""

    VIEW_KNOWLEDGE = "view_knowledge"
    MANAGE_KNOWLEDGE = "manage_knowledge"
    VIEW_ALL_HISTORY = "view_all_history"
    VIEW_OWN_HISTORY = "view_own_history"
    MANAGE_FAMILY = "manage_family"
    MANAGE_API_KEY = "manage_api_key"


# ロールごとの権限マッピング
ROLE_PERMISSIONS: dict[UserRole, frozenset[Permission]] = {
    UserRole.ADMIN: frozenset(
        [
            Permission.VIEW_KNOWLEDGE,
            Permission.MANAGE_KNOWLEDGE,
            Permission.VIEW_ALL_HISTORY,
            Permission.VIEW_OWN_HISTORY,
            Permission.MANAGE_FAMILY,
            Permission.MANAGE_API_KEY,
        ]
    ),
    UserRole.STUDENT: frozenset(
        [
            Permission.VIEW_KNOWLEDGE,
            Permission.VIEW_OWN_HISTORY,
        ]
    ),
}


def has_permission(role: UserRole, permission: Permission) -> bool:
    """指定ロールが権限を持つか判定する。

    Args:
        role: 判定対象のユーザーロール。
        permission: 確認する権限。

    Returns:
        ロールが権限を持つ場合は True、持たない場合は False。
    """
    return permission in ROLE_PERMISSIONS.get(role, frozenset())
