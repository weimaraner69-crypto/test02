"""
ドメイン例外定義
"""

from __future__ import annotations


class DomainError(Exception):
    """ドメイン汎用例外"""

    pass


class AuthenticationError(DomainError):
    """認証失敗"""

    pass


class AuthorizationError(DomainError):
    """権限不足"""

    pass


class ValidationError(DomainError):
    """入力値不正

    Attributes:
        reason_code: 制約・バリデーションルールごとの識別コード。
            例: "C001_invalid_grade"、"FR030_folder_not_found"
    """

    def __init__(self, message: str = "", reason_code: str | None = None) -> None:
        super().__init__(message)
        self.reason_code = reason_code
