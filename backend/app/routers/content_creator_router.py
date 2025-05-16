from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel
from typing import Optional, List

from app.services.blog_generator import build_prompt as blog_prompt, run_llm as blog_run, format_output as blog_format
from app.services.post_generator import build_prompt as post_prompt, run_llm as post_run, format_output as post_format
from app.services.video_script import build_prompt as video_prompt, run_llm as video_run, format_output as video_format

class ContentCreatorState(BaseModel):
    input: str
    content_type: Optional[str] = None  # blog, post, video
    prompt: Optional[str] = None
    output: Optional[str] = None
    tool: str = "content_creator_router"
    error: Optional[str] = None
    trace: List[str] = []

def classify_content(state: ContentCreatorState) -> str:
    state.trace.append("classify_content")
    text = state.input.lower()
    if "video" in text or "script" in text:
        state.content_type = "video"
        return "video_script"
    elif "blog" in text or "article" in text:
        state.content_type = "blog"
        return "blog_generator"
    else:
        state.content_type = "post"
        return "post_generator"

def run_blog(state: ContentCreatorState) -> ContentCreatorState:
    state.trace.append("run_blog_generator")
    return blog_run(blog_prompt(state))

def run_post(state: ContentCreatorState) -> ContentCreatorState:
    state.trace.append("run_post_generator")
    return post_run(post_prompt(state))

def run_video(state: ContentCreatorState) -> ContentCreatorState:
    state.trace.append("run_video_script")
    return video_run(video_prompt(state))

def finalize_output(state: ContentCreatorState) -> dict:
    state.trace.append("finalize_output")
    if state.error:
        return {"tool": state.tool, "error": state.error}
    return blog_format(state) if state.content_type == "blog" else            post_format(state) if state.content_type == "post" else            video_format(state)

def build_content_creator_router():
    graph = StateGraph(ContentCreatorState)
    graph.add_node("classify_content", RunnableLambda(classify_content))
    graph.add_node("blog_generator", RunnableLambda(run_blog))
    graph.add_node("post_generator", RunnableLambda(run_post))
    graph.add_node("video_script", RunnableLambda(run_video))
    graph.add_node("finalize_output", RunnableLambda(finalize_output))

    graph.set_entry_point("classify_content")
    graph.add_conditional_edges("classify_content", classify_content, {
        "blog_generator": "blog_generator",
        "post_generator": "post_generator",
        "video_script": "video_script"
    })

    graph.add_edge("blog_generator", "finalize_output")
    graph.add_edge("post_generator", "finalize_output")
    graph.add_edge("video_script", "finalize_output")

    return graph.compile()
