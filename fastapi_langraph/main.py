from typing import Any, AsyncGenerator, Dict

from fastapi import APIRouter, Body, FastAPI
from fastapi.responses import StreamingResponse

from fastapi_langraph.agent.agent import react_agent
from fastapi_langraph.core.config import settings
from fastapi_langraph.middleware.logging import logging_middleware
from fastapi_langraph.schemas import StreamRequest, StreamResponse

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION or "Default description",
    version="0.1.0",
)

app.middleware("http")(logging_middleware)


router = APIRouter()


@router.get("/")  # type: ignore[misc]
def read_root() -> Dict[str, str]:
    return {"data": "Hello World"}


@router.get("/info")  # type: ignore[misc]
def read_info() -> Dict[str, Any]:
    return {
        "data": {
            "project_name": settings.PROJECT_NAME,
            "description": settings.DESCRIPTION,
            "version": app.version,
        }
    }


@router.post("/stream")  # type: ignore[misc]
async def stream(request: StreamRequest = Body(...)) -> StreamingResponse:
    async def event_stream() -> AsyncGenerator[str, None]:
        async for chunk in react_agent.stream(request.input):
            if "agent" in chunk:
                if messages := chunk["agent"].get("messages"):
                    if messages and len(messages) > 0:
                        # Handle both dict format (from streaming) and message object format
                        if isinstance(messages[0], dict):
                            content = messages[0].get("content", "")
                        else:
                            content = (
                                messages[0].content
                                if hasattr(messages[0], "content")
                                else ""
                            )

                        if content and content.strip():
                            response = StreamResponse(data=content)
                            yield f"{response.model_dump_json()}\n"

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")


app.include_router(router)
