# fmt: off
# fmt: off
from app.utils.token_tracker import track_tokens

from langchain.chat_models import ChatOpenAI

from langchain_core.runnables import RunnableLambda

from langgraph.graph import StateGraph

from pydantic import BaseModel

from typing import Optional


llm = ChatOpenAI(model="gpt-4", temperature=0.7)

class ToolState(BaseModel):
    input: str
    prompt: Optional[str] = None
    output: Optional[str] = None
    voice_style: Optional[str] = "neutral-professional"
    tool: str = "sales-plan"
    error: Optional[str] = None
    token_log: Optional[dict] = None

def build_prompt(state: ToolState) -> ToolState:
    try:
# fmt: off
# fmt: off
# fmt: off
state.prompt = (
"f"Create a {state.voice_style} sales plan for \
    the following target or product: {state.input}"
)
# fmt: on
# fmt: on
# fmt: on
        return state
    except Exception as e:
        state.error = str(e)
        return state

def run_llm(state: ToolState) -> ToolState:
    if state.error:
        return state
    try:
        result = llm.invoke(state.prompt).content
        state.output = result
        state.token_log = track_tokens(state.tool, state.prompt, result)
        return state
    except Exception as e:
        state.error = str(e)
        return state


from datetime import datetime

from pytz import timezone

def format_output(state: ToolState) -> dict:
    if state.error:
        return {
            "tool": state.tool,
            "error": state.error,
            "timestamp": datetime.now(timezone("UTC")).isoformat(),
            "source_agent": "master_chatbot"
        }
    return {
        "tool": state.tool,
        "output": state.output,
        "voice_style": state.voice_style,
        "tokens_used": state.token_log,
        "timestamp": datetime.now(timezone("UTC")).isoformat(),
        "source_agent": "master_chatbot"
    }

    if state.error:
        return {
            "tool": state.tool,
            "error": state.error
        }
    return {
        "tool": state.tool,
        "output": state.output,
        "voice_style": state.voice_style,
        "tokens_used": state.token_log
    }

def run_sales_plan(req: dict) -> None:
    graph = StateGraph()
    graph.add_node("build_prompt", RunnableLambda(build_prompt))
    graph.add_node("generate", RunnableLambda(run_llm))
    graph.add_node("format", RunnableLambda(format_output))

    graph.set_entry_point("build_prompt")
    graph.add_edge("build_prompt", "generate")
    graph.add_edge("generate", "format")
    graph.set_finish_point("format")

    app = graph.compile()
    return app.invoke(ToolState(**req))
# fmt: on
# fmt: on
