from langchain_community.tools.tavily_search import TavilySearchResults
from fastapi_langraph.core.config import settings

web_search_tool = TavilySearchResults(
    max_results=1, tavily_api_key=settings.TAVILY_API_KEY
)