"""
共通ユーティリティ
"""
from typing import TypeVar, Dict, Optional

T = TypeVar("T")

def safe_get(d: Dict[str, T], key: str, default: Optional[T] = None) -> Optional[T]:
    """
    辞書から安全に値を取得する
    """
    return d.get(key, default)
