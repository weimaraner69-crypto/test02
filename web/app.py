"""
MiraStudy Webアプリ（Flask雛形）
"""

import logging
import os

from flask import Flask, abort, render_template_string
from src.auth.service import AuthService
from src.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DomainError,
    ValidationError,
)
from src.drive.service import DriveService
from src.gemini.service import GeminiService
from src.user.profile import UserProfileService

app = Flask(__name__)
# MUST-1: APIキーは環境変数から読み込む（P-002準拠）
API_KEY = os.environ.get("GEMINI_API_KEY", "")

logger = logging.getLogger(__name__)


@app.route("/")
def index():
    auth = AuthService()
    # MUST-3: sign_in_with_google() の None ガード
    user = auth.sign_in_with_google()
    if user is None:
        raise AuthenticationError("Googleサインインに失敗しました")

    profile_service = UserProfileService()
    try:
        profile_service.set_profile(user["uid"], user)
        profile = profile_service.get_profile(user["uid"])
        drive = DriveService()
        pdfs = drive.list_pdfs_in_folder("folder1")
        gemini = GeminiService(api_key=API_KEY)
        question = gemini.generate_question("PDFコンテキスト", "算数", 3)

        # MUST-2: XSS対策 - Jinja2変数展開で自動エスケープを使用
        html = """
<h1>MiraStudy Web</h1>
<p>ログイン: {{ display_name }} ({{ email }})</p>
<p>プロファイル: {{ profile }}</p>
<p>PDF一覧: {{ pdfs }}</p>
<p>Gemini生成問題: {{ question }}</p>
"""
        return render_template_string(
            html,
            display_name=user["displayName"],
            email=user["email"],
            profile=profile,
            pdfs=pdfs,
            question=question,
        )
    except (AuthenticationError, AuthorizationError, ValidationError, DomainError) as e:
        logger.error("ドメインエラー: %s", e)
        abort(500)
    finally:
        # MUST-3: finally で close() を保証
        profile_service.close()


if __name__ == "__main__":
    # デバッグモードは環境変数で制御
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1", host="0.0.0.0", port=5001)
