from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel
from typing import Optional, List

from app.services.tool_recommender import build_prompt as rec_prompt, run_llm as rec_run, format_output as rec_format
from app.services.tool_comparison_gen import build_prompt as comp_prompt, run_llm as comp_run, format_output as comp_format

class AINavigatorState(BaseModel):
    input: str
    use_comparison: Optional[bool] = False
    prompt: Optional[str] = None
    output: Optional[str] = None
    tool: str = "ai_navigator_router"
    error: Optional[str] = None
    trace: List[str] = []

def run_recommender(state: AINavigatorState) -> AINavigatorState:
    state.trace.append("run_tool_recommender")
    return rec_run(rec_prompt(state))

def maybe_compare(state: AINavigatorState) -> str:
    state.trace.append("maybe_compare")
    return "tool_comparison_gen" if state.use_comparison else "finalize_output"

def run_comparison(state: AINavigatorState) -> AINavigatorState:
    state.trace.append("run_tool_comparison_gen")
    return comp_run(comp_prompt(state))

def finalize_output(state: AINavigatorState) -> dict:
    state.trace.append("finalize_output")
    if state.error:
        return {"tool": state.tool, "error": state.error}
    return {
        "tool": state.tool,
        "input": state.input,
        "output": state.output,
        "trace": state.trace
    }

def build_ai_navigator_router():
    graph = StateGraph(AINavigatorState)
    graph.add_node("tool_recommender", RunnableLambda(run_recommender))
    graph.add_node("tool_comparison_gen", RunnableLambda(run_comparison))
    graph.add_node("maybe_compare", RunnableLambda(maybe_compare))
    graph.add_node("finalize_output", RunnableLambda(finalize_output))

    graph.set_entry_point("tool_recommender")
    graph.add_edge("tool_recommender", "maybe_compare")
    graph.add_conditional_edges("maybe_compare", maybe_compare, {
        "tool_comparison_gen": "tool_comparison_gen",
        "finalize_output": "finalize_output"
    })
    graph.add_edge("tool_comparison_gen", "finalize_output")

    return graph.compile()
