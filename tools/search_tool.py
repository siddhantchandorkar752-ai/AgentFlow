from tavily import TavilyClient
from config import config
from utils.logger import get_logger

logger = get_logger("search_tool")
client = TavilyClient(api_key=config.TAVILY_API_KEY)

def search(query: str, max_results: int = 5) -> str:
    try:
        logger.info(f"Searching: {query}")
        response = client.search(query=query, max_results=max_results)
        results = response.get("results", [])
        output = "\n\n".join([f"**{r['title']}**\n{r['content']}\nURL: {r['url']}" for r in results])
        return output if output else "No results found."
    except Exception as e:
        logger.error(f"Search error: {e}")
        return f"Search failed: {str(e)}"