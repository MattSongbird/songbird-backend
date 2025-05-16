from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel
from typing import Optional, List

# === State ===

class RouteState(BaseModel):
    input: str
    tool_group: str
    selected_tool: Optional[str] = None
    output: Optional[str] = None
    error: Optional[str] = None
    trace: List[str] = []

# === Core Nodes ===

def start_node(state: RouteState) -> RouteState:
    state.trace.append("start")
    return state

def route_tool_group(state: RouteState) -> str:
    state.trace.append("route_tool_group")
    if state.tool_group == "content":
        return "content_router"
    elif state.tool_group == "business":
        return "business_router"
    elif state.tool_group == "strategy":
        return "strategy_router"
    elif state.tool_group in ["content_creator", "business_partner", "ai_navigator"]:
        return state.tool_group
    else:
        state.error = f"Unknown tool group: {state.tool_group}"
        return "error_handler"

def content_router(state: RouteState) -> RouteState:
    state.trace.append("content_router")
    state.selected_tool = "blog_generator"  # placeholder for real logic
    return state

def business_router(state: RouteState) -> RouteState:
    state.trace.append("business_router")
    state.selected_tool = "business_plan"  # placeholder
    return state

def strategy_router(state: RouteState) -> RouteState:
    state.trace.append("strategy_router")
    state.selected_tool = "tool_comparison_gen"  # placeholder
    return state

def content_creator(state: RouteState) -> RouteState:
    state.trace.append("content_creator")
    state.output = f"[content_creator output for]: {state.input}"
    return state

def business_partner(state: RouteState) -> RouteState:
    state.trace.append("business_partner")
    state.output = f"[business_partner output for]: {state.input}"
    return state

def ai_navigator(state: RouteState) -> RouteState:
    state.trace.append("ai_navigator")
    state.output = f"[ai_navigator output for]: {state.input}"
    return state

def finalize_output(state: RouteState) -> RouteState:
    state.trace.append("finalize_output")
    if state.output is None and state.selected_tool:
        state.output = f"Executed tool: {state.selected_tool} on input: {state.input}"
    return state

def error_handler(state: RouteState) -> RouteState:
    state.trace.append("error_handler")
    state.output = f"[Error]: {state.error}"
    return state

# === Build Graph ===

def build_routing_graph():
    graph = StateGraph(RouteState)
    graph.add_node("start", RunnableLambda(start_node))
    graph.add_node("route_tool_group", RunnableLambda(route_tool_group))
    graph.add_node("content_router", RunnableLambda(content_router))
    graph.add_node("business_router", RunnableLambda(business_router))
    graph.add_node("strategy_router", RunnableLambda(strategy_router))
    graph.add_node("content_creator", RunnableLambda(content_creator))
    graph.add_node("business_partner", RunnableLambda(business_partner))
    graph.add_node("ai_navigator", RunnableLambda(ai_navigator))
    graph.add_node("finalize_output", RunnableLambda(finalize_output))
    graph.add_node("error_handler", RunnableLambda(error_handler))

    graph.set_entry_point("start")
    graph.add_edge("start", "route_tool_group")
    graph.add_conditional_edges("route_tool_group", route_tool_group, {
        "content_router": "content_router",
        "business_router": "business_router",
        "strategy_router": "strategy_router",
        "content_creator": "content_creator",
        "business_partner": "business_partner",
        "ai_navigator": "ai_navigator",
        "error_handler": "error_handler"
    })

    graph.add_edge("content_router", "finalize_output")
    graph.add_edge("business_router", "finalize_output")
    graph.add_edge("strategy_router", "finalize_output")
    graph.add_edge("content_creator", "finalize_output")
    graph.add_edge("business_partner", "finalize_output")
    graph.add_edge("ai_navigator", "finalize_output")
    graph.add_edge("error_handler", "finalize_output")

    return graph.compile()
