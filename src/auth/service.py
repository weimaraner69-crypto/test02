"""
Google OAuth + Firebase Authentication サービス
AUTH_MODE 環境変数でモック/本番を切り替える。
"""

from __future__ import annotations

import logging
from enum import Enum

from src.observability.tracing import trace_agent_operation

logger = logging.getLogger(__name__)


class AuthMode(Enum):
    """認証モードの列挙型。"""

    MOCK = "mock"
    GOOGLE = "google"


class AuthService:
    def __init__(self, mode: str = "mock") -> None:
        """認証サービスを初期化する。mode は AUTH_MODE 環境変数から渡す。"""
        self._mode = AuthMode(mode)
        if self._mode is AuthMode.GOOGLE:
            logger.warning(
                "GOOGLE モードは未実装です。本番使用前に実装してください。"
                "現在は sign_in_with_google() を呼び出すと NotImplementedError が発生します。"
            )

    @trace_agent_operation("auth.sign_in")
    def sign_in_with_google(self) -> dict | None:
        """
        Googleアカウントでログインする。
        - MOCK モード: テスト用固定ユーザーを返す
        - GOOGLE モード: 将来実装予定（現在は NotImplementedError）
        """
        if self._mode is AuthMode.GOOGLE:
            raise NotImplementedError(
                "Google OAuth は未実装です。AUTH_MODE=mock を使用してください"
            )
        # MOCK モード: テスト用固定ダミーユーザーを返す
        return {
            "uid": "mock_uid_001",
            "email": "mock_user@example.com",
            "displayName": "モックユーザー",
            "isNewUser": False,
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
