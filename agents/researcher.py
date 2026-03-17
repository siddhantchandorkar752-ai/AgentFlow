import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langchain_groq import ChatGroq
from core.state import AgentState
from tools.search_tool import search
from config import config
from utils.logger import get_logger

logger = get_logger("researcher")

PROMPT = """You are the Researcher Agent of AgentFlow.
Gather all relevant information to complete the task.

Task: {task}
Plan: {plan}
Search Results: {results}

Provide a comprehensive research summary."""

def researcher_node(state: AgentState) -> AgentState:
    llm = ChatGroq(api_key=config.GROQ_API_KEY, model=config.MODEL_NAME, temperature=config.TEMPERATURE)
    logger.info("Researcher running...")
    try:
        results = search(state["task"])
        response = llm.invoke(PROMPT.format(task=state["task"], plan=state["plan"], results=results[:3000]))
        return {**state, "research": response.content, "next": "executor", "messages": ["Researcher: completed"]}
    except Exception as e:
        logger.error(f"Researcher error: {e}")
        return {**state, "error": str(e), "next": "reviewer"}