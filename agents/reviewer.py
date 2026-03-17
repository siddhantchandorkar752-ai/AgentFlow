import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langchain_groq import ChatGroq
from core.state import AgentState
from config import config
from utils.logger import get_logger

logger = get_logger("reviewer")

PROMPT = """You are the Reviewer Agent of AgentFlow.
Verify quality and produce the final answer.

Task: {task}
Plan: {plan}
Research: {research}
Code: {code}
Code Output: {code_output}
Errors: {error}

Format:
QUALITY: <PASS|FAIL>
ISSUES: <none or issues>
FINAL_ANSWER: <complete answer>"""

def reviewer_node(state: AgentState) -> AgentState:
    llm = ChatGroq(api_key=config.GROQ_API_KEY, model=config.MODEL_NAME, temperature=config.TEMPERATURE)
    logger.info("Reviewer running...")
    try:
        response = llm.invoke(PROMPT.format(
            task=state["task"], plan=state.get("plan", ""),
            research=state.get("research", "")[:1500],
            code=state.get("code", ""), code_output=state.get("code_output", ""),
            error=state.get("error", "none")
        ))
        content = response.content
        final_answer = content.split("FINAL_ANSWER:")[1].strip() if "FINAL_ANSWER:" in content else content
        return {**state, "review": content, "final_answer": final_answer, "next": "FINISH", "messages": ["Reviewer: done"]}
    except Exception as e:
        logger.error(f"Reviewer error: {e}")
        return {**state, "error": str(e), "final_answer": f"Error: {str(e)}", "next": "FINISH"}