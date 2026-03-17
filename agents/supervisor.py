import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langchain_groq import ChatGroq
from core.state import AgentState
from config import config
from utils.logger import get_logger

logger = get_logger("supervisor")

PROMPT = """You are the Supervisor Agent of AgentFlow.
Analyze the task and decide the execution plan.

Task: {task}
Iteration: {iteration}

Respond in this exact format:
PLAN: <step by step plan>
NEXT: <researcher|executor|reviewer|FINISH>"""

def supervisor_node(state: AgentState) -> AgentState:
    llm = ChatGroq(api_key=config.GROQ_API_KEY, model=config.MODEL_NAME, temperature=config.TEMPERATURE)
    logger.info(f"Supervisor running | iteration {state['iteration']}")
    try:
        response = llm.invoke(PROMPT.format(task=state["task"], iteration=state["iteration"]))
        content = response.content
        plan, next_agent = "", "researcher"
        for line in content.split("\n"):
            if line.startswith("PLAN:"):
                plan = line.replace("PLAN:", "").strip()
            if line.startswith("NEXT:"):
                next_agent = line.replace("NEXT:", "").strip().lower()
        return {**state, "plan": plan, "next": next_agent, "messages": [f"Supervisor: {plan}"]}
    except Exception as e:
        logger.error(f"Supervisor error: {e}")
        return {**state, "error": str(e), "next": "reviewer"}