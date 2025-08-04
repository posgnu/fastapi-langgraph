from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi_langraph.core.config import settings
from fastapi_langraph.middleware.logging import logging_middleware
from fastapi_langraph.agent.agent import react_agent

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version="0.1.0",
)

app.middleware("http")(logging_middleware)

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/info")
def read_info():
    return {
        "project_name": settings.PROJECT_NAME,
        "description": settings.DESCRIPTION,
        "version": app.version,
    }

@app.post("/stream")
async def stream(query: str):
    async def event_stream():
        async for chunk in react_agent.stream(query):
            yield f"data: {chunk}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream") 