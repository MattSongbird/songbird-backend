from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel
from typing import Optional, List

from app.services.business_plan import build_prompt as plan_prompt, run_llm as plan_run, format_output as plan_format
from app.services.sales_plan import build_prompt as sales_prompt, run_llm as sales_run, format_output as sales_format
from app.services.marketing_plan import build_prompt as mkt_prompt, run_llm as mkt_run, format_output as mkt_format
from app.services.industry_analysis import build_prompt as ind_prompt, run_llm as ind_run, format_output as ind_format
from app.services.business_coach import build_prompt as coach_prompt, run_llm as coach_run, format_output as coach_format

class BusinessPartnerState(BaseModel):
    input: str
    prompt: Optional[str] = None
    output: Optional[str] = None
    tool: str = "business_partner_router"
    error: Optional[str] = None
    trace: List[str] = []

def run_all_tools(state: BusinessPartnerState) -> BusinessPartnerState:
    state.trace.append("run_business_plan")
    plan = plan_run(plan_prompt(state))
    state.trace.append("run_sales_plan")
    sales = sales_run(sales_prompt(state))
    state.trace.append("run_marketing_plan")
    mkt = mkt_run(mkt_prompt(state))
    state.trace.append("run_industry_analysis")
    ind = ind_run(ind_prompt(state))
    state.trace.append("run_business_coach")
    coach = coach_run(coach_prompt(state))

    # Combine
    state.output = "\n\n---\n\n".join([
        plan.output or "", sales.output or "", mkt.output or "",
        ind.output or "", coach.output or ""
    ])
    return state

def finalize_output(state: BusinessPartnerState) -> dict:
    state.trace.append("finalize_output")
    if state.error:
        return {"tool": state.tool, "error": state.error}
    return {
        "tool": state.tool,
        "input": state.input,
        "output": state.output,
        "trace": state.trace
    }

def build_business_partner_router():
    graph = StateGraph(BusinessPartnerState)
    graph.add_node("run_all", RunnableLambda(run_all_tools))
    graph.add_node("finalize_output", RunnableLambda(finalize_output))

    graph.set_entry_point("run_all")
    graph.add_edge("run_all", "finalize_output")

    return graph.compile()
