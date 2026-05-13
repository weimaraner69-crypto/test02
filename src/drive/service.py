"""
Google Drive API 連携サービス（FR-030・FR-031 準拠）
"""

from __future__ import annotations

import json
import re

from src.core.exceptions import AuthorizationError, ValidationError

# folder_id 入力値検証パターン（英数字・ハイフン・アンダースコアのみを許容）
_FOLDER_ID_RE = re.compile(r"^[A-Za-z0-9_\-]+$")

# google-api-python-client SDK の条件付きインポート（P-010 フェイルクローズ）
try:
    from googleapiclient.discovery import Resource  # type: ignore[import]
    from googleapiclient.errors import HttpError  # type: ignore[import]

    _DRIVE_AVAILABLE = True
except ImportError:
    Resource = None  # type: ignore[assignment, misc]

    class HttpError(Exception):  # type: ignore[no-redef]
        """SDK 未インストール時のダミー HttpError（到達不可）"""

        resp: object = None

    _DRIVE_AVAILABLE = False


class DriveService:
    """Google Drive API 連携サービス"""

    def __init__(self, service: Resource) -> None:
        """認証済み Drive API リソースを注入する。

        Args:
            service: 認証済み googleapiclient.discovery.Resource

        Raises:
            RuntimeError: SDK 未インストール時（P-010 フェイルクローズ）
        """
        if not _DRIVE_AVAILABLE:
            raise RuntimeError(
                "google-api-python-client がインストールされていません。"
                "pip install google-api-python-client を実行してください。"
            )
        self._service = service

    def list_pdfs_in_folder(self, folder_id: str) -> list[dict]:
        """FR-030: 指定フォルダ内の PDF ファイル一覧を取得する。

        Args:
            folder_id: Google Drive のフォルダ ID

        Returns:
            [{"id": str, "name": str}, ...] — PDF ファイルのリスト。
            PDF が存在しない場合は空リスト。

        Raises:
            ValidationError: フォルダが見つからない場合
            AuthorizationError: 権限が不足している場合
            RuntimeError: API 通信エラーが発生した場合（P-010）
        """
        if not _FOLDER_ID_RE.match(folder_id):
            raise ValidationError(
                f"不正な folder_id 形式です: {folder_id!r}",
                reason_code="FR030_folder_not_found",
            )
        query = f"'{folder_id}' in parents and mimeType='application/pdf' and trashed=false"
        try:
            result = self._service.files().list(q=query, fields="files(id, name)").execute()
        except HttpError as e:
            if e.resp.status == 403:
                raise AuthorizationError("Drive アクセス権限がありません") from e
            if e.resp.status == 404:
                raise ValidationError(
                    "フォルダが見つかりません",
                    reason_code="FR030_folder_not_found",
                ) from e
            raise RuntimeError(f"Drive API エラー: {str(e)[:200]}") from e

        files = result.get("files", [])
        return [{"id": f["id"], "name": f["name"]} for f in files]

    def get_metadata(self, folder_id: str, subject: str) -> dict | None:
        """FR-031: フォルダ内の metadata.json を取得し、subject が一致する場合に返す。

        Args:
            folder_id: Google Drive のフォルダ ID
            subject: 照合対象の科目名（Drive 検索条件には使わない）

        Returns:
            {"file_id": str, "subject": str, "chapters": list} — subject 一致時。
            metadata.json 不存在または subject 不一致の場合は None。

        Raises:
            ValidationError: フォルダが見つからない / JSON パースエラーの場合
            AuthorizationError: 権限が不足している場合
            RuntimeError: API 通信エラーが発生した場合（P-010）
        """
        if not _FOLDER_ID_RE.match(folder_id):
            raise ValidationError(
                f"不正な folder_id 形式です: {folder_id!r}",
                reason_code="FR031_folder_not_found",
            )
        query = f"'{folder_id}' in parents and name='metadata.json' and trashed=false"
        try:
            result = self._service.files().list(q=query, fields="files(id, name)").execute()
        except HttpError as e:
            if e.resp.status == 403:
                raise AuthorizationError("Drive アクセス権限がありません") from e
            if e.resp.status == 404:
                raise ValidationError(
                    "フォルダが見つかりません",
                    reason_code="FR031_folder_not_found",
                ) from e
            raise RuntimeError(f"Drive API エラー: {str(e)[:200]}") from e

        files = result.get("files", [])
        if not files:
            return None

        file_id = files[0]["id"]
        try:
            raw = self._service.files().get_media(fileId=file_id).execute()
        except HttpError as e:
            if e.resp.status == 403:
                raise AuthorizationError("Drive アクセス権限がありません") from e
            raise RuntimeError(f"Drive API エラー: {str(e)[:200]}") from e

        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, ValueError) as e:
            raise ValidationError(f"metadata.json のパースに失敗しました: {e}") from e

        if data.get("subject") != subject:
            return None

        return {
            "file_id": file_id,
            "subject": data["subject"],
            "chapters": data.get("chapters", []),
        }
