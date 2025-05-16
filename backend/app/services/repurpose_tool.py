from app.utils.token_tracker import track_tokens

from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel
from typing import Optional


llm = ChatOpenAI(model="gpt-4", temperature=0.7)


class ToolState(BaseModel):
    input: str
    prompt: Optional[str] = None
    output: Optional[str] = None
    voice_style: Optional[str] = "efficient-adaptive"
    tool: str = "repurpose_tool"
    error: Optional[str] = None
    token_log: Optional[dict] = None


def build_prompt(state: ToolState) -> ToolState:
    try:
        state.prompt = (
            f"Repurpose the following content into multiple formats using a {state.voice_style} tone. "
            f"Create a blog excerpt, a tweet/post, an email intro, and a video script teaser:

{state.input}"
        )
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


def format_output(state: ToolState) -> dict:
    if state.error:
        return {"tool": state.tool, "error": state.error}
    return {
        "tool": state.tool,
        "input": state.input,
        "output": state.output,
        "prompt": state.prompt,
        "token_log": state.token_log,
    }
