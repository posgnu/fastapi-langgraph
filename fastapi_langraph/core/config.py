from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "fastapi-langraph"
    API_V1_STR: str = "/api/v1"
    TAVILY_API_KEY: Optional[str] = None
    DESCRIPTION: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings() 