"""
ドメイン例外定義
"""
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
    """入力値不正"""
    pass
