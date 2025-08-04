import time
from fastapi import Request
from loguru import logger

async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"\"{request.method} {request.url.path} {request.scope['http_version']}\" {response.status_code} {process_time:.2f}s"
    )
    return response
