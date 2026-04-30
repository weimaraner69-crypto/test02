"""
Google OAuth + Firebase Authentication サービス雛形
"""

from __future__ import annotations


class AuthService:
    def __init__(self):
        # 実際はSDK初期化や設定を行う
        pass

    def sign_in_with_google(self) -> dict | None:
        """
        Googleアカウントでログイン（雛形）
        """
        # 実装例: Google OAuth 2.0 → Firebase Auth
        # 実際は外部SDK/API呼び出し
        return {
            "uid": "sample_uid",
            "email": "user@example.com",
            "displayName": "サンプルユーザー",
            "isNewUser": True,
        }

    def setup_profile(self, uid: str, profile: dict) -> bool:
        """
        初回プロファイル設定（雛形）
        """
        # 実装例: Firestoreへ保存
        return True

    def sign_out(self) -> bool:
        """
        ログアウト（雛形）
        """
        return True
