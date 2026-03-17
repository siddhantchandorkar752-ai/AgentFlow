from typing import TypedDict, Annotated, List
import operator

class AgentState(TypedDict):
    task: str
    plan: str
    research: str
    code: str
    code_output: str
    review: str
    final_answer: str
    error: str
    iteration: int
    messages: Annotated[List[str], operator.add]
    next: str
    hitl_required: bool
    approved: bool