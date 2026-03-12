from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette import status


class ApiError(Exception):
    def __init__(self, code: int, message: str, http_status: int = status.HTTP_400_BAD_REQUEST):
        self.code = code
        self.message = message
        self.http_status = http_status
        super().__init__(message)


def api_success(data=None, message: str = "success", code: int = 0):
    return {"code": code, "message": message, "data": data}


def register_exception_handlers(app):
    @app.exception_handler(ApiError)
    async def handle_api_error(_: Request, exc: ApiError):
        return JSONResponse(
            status_code=exc.http_status,
            content={"code": exc.code, "message": exc.message, "data": None},
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"code": 1001, "message": "请求参数校验失败", "data": exc.errors()},
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(_: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": 1000, "message": str(exc.detail), "data": None},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, __: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 5000, "message": "服务器内部错误", "data": None},
        )
