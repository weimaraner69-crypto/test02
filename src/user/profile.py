"""
ユーザープロファイル管理サービス雛形
"""
from typing import Optional, Dict

class UserProfileService:
    def __init__(self):
        # 実際はDB接続や初期化
        self._profiles: Dict[str, dict] = {}

    def get_profile(self, uid: str) -> Optional[dict]:
        """
        ユーザープロファイル取得
        """
        return self._profiles.get(uid)

    def set_profile(self, uid: str, profile: dict) -> bool:
        """
        ユーザープロファイル保存/更新
        """
        self._profiles[uid] = profile
        return True

    def list_family_members(self, admin_uid: str) -> list:
        """
        管理者の家族メンバー一覧取得（雛形）
        """
        # 実際はprofile['familyMembers']参照
        admin = self._profiles.get(admin_uid)
        return admin.get('familyMembers', []) if admin else []
