"""공통 예외 (계획서 18.1). 담당: 팀원 1.

화면은 AppError만 잡아 message를 그대로 보여준다.
message는 사용자가 읽을 한국어 문장으로 쓴다.
"""


class AppError(Exception):
    code = "app_error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class PermissionDenied(AppError):
    code = "permission_denied"


class InvalidTransition(AppError):
    code = "invalid_transition"


class ConcurrentUpdate(AppError):
    code = "concurrent_update"


class ValidationError(AppError):
    """잘못된 파일·ROI·파라미터."""

    code = "validation_error"


class NotFound(AppError):
    code = "not_found"


class DuplicateImage(AppError):
    code = "duplicate_image"


class ProcessingFailed(AppError):
    code = "processing_failed"


class StorageError(AppError):
    code = "storage_error"
