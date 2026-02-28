"""
MiraStudy Webアプリ（Flask雛形）
"""
from flask import Flask, render_template_string, request
from src.auth.service import AuthService
from src.user.profile import UserProfileService
from src.permissions.roles import Permission, has_permission
from src.drive.service import DriveService
from src.gemini.service import GeminiService

app = Flask(__name__)
API_KEY = "dummy-key"

@app.route("/")
def index():
    auth = AuthService()
    user = auth.sign_in_with_google()
    profile_service = UserProfileService()
    profile_service.set_profile(user["uid"], user)
    profile = profile_service.get_profile(user["uid"])
    role = profile.get("role", "student")
    drive = DriveService()
    pdfs = drive.list_pdfs_in_folder("folder1")
    gemini = GeminiService(api_key=API_KEY)
    question = gemini.generate_question("PDFコンテキスト", "算数", 3)
    html = f"""
    <h1>MiraStudy Web</h1>
    <p>ログイン: {user['displayName']} ({user['email']})</p>
    <p>プロファイル: {profile}</p>
    <p>PDF一覧: {pdfs}</p>
    <p>Gemini生成問題: {question}</p>
    """
    return render_template_string(html)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
