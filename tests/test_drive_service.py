"""
src/drive/service.py の DriveService テスト（FR-030・FR-031）
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from src.core.exceptions import AuthorizationError, ValidationError
from src.drive.service import DriveService

# ─── テスト用ヘルパー ──────────────────────────────────────────


class _FakeHttpError(Exception):
    """テスト用 HttpError 代替クラス（SDK 非依存）"""

    def __init__(self, status: int) -> None:
        self.resp = MagicMock()
        self.resp.status = status
        super().__init__(f"HTTP {status}")


def _make_service(
    *,
    list_result: dict | None = None,
    media_result: bytes | None = None,
    list_error: Exception | None = None,
    media_error: Exception | None = None,
) -> MagicMock:
    """Drive API service モックを生成する。"""
    service = MagicMock()
    files_mock = service.files.return_value

    if list_error is not None:
        files_mock.list.return_value.execute.side_effect = list_error
    else:
        files_mock.list.return_value.execute.return_value = (
            list_result if list_result is not None else {"files": []}
        )

    if media_error is not None:
        files_mock.get_media.return_value.execute.side_effect = media_error
    elif media_result is not None:
        files_mock.get_media.return_value.execute.return_value = media_result

    return service


# ─── list_pdfs_in_folder テスト ────────────────────────────────


class TestListPdfsInFolder:
    """DriveService.list_pdfs_in_folder のテスト（FR-030）"""

    def test_list_pdfs_success(self) -> None:
        """PDF 2 件返却の正常系"""
        list_result = {
            "files": [
                {"id": "file1", "name": "doc1.pdf"},
                {"id": "file2", "name": "doc2.pdf"},
            ]
        }
        service = _make_service(list_result=list_result)
        drive = DriveService(service)
        result = drive.list_pdfs_in_folder("folder_abc")
        assert result == [
            {"id": "file1", "name": "doc1.pdf"},
            {"id": "file2", "name": "doc2.pdf"},
        ]

    def test_list_pdfs_empty(self) -> None:
        """PDF なし → 空リストを返す"""
        service = _make_service(list_result={"files": []})
        drive = DriveService(service)
        result = drive.list_pdfs_in_folder("folder_empty")
        assert result == []

    def test_list_pdfs_authorization_error(self) -> None:
        """HttpError 403 → AuthorizationError"""
        err = _FakeHttpError(403)
        service = _make_service(list_error=err)
        with patch("src.drive.service.HttpError", _FakeHttpError):
            drive = DriveService(service)
            with pytest.raises(AuthorizationError):
                drive.list_pdfs_in_folder("folder_403")

    def test_list_pdfs_folder_not_found(self) -> None:
        """HttpError 404 → ValidationError（FR030_folder_not_found）、reason_code 属性あり"""
        err = _FakeHttpError(404)
        service = _make_service(list_error=err)
        with patch("src.drive.service.HttpError", _FakeHttpError):
            drive = DriveService(service)
            with pytest.raises(ValidationError) as exc_info:
                drive.list_pdfs_in_folder("folder_404")
            assert exc_info.value.reason_code == "FR030_folder_not_found"

    def test_list_pdfs_api_error(self) -> None:
        """その他 HttpError → RuntimeError"""
        err = _FakeHttpError(500)
        service = _make_service(list_error=err)
        with patch("src.drive.service.HttpError", _FakeHttpError):
            drive = DriveService(service)
            with pytest.raises(RuntimeError):
                drive.list_pdfs_in_folder("folder_500")


# ─── get_metadata テスト ───────────────────────────────────────

_VALID_METADATA_BYTES = json.dumps({"subject": "math", "chapters": ["ch1", "ch2"]}).encode()


class TestGetMetadata:
    """DriveService.get_metadata のテスト（FR-031）"""

    def test_get_metadata_subject_match(self) -> None:
        """subject 一致 → dict を返す"""
        list_result = {"files": [{"id": "meta1", "name": "metadata.json"}]}
        service = _make_service(
            list_result=list_result,
            media_result=_VALID_METADATA_BYTES,
        )
        drive = DriveService(service)
        result = drive.get_metadata("folder_abc", "math")
        assert result == {
            "file_id": "meta1",
            "subject": "math",
            "chapters": ["ch1", "ch2"],
        }

    def test_get_metadata_not_found(self) -> None:
        """metadata.json なし → None"""
        service = _make_service(list_result={"files": []})
        drive = DriveService(service)
        result = drive.get_metadata("folder_no_meta", "math")
        assert result is None

    def test_get_metadata_subject_mismatch(self) -> None:
        """subject 不一致 → None"""
        list_result = {"files": [{"id": "meta2", "name": "metadata.json"}]}
        service = _make_service(
            list_result=list_result,
            media_result=_VALID_METADATA_BYTES,
        )
        drive = DriveService(service)
        result = drive.get_metadata("folder_abc", "science")
        assert result is None

    def test_get_metadata_authorization_error(self) -> None:
        """HttpError 403 → AuthorizationError"""
        err = _FakeHttpError(403)
        service = _make_service(list_error=err)
        with patch("src.drive.service.HttpError", _FakeHttpError):
            drive = DriveService(service)
            with pytest.raises(AuthorizationError):
                drive.get_metadata("folder_403", "math")

    def test_get_metadata_folder_not_found(self) -> None:
        """HttpError 404 → ValidationError（FR031_folder_not_found）、reason_code 属性あり"""
        err = _FakeHttpError(404)
        service = _make_service(list_error=err)
        with patch("src.drive.service.HttpError", _FakeHttpError):
            drive = DriveService(service)
            with pytest.raises(ValidationError) as exc_info:
                drive.get_metadata("folder_404", "math")
            assert exc_info.value.reason_code == "FR031_folder_not_found"

    def test_get_metadata_media_authorization_error(self) -> None:
        """get_media フェーズの HttpError 403 → AuthorizationError"""
        list_result = {"files": [{"id": "meta1", "name": "metadata.json"}]}
        err = _FakeHttpError(403)
        service = _make_service(list_result=list_result, media_error=err)
        with patch("src.drive.service.HttpError", _FakeHttpError):
            drive = DriveService(service)
            with pytest.raises(AuthorizationError):
                drive.get_metadata("folder_abc", "math")

    def test_get_metadata_media_api_error(self) -> None:
        """get_media フェーズのその他 HttpError → RuntimeError"""
        list_result = {"files": [{"id": "meta1", "name": "metadata.json"}]}
        err = _FakeHttpError(500)
        service = _make_service(list_result=list_result, media_error=err)
        with patch("src.drive.service.HttpError", _FakeHttpError):
            drive = DriveService(service)
            with pytest.raises(RuntimeError):
                drive.get_metadata("folder_abc", "math")

    def test_get_metadata_json_parse_error(self) -> None:
        """JSON パースエラー → ValidationError"""
        list_result = {"files": [{"id": "meta3", "name": "metadata.json"}]}
        service = _make_service(
            list_result=list_result,
            media_result=b"this is not valid json{{{",
        )
        drive = DriveService(service)
        with pytest.raises(ValidationError, match="パース"):
            drive.get_metadata("folder_abc", "math")

    def test_get_metadata_api_error(self) -> None:
        """その他 HttpError → RuntimeError"""
        err = _FakeHttpError(500)
        service = _make_service(list_error=err)
        with patch("src.drive.service.HttpError", _FakeHttpError):
            drive = DriveService(service)
            with pytest.raises(RuntimeError):
                drive.get_metadata("folder_500", "math")


# ─── SDK 利用不可テスト ────────────────────────────────────────


class TestSdkNotAvailable:
    """SDK 未インストール時の挙動テスト（P-010 フェイルクローズ）"""

    def test_sdk_not_available(self) -> None:
        """_DRIVE_AVAILABLE=False → __init__ で RuntimeError"""
        with (
            patch("src.drive.service._DRIVE_AVAILABLE", False),
            pytest.raises(RuntimeError, match="google-api-python-client"),
        ):
            DriveService(MagicMock())
