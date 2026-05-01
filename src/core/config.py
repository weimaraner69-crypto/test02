"""
設定管理モジュール
環境変数による設定ロードを担う。利用可能な場合は .env ファイルからも読み込む。
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


def _load_dotenv() -> None:
    """利用可能な場合のみ python-dotenv で .env を読み込む。"""
    try:
        from dotenv import load_dotenv  # type: ignore[import]

        load_dotenv()
        logger.debug(".env ファイルを読み込みました")
    except ImportError:
        logger.debug("python-dotenv が未インストールのため .env の読み込みをスキップします")


@dataclass
class AppConfig:
    """アプリケーション設定。環境変数から構築する。"""

    api_key: str = field(default="", repr=False)
    log_level: str = field(default="INFO")
    drive_folder_id: str = field(default="folder1")
    gemini_topic: str = field(default="算数")
    gemini_grade: int = field(default=3)

    @classmethod
    def from_env(cls) -> AppConfig:
        """環境変数から設定を構築する。.env が存在すれば先に読み込む。"""
        _load_dotenv()
        grade_raw = os.environ.get("GEMINI_GRADE", "3")
        try:
            grade = int(grade_raw)
            if grade < 1 or grade > 6:
                logger.warning(
                    "GEMINI_GRADE の値 %r が有効範囲（1〜6）外です。デフォルト値 3 を使用します。",
                    grade_raw,
                )
                grade = 3
        except ValueError:
            logger.warning(
                "GEMINI_GRADE の値 %r が整数に変換できません。デフォルト値 3 を使用します。",
                grade_raw,
            )
            grade = 3
        return cls(
            api_key=os.environ.get("GEMINI_API_KEY", ""),
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
            drive_folder_id=os.environ.get("DRIVE_FOLDER_ID", "folder1"),
            gemini_topic=os.environ.get("GEMINI_TOPIC", "算数"),
            gemini_grade=grade,
        )
