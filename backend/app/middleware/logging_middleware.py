import time

from fastapi import Request

from app.utils.logger import logger


async def logging_middleware(
    request: Request,
    call_next
):

    start_time = time.perf_counter()

    # =====================================================
    # REQUEST
    # =====================================================

    logger.info(

        "REQUEST | %s %s",

        request.method,

        request.url.path
    )

    try:

        response = await call_next(
            request
        )

        # =================================================
        # RESPONSE
        # =================================================

        duration = (
            time.perf_counter()
            - start_time
        )

        logger.info(

            "RESPONSE | %s %s | "
            "status=%s | "
            "duration=%.4fs",

            request.method,

            request.url.path,

            response.status_code,

            duration
        )

        return response

    except Exception as exc:

        duration = (
            time.perf_counter()
            - start_time
        )

        logger.exception(

            "ERROR | %s %s | "
            "duration=%.4fs | "
            "error=%s",

            request.method,

            request.url.path,

            duration,

            exc
        )

        raise