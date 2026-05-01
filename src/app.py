"""
MiraStudy CLI統合アプリ（雛形）
"""

from __future__ import annotations

import logging

from src.auth.service import AuthService
from src.core.config import AppConfig
from src.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DomainError,
    ValidationError,
)
from src.drive.service import DriveService
from src.gemini.service import GeminiService
from src.permissions.roles import Permission, has_permission
from src.user.profile import UserProfileService

logger = logging.getLogger(__name__)


def _setup_logging(level: str) -> None:
    """ログ設定を初期化する。"""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def main() -> None:
    """メインパイプライン。設定ロード → 認証 → プロファイル → 権限判定 → Drive → Gemini。"""
    config = AppConfig.from_env()
    _setup_logging(config.log_level)

    print("=== MiraStudy CLI ===")
    try:
        # AUTH_MODE に応じた認証サービスを初期化する
        auth = AuthService(mode=config.auth_mode)
        user = auth.sign_in_with_google()
        if user is None:
            raise AuthenticationError("サインインに失敗しました")
        print(f"ログイン: {user['displayName']}")

        # プロファイル管理
        profile_service = UserProfileService()
        profile_service.set_profile(user["uid"], user)
        profile = profile_service.get_profile(user["uid"])
        print(f"プロファイル: {profile}")

        # 権限判定: VIEW_KNOWLEDGE がなければ処理を停止する
        # profile が None は異常状態（フェイルクローズ P-010）
        if profile is None:
            raise AuthorizationError("プロファイルが取得できません。アクセスを拒否します。")
        role = profile.get("role", "student")
        if not has_permission(role, Permission.VIEW_KNOWLEDGE):
            raise AuthorizationError(
                f"ロール '{role}' は VIEW_KNOWLEDGE 権限を持っていません"
            )
        print("知識共有フォルダ閲覧権限あり")

        # Drive連携
        drive = DriveService()
        pdfs = drive.list_pdfs_in_folder(config.drive_folder_id)
        print(f"PDF一覧: {pdfs}")
        meta = drive.get_metadata(config.drive_folder_id, config.gemini_topic)
        print(f"metadata: {meta}")

        # Gemini API連携
        gemini = GeminiService(api_key=config.api_key)
        question = gemini.generate_question(
            "PDFコンテキスト", config.gemini_topic, config.gemini_grade
        )
        print(f"Gemini生成問題: {question}")

    except AuthenticationError as e:
        logger.error("認証エラー: %s", e)
        raise
    except AuthorizationError as e:
        logger.error("認可エラー: %s", e)
        raise
    except ValidationError as e:
        logger.error("検証エラー: %s", e)
        raise
    except DomainError as e:
        logger.error("ドメインエラー: %s", e)
        raise


if __name__ == "__main__":
    main()
