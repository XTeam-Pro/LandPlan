"""Пользовательские исключения приложения"""

from typing import Any, Dict, Optional


class ApplicationException(Exception):
    """Базовое исключение приложения"""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationException(ApplicationException):
    """Ошибка аутентификации"""

    def __init__(self, message: str = "Ошибка аутентификации", details=None):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details,
        )


class AuthorizationException(ApplicationException):
    """Пользователь не авторизован для выполнения действия"""

    def __init__(self, message: str = "Не авторизовано", details=None):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=403,
            details=details,
        )


class NotFoundError(ApplicationException):
    """Ресурс не найден"""

    def __init__(self, resource: str, resource_id: Any = None, details=None):
        message = f"{resource} не найден"
        if resource_id:
            message = f"{resource} с id {resource_id} не найден"
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
            details=details,
        )


class ValidationError(ApplicationException):
    """Ошибка валидации"""

    def __init__(self, message: str = "Ошибка валидации", details=None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )


class ConflictError(ApplicationException):
    """Конфликт ресурса (например, дубликат)"""

    def __init__(self, message: str = "Конфликт ресурса", details=None):
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=409,
            details=details,
        )


class InternalServerError(ApplicationException):
    """Ошибка внутреннего сервера"""

    def __init__(self, message: str = "Ошибка внутреннего сервера", details=None):
        super().__init__(
            message=message,
            code="INTERNAL_ERROR",
            status_code=500,
            details=details,
        )
