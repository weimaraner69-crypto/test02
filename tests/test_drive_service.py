"""
src/drive/service.py のGoogle Drive連携サービス雛形テスト
"""
import pytest
from src.drive.service import DriveService

def test_list_pdfs_in_folder():
    drive = DriveService()
    pdfs = drive.list_pdfs_in_folder("folder1")
    assert isinstance(pdfs, list)
    assert len(pdfs) == 2
    assert pdfs[0]["name"].endswith(".pdf")

def test_get_metadata():
    drive = DriveService()
    meta = drive.get_metadata("folder1", "math")
    assert meta is not None
    assert meta["subject"] == "math"
    assert "file_id" in meta
