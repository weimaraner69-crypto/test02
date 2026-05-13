"""
MiraStudy Web アプリ（Flask）
AppConfig / AuthService / UserProfileService / GeminiService の現行 API に準拠。
"""

from __future__ import annotations

import logging
import os

from flask import Flask, jsonify, redirect, render_template_string, session, url_for
from src.auth.service import AuthService
from src.core.config import AppConfig
from src.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DomainError,
    RateLimitError,
    ValidationError,
)
from src.domain.learning import Subject
from src.gemini.service import GeminiService
from src.learning.service import LearningService
from src.user.profile import UserProfileService

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """Flask アプリを生成して返す。SECRET_KEY 未設定時は起動エラーとする。"""
    secret_key = os.environ.get("SECRET_KEY", "")
    if not secret_key:
        raise RuntimeError("SECRET_KEY が未設定です。起動前に環境変数を設定してください。")

    flask_app = Flask(__name__)
    flask_app.config["SECRET_KEY"] = secret_key
    flask_app.config["SESSION_COOKIE_HTTPONLY"] = True
    flask_app.config["SESSION_COOKIE_SECURE"] = True
    flask_app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    return flask_app


app = create_app()


@app.route("/health")
def health() -> tuple:
    """ヘルスチェックエンドポイント。認証不要。"""
    return jsonify({"status": "ok"}), 200


@app.route("/")
def index():
    """メインページ。ログイン済みセッションを前提に問題生成を実行する。"""
    if "uid" not in session:
        return redirect(url_for("login"))

    config = AppConfig.from_env()
    profile_service: UserProfileService | None = None
    try:
        # プロファイル管理
        profile_service = UserProfileService(db_path=config.database_path)
        user = {
            "uid": session["uid"],
            "email": session.get("email", ""),
            "displayName": session.get("display_name", ""),
            "isNewUser": False,
        }
        profile_service.set_profile(user["uid"], user)
        profile = profile_service.get_profile(user["uid"])

        # 問題生成（LearningService 経由で C-003/C-004 を適用）
        gemini = GeminiService(api_key=config.api_key)
        learning = LearningService(profile_service=profile_service, gemini_service=gemini)
        question = learning.generate_question(
            uid=user["uid"],
            grade=config.gemini_grade,
            subject=Subject.MATH,
            topic=config.gemini_topic,
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
    except RateLimitError:
        logger.exception("index 処理中にレート制限を検知")
        return render_template_string(
            "<h1>アクセス制限</h1><p>アクセスが集中しています。しばらく時間をおいて再試行してください。</p>"
        ), 429
    except ValidationError as e:
        if e.reason_code == "C004_session_timeout":
            logger.exception("index 処理中にセッション時間制限を検知")
            return render_template_string(
                "<h1>休憩のお願い</h1><p>学習セッションの時間上限に達しました。休憩してから再開してください。</p>"
            ), 429
        logger.exception("index 処理中に検証エラーが発生")
        return render_template_string(
            "<h1>エラー</h1><p>処理中にエラーが発生しました。時間をおいて再試行してください。</p>"
        ), 500
    except (
        AuthenticationError,
        AuthorizationError,
        DomainError,
        RuntimeError,
        OSError,
        ConnectionError,
        TimeoutError,
    ):
        logger.exception("index 処理中にエラーが発生")
        return render_template_string(
            "<h1>エラー</h1><p>処理中にエラーが発生しました。時間をおいて再試行してください。</p>"
        ), 500
    finally:
        if profile_service is not None:
            profile_service.close()


@app.route("/login", methods=["GET"])
def login_page():
    """ログイン画面を表示する。"""
    html = (
        "<h1>ログイン</h1>"
        "<form method='POST' action='/login'>"
        "<button type='submit'>Google でログイン</button>"
        "</form>"
    )
    return render_template_string(html), 200


@app.route("/login", methods=["POST"])
def login():
    """ログイン処理を実行し、成功時はセッションを作成してトップへ遷移する。"""
    config = AppConfig.from_env()
    try:
        auth = AuthService(mode=config.auth_mode)
        user = auth.sign_in_with_google()
        if user is None:
            raise AuthenticationError("サインインに失敗しました")

        # ログイン時は既存セッションを破棄して新しいセッション情報のみ保持する
        session.clear()
        session["uid"] = user["uid"]
        session["email"] = user.get("email", "")
        session["display_name"] = user.get("displayName", "")
        return redirect(url_for("index"))
    except (
        AuthenticationError,
        AuthorizationError,
        ValidationError,
        DomainError,
        RuntimeError,
        OSError,
        ConnectionError,
        TimeoutError,
    ):
        logger.exception("login 処理中にエラーが発生")
        return render_template_string(
            "<h1>エラー</h1><p>ログイン処理でエラーが発生しました。設定を確認してください。</p>"
        ), 500


@app.route("/logout", methods=["POST"])
def logout():
    """セッションを破棄してログインページへ遷移する。"""
    session.clear()
    return redirect(url_for("login"), code=303)


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    host = os.environ.get("FLASK_HOST", "127.0.0.1")
    app.run(debug=debug, host=host, port=5001)
