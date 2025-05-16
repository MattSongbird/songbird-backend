from app.utils.token_tracker import track_tokens

from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel
from typing import Optional


llm = ChatOpenAI(model="gpt-4", temperature=0.8)


class ToolState(BaseModel):
    input: str
    prompt: Optional[str] = None
    output: Optional[str] = None
    voice_style: Optional[str] = "attention-grabbing"
    tool: str = "hook_generator"
    error: Optional[str] = None
    token_log: Optional[dict] = None


def build_prompt(state: ToolState) -> ToolState:
    try:
        state.prompt = (
            f"Generate 5 punchy, creative hooks using a {state.voice_style} tone for the following topic or message:

{state.input}

"
            f"Hooks should be short, high-impact, and suitable for posts, titles, or ads."
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
