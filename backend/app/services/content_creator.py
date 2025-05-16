from app.utils.token_tracker import track_tokens
from app.services.blog_generator import build_prompt as blog_prompt, run_llm as blog_run, format_output as blog_format
from app.services.post_generator import build_prompt as post_prompt, run_llm as post_run, format_output as post_format
from app.services.video_script import build_prompt as video_prompt, run_llm as video_run, format_output as video_format

from langchain.chat_models import ChatOpenAI
from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel
from typing import Optional


class ToolState(BaseModel):
    input: str
    input_type: Optional[str] = None  # e.g., blog, post, video
    prompt: Optional[str] = None
    output: Optional[str] = None
    voice_style: Optional[str] = "confident-creator"
    tool: str = "content_creator"
    error: Optional[str] = None
    token_log: Optional[dict] = None


def classify_input(state: ToolState) -> str:
    lower_input = state.input.lower()
    if "video" in lower_input or "script" in lower_input:
        state.input_type = "video"
    elif "blog" in lower_input or "article" in lower_input:
        state.input_type = "blog"
    elif "post" in lower_input or "social" in lower_input:
        state.input_type = "post"
    else:
        state.input_type = "post"  # default
    return state.input_type


def dispatch_prompt(state: ToolState) -> ToolState:
    if state.input_type == "blog":
        return blog_prompt(state)
    elif state.input_type == "video":
        return video_prompt(state)
    else:
        return post_prompt(state)


def dispatch_llm(state: ToolState) -> ToolState:
    if state.input_type == "blog":
        return blog_run(state)
    elif state.input_type == "video":
        return video_run(state)
    else:
        return post_run(state)


def dispatch_format(state: ToolState) -> dict:
    if state.input_type == "blog":
        return blog_format(state)
    elif state.input_type == "video":
        return video_format(state)
    else:
        return post_format(state)
