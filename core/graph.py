from langgraph.graph import StateGraph, END
from core.state import AgentState
from agents.supervisor import supervisor_node
from agents.researcher import researcher_node
from agents.executor import executor_node
from agents.reviewer import reviewer_node
from utils.logger import get_logger

logger = get_logger("graph")

def route(state: AgentState) -> str:
    next_node = state.get("next", "reviewer")
    iteration = state.get("iteration", 0)
    if iteration >= 10:
        logger.warning("Max iterations reached")
        return "reviewer"
    if next_node == "FINISH":
        return END
    return next_node

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("executor", executor_node)
    graph.add_node("reviewer", reviewer_node)
    graph.set_entry_point("supervisor")
    graph.add_conditional_edges("supervisor", route, {
        "researcher": "researcher",
        "executor": "executor",
        "reviewer": "reviewer",
        END: END,
    })
    graph.add_conditional_edges("researcher", route, {
        "executor": "executor",
        "reviewer": "reviewer",
        END: END,
    })
    graph.add_conditional_edges("executor", route, {
        "reviewer": "reviewer",
        END: END,
    })
    graph.add_conditional_edges("reviewer", route, {
        END: END,
    })
    logger.info("Graph built successfully")
    return graph.compile()