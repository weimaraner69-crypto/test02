"""設定管理モジュールのテスト。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.config import AppConfig

if TYPE_CHECKING:
    import pytest


def test_config_defaults() -> None:
    """デフォルト値が正しく設定されている。"""
    config = AppConfig()
    assert config.api_key == ""
    assert config.log_level == "INFO"
    assert config.drive_folder_id == "folder1"
    assert config.gemini_topic == "算数"
    assert config.gemini_grade == 3


def test_config_from_env_all_set(monkeypatch: pytest.MonkeyPatch) -> None:
    """環境変数がすべて設定された場合、正しく読み込まれる。"""
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-123")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DRIVE_FOLDER_ID", "test-folder")
    monkeypatch.setenv("GEMINI_TOPIC", "理科")
    monkeypatch.setenv("GEMINI_GRADE", "5")

    config = AppConfig.from_env()
    assert config.api_key == "test-key-123"
    assert config.log_level == "DEBUG"
    assert config.drive_folder_id == "test-folder"
    assert config.gemini_topic == "理科"
    assert config.gemini_grade == 5


def test_config_from_env_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    """環境変数が未設定の場合はデフォルト値が使われる。"""
    for key in ["GEMINI_API_KEY", "LOG_LEVEL", "DRIVE_FOLDER_ID", "GEMINI_TOPIC", "GEMINI_GRADE"]:
        monkeypatch.delenv(key, raising=False)

    config = AppConfig.from_env()
    assert config.api_key == ""
    assert config.log_level == "INFO"
    assert config.drive_folder_id == "folder1"
    assert config.gemini_topic == "算数"
    assert config.gemini_grade == 3


def test_config_grade_is_int(monkeypatch: pytest.MonkeyPatch) -> None:
    """GEMINI_GRADE が int 型に変換される。"""
    monkeypatch.setenv("GEMINI_GRADE", "6")
    config = AppConfig.from_env()
    assert isinstance(config.gemini_grade, int)
    assert config.gemini_grade == 6


def test_config_grade_invalid_falls_back_to_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """GEMINI_GRADE に不正値が設定された場合、デフォルト値 3 にフォールバックする。"""
    monkeypatch.setenv("GEMINI_GRADE", "not-a-number")
    config = AppConfig.from_env()
    assert config.gemini_grade == 3


def test_config_grade_boundary_min(monkeypatch: pytest.MonkeyPatch) -> None:
    """GEMINI_GRADE = 1（最小学年）が正しく設定される。"""
    monkeypatch.setenv("GEMINI_GRADE", "1")
    config = AppConfig.from_env()
    assert config.gemini_grade == 1


def test_config_grade_boundary_max(monkeypatch: pytest.MonkeyPatch) -> None:
    """GEMINI_GRADE = 6（最大学年）が正しく設定される。"""
    monkeypatch.setenv("GEMINI_GRADE", "6")
    config = AppConfig.from_env()
    assert config.gemini_grade == 6


def test_config_grade_below_min_falls_back_to_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """GEMINI_GRADE = 0（最小値未満）が grade=3 にフォールバックする。"""
    monkeypatch.setenv("GEMINI_GRADE", "0")
    config = AppConfig.from_env()
    assert config.gemini_grade == 3


def test_config_grade_above_max_falls_back_to_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """GEMINI_GRADE = 7（最大値超過）が grade=3 にフォールバックする。"""
    monkeypatch.setenv("GEMINI_GRADE", "7")
    config = AppConfig.from_env()
    assert config.gemini_grade == 3
