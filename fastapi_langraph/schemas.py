from pydantic import BaseModel, Field


class StreamRequest(BaseModel):  # type: ignore[misc]
    input: str = Field(..., description="The user's query for the agent")


class StreamResponse(BaseModel):  # type: ignore[misc]
    data: str
