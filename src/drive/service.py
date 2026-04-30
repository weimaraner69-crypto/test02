"""
Google Drive API連携サービス雛形
"""

from __future__ import annotations


class DriveService:
    def __init__(self):
        # 実際はGoogle API認証・初期化
        pass

    def list_pdfs_in_folder(self, folder_id: str) -> list[dict]:
        """
        共有フォルダ内のPDF一覧取得（雛形）
        """
        # 実際はGoogle Drive API呼び出し
        return [{"id": "file1", "name": "sample1.pdf"}, {"id": "file2", "name": "sample2.pdf"}]

    def get_metadata(self, folder_id: str, subject: str) -> dict | None:
        """
        metadata.json取得（雛形）
        """
        # 実際はDrive APIでJSON取得
        return {"file_id": "file1", "subject": subject, "chapters": []}
