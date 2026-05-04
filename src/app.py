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
from src.domain.learning import Subject
from src.drive.service import DriveService
from src.gemini.service import GeminiService
from src.learning.service import LearningService
from src.observability.tracing import init_tracer
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
    init_tracer()
    config = AppConfig.from_env()
    _setup_logging(config.log_level)
    profile_service: UserProfileService | None = None

    logger.info("=== MiraStudy CLI ===")
    try:
        # AUTH_MODE に応じた認証サービスを初期化する
        auth = AuthService(mode=config.auth_mode, token_path=config.token_path)
        user = auth.sign_in_with_google()
        if user is None:
            raise AuthenticationError("サインインに失敗しました")
        logger.info("ログイン成功")

        # プロファイル管理
        profile_service = UserProfileService(db_path=config.database_path)
        profile_service.set_profile(user["uid"], user)
        profile = profile_service.get_profile(user["uid"])
        logger.info("プロファイルを保存しました")

        # 権限判定: VIEW_KNOWLEDGE がなければ処理を停止する
        # profile が None は異常状態（フェイルクローズ P-010）
        if profile is None:
            raise AuthorizationError("プロファイルが取得できません。アクセスを拒否します。")
        role = profile.get("role", "student")
        if not has_permission(role, Permission.VIEW_KNOWLEDGE):
            raise AuthorizationError(f"ロール '{role}' は VIEW_KNOWLEDGE 権限を持っていません")
        logger.info("知識共有フォルダ閲覧権限あり")

        # Drive連携
        drive = DriveService()
        pdfs = drive.list_pdfs_in_folder(config.drive_folder_id)
        logger.info("PDF一覧: %s", pdfs)
        meta = drive.get_metadata(config.drive_folder_id, config.gemini_topic)
        logger.info("metadata: %s", meta)

        # GeminiService 初期化（LearningService に注入する）
        gemini = GeminiService(api_key=config.api_key)

        # 学習機能: 学年別コンテンツ配信・問題生成（LearningService 経由で実施）
        learning = LearningService(
            profile_service=profile_service,
            gemini_service=gemini,
        )
        content = learning.get_content_for_grade(config.gemini_grade, Subject.MATH)
        if content is not None:
            logger.info("学年コンテンツ: %s", content.title)

        topic_key = config.gemini_topic
        learning.generate_question(user["uid"], config.gemini_grade, Subject.MATH, topic_key)
        logger.info("学習問題を生成しました")

        learning.record_answer(user["uid"], Subject.MATH, topic_key, is_correct=True)
        summary = learning.get_progress_summary(user["uid"], Subject.MATH)
        logger.info("進捗サマリー: %s", summary)

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
    finally:
        if profile_service is not None:
            profile_service.close()


if __name__ == "__main__":
    main()
