"""业务异常与全局异常处理器：统一返回 { code, message, data }。"""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class BusinessError(Exception):
    """业务异常：code != 0，HTTP 状态码恒为 200。"""

    def __init__(self, code: int = 1, message: str = "业务处理失败"):
        self.code = code
        self.message = message
        super().__init__(message)


def _body(code: int, message: str, data=None) -> dict:
    return {"code": code, "message": message, "data": data}


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器，接口内不散落 try/except 吞异常。"""

    @app.exception_handler(BusinessError)
    async def business_error_handler(request: Request, exc: BusinessError):
        return JSONResponse(status_code=200, content=_body(exc.code, exc.message))

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(status_code=exc.status_code, content=_body(exc.status_code, str(exc.detail)))

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=422, content=_body(422, "参数校验失败", exc.errors()))

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        return JSONResponse(status_code=500, content=_body(500, "服务器内部错误"))
