"""
共通ユーティリティ
"""

from __future__ import annotations

from typing import Dict, TypeVar

T = TypeVar("T")


def safe_get(d: Dict[str, T], key: str, default: T | None = None) -> T | None:
    """
    辞書から安全に値を取得する
    """
    return d.get(key, default)
