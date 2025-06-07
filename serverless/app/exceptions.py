from fastapi import FastAPI, Request, responses


class AppException(Exception):
    status_code: int = 500
    message: str = "Internal Server Error"
    details: dict | None = None


class NotFound(AppException):
    status_code: int = 404
    message: str = "Not Found"

    def __init__(
        self, resource: str, resource_id: int
    ) -> None:
        self.details = {resource: resource_id}


class AlreadyExists(AppException):
    """
    Exception raised when a resource already exists.
    """
    status_code: int = 400
    message: str = "Resource already exists"

    def __init__(self, resource: str, resource_id: int) -> None:
        self.details = {resource: resource_id}


class DatabaseError(AppException):
    """
    Exception raised for any unexpected database-related error.
    """
    status_code: int = 500
    message: str = "Database Error"

    def __init__(
        self,
        detail: str | None = None,
        original_exception: Exception | None = None
    ) -> None:
        """
        :param detail: 人間が読める追加情報（任意）
        :param original_exception: 元になった例外インスタンス（任意）
        """
        # 追加情報があれば details に格納
        if detail:
            self.details = {"info": detail}

        # 必要に応じて元の例外情報も一緒に保持しておく
        if original_exception:
            self.details = self.details or {}
            self.details["original_exception"] = repr(original_exception)


def init_exception_handler(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exception_handler(
        req: Request, exc: AppException
    ):
        content = {"message": exc.message}
        if exc.details:
            content["details"] = exc.details
        return responses.JSONResponse(
            status_code=exc.status_code,
            content=content,
        )
