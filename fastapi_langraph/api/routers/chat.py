import logging
import uuid
from datetime import datetime
from typing import AsyncGenerator

from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse

from fastapi_langraph.agent.agent import memory_enabled_agent
from fastapi_langraph.schemas import StreamRequest, StreamResponse

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/stream")  # type: ignore[misc]
async def stream_chat(request: StreamRequest = Body(...)) -> StreamingResponse:
    """
    Stream chat responses with thread-based persistence.

    Features:
    - Automatic thread creation if not provided
    - Persistent conversation state
    - Token-level streaming
    - Comprehensive error handling
    - Request/response tracking
    """

    # Generate thread ID if not provided
    thread_id = request.thread_id or str(uuid.uuid4())

    logger.info(f"Processing stream request for thread {thread_id}")

    async def event_stream() -> AsyncGenerator[str, None]:
        """Generate streaming response events."""
        try:
            # Send initial metadata
            metadata_response = StreamResponse(
                type="metadata",
                content=None,
                thread_id=thread_id,
                user_id=None,
                metadata={
                    "request_id": str(uuid.uuid4()),
                    "timestamp": datetime.utcnow().isoformat(),
                    "thread_created": request.thread_id is None,
                },
            )
            yield f"{metadata_response.model_dump_json()}\n"

            # Stream agent responses
            async for chunk in memory_enabled_agent.astream_events(
                input_data={"input": request.input},
                thread_id=thread_id,
                session_metadata=request.session_metadata,
            ):
                # Transform agent output to API response format
                if chunk.get("event") == "on_chat_model_stream":
                    chunk_data = chunk.get("data", {})
                    content_chunk = chunk_data.get("chunk")

                    if (
                        content_chunk
                        and hasattr(content_chunk, "content")
                        and content_chunk.content
                    ):
                        response = StreamResponse(
                            type="token",
                            content=content_chunk.content,
                            thread_id=thread_id,
                            user_id=None,
                            metadata=None,
                        )
                        yield f"{response.model_dump_json()}\n"

                elif chunk.get("event") in ["on_tool_start", "on_tool_end"]:
                    response = StreamResponse(
                        type="tool_event",
                        content=None,
                        thread_id=thread_id,
                        user_id=None,
                        metadata=chunk.get("data", {}),
                    )
                    yield f"{response.model_dump_json()}\n"

                elif chunk.get("event") == "error":
                    error_response = StreamResponse(
                        type="error",
                        content=chunk.get("data", {}).get("error", "Unknown error"),
                        thread_id=thread_id,
                        user_id=None,
                        metadata=None,
                    )
                    yield f"{error_response.model_dump_json()}\n"

            # Send completion metadata
            completion_response = StreamResponse(
                type="metadata",
                content=None,
                thread_id=thread_id,
                user_id=None,
                metadata={
                    "status": "completed",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
            yield f"{completion_response.model_dump_json()}\n"

        except Exception as e:
            logger.error(f"Error in event stream: {e}")
            error_response = StreamResponse(
                type="error",
                content=f"Stream error: {str(e)}",
                thread_id=thread_id,
                user_id=None,
                metadata=None,
            )
            yield f"{error_response.model_dump_json()}\n"

    return StreamingResponse(
        event_stream(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Thread-ID": thread_id,
        },
    )
