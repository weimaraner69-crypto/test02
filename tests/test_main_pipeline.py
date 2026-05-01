"""MVP パイプライン統合テスト。

認証 → プロファイル管理 → 権限判定 → Drive 連携 → Gemini 問題生成
の一連のフローが例外なく動作することを検証する。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.app import main
from src.auth.service import AuthService
from src.drive.service import DriveService
from src.gemini.service import GeminiService
from src.permissions.roles import Permission, has_permission
from src.user.profile import UserProfileService

if TYPE_CHECKING:
    import pytest


def test_main_pipeline_no_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() が例外なく実行できることを確認する。"""
    monkeypatch.setenv("DATABASE_PATH", ":memory:")
    main()


def test_auth_returns_user_dict():
    """AuthService が必須フィールドを持つユーザー辞書を返す。"""
    auth = AuthService()
    user = auth.sign_in_with_google()
    assert user is not None
    assert {"uid", "email", "displayName"}.issubset(user.keys())


def test_profile_set_and_get() -> None:
    """プロファイルを保存した後に取得できる。"""
    service = UserProfileService(db_path=":memory:")
    uid = "test_uid_001"
    profile = {"uid": uid, "email": "test@example.com", "role": "student"}
    assert service.set_profile(uid, profile) is True
    result = service.get_profile(uid)
    service.close()
    assert result is not None
    assert result["uid"] == uid


def test_permission_student_can_view_knowledge():
    """student ロールが VIEW_KNOWLEDGE 権限を持つ。"""
    assert has_permission("student", Permission.VIEW_KNOWLEDGE) is True


def test_permission_student_cannot_manage_knowledge():
    """student ロールが MANAGE_KNOWLEDGE 権限を持たない。"""
    assert has_permission("student", Permission.MANAGE_KNOWLEDGE) is False


def test_permission_admin_has_all_permissions():
    """admin ロールが全権限を持つ。"""
    for perm in Permission:
        assert has_permission("admin", perm) is True


def test_drive_list_pdfs_returns_list():
    """DriveService が PDF 一覧（リスト）を返す。"""
    drive = DriveService()
    pdfs = drive.list_pdfs_in_folder("folder_test")
    assert isinstance(pdfs, list)
    assert len(pdfs) > 0
    assert "id" in pdfs[0]
    assert "name" in pdfs[0]


def test_drive_get_metadata_returns_dict():
    """DriveService が metadata 辞書を返す。"""
    drive = DriveService()
    meta = drive.get_metadata("folder_test", "算数")
    assert meta is not None
    assert "subject" in meta
    assert meta["subject"] == "算数"


def test_gemini_generate_question_structure():
    """GeminiService が期待する構造の問題を返す。"""
    gemini = GeminiService(api_key="dummy-key")
    result = gemini.generate_question("テストコンテキスト", "算数", 3)
    assert result is not None
    assert "question" in result
    assert "answer" in result
    assert "hints" in result
    assert "curriculum_reference" in result
    assert isinstance(result["question"]["options"], list)


def test_full_pipeline_flow() -> None:
    """MVP パイプライン全体フローが整合して動作する。"""
    # 認証
    auth = AuthService()
    user = auth.sign_in_with_google()
    assert user is not None

    # プロファイル設定・取得
    profile_service = UserProfileService(db_path=":memory:")
    profile_service.set_profile(user["uid"], user)
    profile = profile_service.get_profile(user["uid"])
    profile_service.set_learning_progress(
        user["uid"], "算数", {"topic": "算数", "status": "generated"}
    )
    progress = profile_service.get_learning_progress(user["uid"], "算数")
    profile_service.close()
    assert profile is not None
    assert progress is not None

    # 権限判定
    role = profile.get("role", "student")
    assert isinstance(role, str)
    can_view = has_permission(role, Permission.VIEW_KNOWLEDGE)
    assert isinstance(can_view, bool)

    # Drive 連携
    drive = DriveService()
    pdfs = drive.list_pdfs_in_folder("folder1")
    assert isinstance(pdfs, list)

    # Gemini 問題生成
    gemini = GeminiService(api_key="dummy-key")
    question = gemini.generate_question("コンテキスト", "算数", 3)
    assert question is not None
    assert "question" in question
