"""
Logging middleware for OpportunityOS.
"""

from __future__ import annotations

import logging
import time
import uuid

from fastapi import FastAPI, Request

logger = logging.getLogger("opportunityos")


def register_middlewares(app: FastAPI) -> None:
    """
    Register application middlewares.
    """

    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):

        request_id = str(uuid.uuid4())[:8]
        start_time = time.perf_counter()

        logger.info(
            "[%s] %s %s",
            request_id,
            request.method,
            request.url.path,
        )

        try:
            response = await call_next(request)

        except Exception:
            logger.exception("[%s] Unhandled exception", request_id)
            raise

        process_time = (time.perf_counter() - start_time) * 1000

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.2f} ms"

        logger.info(
            "[%s] %s %s -> %s (%.2f ms)",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            process_time,
        )

        return response