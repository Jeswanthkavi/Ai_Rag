from fastapi import Request

from fastapi.responses import JSONResponse

from app.utils.logger import logger


async def global_exception_handler(
    request: Request,
    exc: Exception
):

    logger.exception(

        "UNHANDLED ERROR | "
        "%s %s | "
        "error=%s",

        request.method,

        request.url.path,

        exc
    )

    return JSONResponse(

        status_code=500,

        content={

            "error":
                "Internal server error",

            "message":
                "Something went wrong."
        }
    )