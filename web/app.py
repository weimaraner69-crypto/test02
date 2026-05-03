"""
MiraStudy Web アプリ（Flask）
AppConfig / AuthService / UserProfileService / GeminiService の現行 API に準拠。
"""

from __future__ import annotations

import logging
import os

from flask import Flask, jsonify, render_template_string
from src.auth.service import AuthService
from src.core.config import AppConfig
from src.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DomainError,
    ValidationError,
)
from src.gemini.service import GeminiService
from src.user.profile import UserProfileService

logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/health")
def health() -> tuple:
    """ヘルスチェックエンドポイント。認証不要。"""
    return jsonify({"status": "ok"}), 200


@app.route("/")
def index():
    """メインページ。認証 → プロファイル取得 → Gemini 問題生成を実行する。"""
    config = AppConfig.from_env()
    profile_service: UserProfileService | None = None
    try:
        # 認証
        auth = AuthService(mode=config.auth_mode)
        user = auth.sign_in_with_google()
        if user is None:
            raise AuthenticationError("サインインに失敗しました")

        # プロファイル管理
        profile_service = UserProfileService(db_path=config.database_path)
        profile_service.set_profile(user["uid"], user)
        profile = profile_service.get_profile(user["uid"])

        # 問題生成
        gemini = GeminiService(api_key=config.api_key)
        question = gemini.generate_question(
            "PDFコンテキスト", config.gemini_topic, config.gemini_grade
        )

        html = """
        <h1>MiraStudy Web</h1>
        <p>ログイン: {{ display_name }} ({{ email }})</p>
        <p>プロファイル: {{ profile }}</p>
        <p>Gemini生成問題: {{ question }}</p>
        """
        return render_template_string(
            html,
            display_name=user["displayName"],
            email=user["email"],
            profile=profile,
            question=question,
        )
    except (AuthenticationError, AuthorizationError, ValidationError, DomainError) as e:
        logger.error("エラー発生: %s", e)
        return render_template_string("<h1>エラー</h1><p>{{ msg }}</p>", msg=str(e)), 500
    finally:
        if profile_service is not None:
            profile_service.close()


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug, host="0.0.0.0", port=5001)
