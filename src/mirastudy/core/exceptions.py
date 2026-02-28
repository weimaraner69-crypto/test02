"""MiraStudy カスタム例外。"""


class MiraStudyError(Exception):
    """MiraStudy の基底例外。"""


class PermissionDeniedError(MiraStudyError):
    """権限不足エラー。"""


class InvalidStageError(MiraStudyError):
    """無効なステージエラー。"""


class InvalidGradeError(MiraStudyError):
    """無効な学年エラー。"""


class CacheExpiredError(MiraStudyError):
    """コンテキストキャッシュ期限切れエラー。"""
