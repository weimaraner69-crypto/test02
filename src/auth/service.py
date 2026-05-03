"""
Google OAuth + Firebase Authentication サービス
AUTH_MODE 環境変数でモック/本番を切り替える。
"""

from __future__ import annotations

import logging
import os
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
        self._token_cache: dict | None = None

    @trace_agent_operation("auth.sign_in")
    def sign_in_with_google(self) -> dict | None:
        """
        Googleアカウントでログインする。
        - MOCK モード: テスト用固定ユーザーを返す
        - GOOGLE モード: Google OAuth 2.0 認可コード フローを実行
        """
        if self._mode is AuthMode.MOCK:
            # MOCK モード: テスト用固定ダミーユーザーを返す
            return {
                "uid": "mock_uid_001",
                "email": "mock_user@example.com",
                "displayName": "モックユーザー",
                "isNewUser": False,
            }

        # GOOGLE モード: 本実装
        return self._sign_in_with_google_oauth()

    def _sign_in_with_google_oauth(self) -> dict | None:
        """
        Google OAuth 2.0 認可コード フローでログインする。
        リダイレクト URI: http://localhost:8080/auth/callback
        """
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore[import]
        except ImportError as e:
            logger.error("google-auth-oauthlib が未インストール: %s", e)
            raise RuntimeError("Google OAuth ライブラリが未インストール") from e

        # 環境変数から Google OAuth 認証情報を取得
        client_id = os.environ.get("GOOGLE_CLIENT_ID")
        client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")

        if not client_id or not client_secret:
            logger.error("GOOGLE_CLIENT_ID または GOOGLE_CLIENT_SECRET が未設定")
            raise ValueError("Google OAuth 認証情報が未設定")

        # リダイレクト URI（ローカル開発用）
        redirect_uri = "http://localhost:8080/auth/callback"

        # OAuth フロー作成
        flow = InstalledAppFlow.from_client_secrets_dict(
            {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri],
                }
            },
            scopes=[
                "https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/userinfo.email",
            ],
        )

        # ローカル開発用: web サーバーを起動して認可コードを待機
        try:
            creds = flow.run_local_server(port=8080, open_browser=True)
        except OSError as e:
            logger.error("ローカル web サーバー起動失敗（ポート 8080 が使用中の可能性）: %s", e)
            raise RuntimeError("ローカル web サーバー起動失敗") from e

        # トークンをキャッシュ
        self._token_cache = creds

        # ユーザー情報取得
        try:
            import googleapiclient.discovery  # type: ignore[import]

            service = googleapiclient.discovery.build("oauth2", "v2", credentials=creds)
            user_info = service.userinfo().get().execute()
        except Exception as e:
            logger.error("ユーザー情報取得失敗: %s", e)
            raise RuntimeError("ユーザー情報取得失敗") from e

        return {
            "uid": user_info.get("id"),
            "email": user_info.get("email"),
            "displayName": user_info.get("name", ""),
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
