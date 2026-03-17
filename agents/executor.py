import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langchain_groq import ChatGroq
from core.state import AgentState
from tools.sandbox_tool import run_code
from config import config
from utils.logger import get_logger

logger = get_logger("executor")

PROMPT = """You are the Executor Agent of AgentFlow.
Write Python code to complete the task using only standard library.

Task: {task}
Plan: {plan}
Research: {research}

Wrap code between ```python and ```.
Only use: math, json, datetime, re, statistics, collections."""

def executor_node(state: AgentState) -> AgentState:
    llm = ChatGroq(api_key=config.GROQ_API_KEY, model=config.MODEL_NAME, temperature=config.TEMPERATURE)
    logger.info("Executor running...")
    try:
        response = llm.invoke(PROMPT.format(task=state["task"], plan=state["plan"], research=state.get("research", "")[:2000]))
        content = response.content
        code, code_output = "", ""
        if "```python" in content:
            code = content.split("```python")[1].split("```")[0].strip()
            code_output = run_code(code)
        return {**state, "code": code, "code_output": code_output, "next": "reviewer", "messages": ["Executor: done"]}
    except Exception as e:
        logger.error(f"Executor error: {e}")
        return {**state, "error": str(e), "next": "reviewer"}