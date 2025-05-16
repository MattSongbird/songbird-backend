from app.utils.token_tracker import track_tokens
from app.services.business_plan import build_prompt as plan_prompt, run_llm as plan_run, format_output as plan_format
from app.services.sales_plan import build_prompt as sales_prompt, run_llm as sales_run, format_output as sales_format
from app.services.marketing_plan import build_prompt as mkt_prompt, run_llm as mkt_run, format_output as mkt_format
from app.services.industry_analysis import build_prompt as ind_prompt, run_llm as ind_run, format_output as ind_format
from app.services.business_coach import build_prompt as coach_prompt, run_llm as coach_run, format_output as coach_format

from pydantic import BaseModel
from typing import Optional


class ToolState(BaseModel):
    input: str
    prompt: Optional[str] = None
    output: Optional[str] = None
    voice_style: Optional[str] = "founder-friendly"
    tool: str = "business_partner"
    error: Optional[str] = None
    token_log: Optional[dict] = None


def build_prompt(state: ToolState) -> ToolState:
    try:
        state = plan_prompt(state)
        state = sales_prompt(state)
        state = mkt_prompt(state)
        state = ind_prompt(state)
        state = coach_prompt(state)
        return state
    except Exception as e:
        state.error = str(e)
        return state


def run_llm(state: ToolState) -> ToolState:
    if state.error:
        return state
    try:
        combined_output = []
        for func in [plan_run, sales_run, mkt_run, ind_run, coach_run]:
            result_state = func(state)
            if result_state.output:
                combined_output.append(result_state.output)
        state.output = "\n\n---\n\n".join(combined_output)
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
