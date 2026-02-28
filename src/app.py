"""
MiraStudy CLI統合アプリ（雛形）
"""
from src.auth.service import AuthService
from src.user.profile import UserProfileService
from src.permissions.roles import Permission, has_permission
from src.drive.service import DriveService
from src.gemini.service import GeminiService

# サンプルAPIキー（実運用は安全管理）
API_KEY = "dummy-key"

def main():
    print("=== MiraStudy CLI ===")
    auth = AuthService()
    user = auth.sign_in_with_google()
    print(f"ログイン: {user['displayName']} ({user['email']})")

    # プロファイル管理
    profile_service = UserProfileService()
    profile_service.set_profile(user["uid"], user)
    profile = profile_service.get_profile(user["uid"])
    print(f"プロファイル: {profile}")

    # 権限判定
    role = profile.get("role", "student")
    if has_permission(role, Permission.VIEW_KNOWLEDGE):
        print("知識共有フォルダ閲覧権限あり")

    # Drive連携
    drive = DriveService()
    pdfs = drive.list_pdfs_in_folder("folder1")
    print(f"PDF一覧: {pdfs}")
    meta = drive.get_metadata("folder1", "math")
    print(f"metadata: {meta}")

    # Gemini API連携
    gemini = GeminiService(api_key=API_KEY)
    question = gemini.generate_question("PDFコンテキスト", "算数", 3)
    print(f"Gemini生成問題: {question}")

if __name__ == "__main__":
    main()
