# fmt: off







# fmt: off







from fastapi import APIRouter















from langchain.chat_models import ChatOpenAI















from langchain_core.runnables import RunnableLambda















from langgraph.graph import StateGraph















from pydantic import BaseModel, constr















from uuid import uuid4























router = APIRouter()







llm = ChatOpenAI(model="gpt-4", temperature=0.7)















# In-memory memory store







conversation_memory = {}







feedback_log = []















class ChatMessage(BaseModel):







    message: str







    session_id: str = None















class Feedback(BaseModel):







    session_id: str







    rating: constr(regex="^(up|down)$")







    message: str = ""















# Business tools supported







TOOL_LIST = ["content_creator", "business_partner", "ai_navigator"]



    "content_creator",







    "business_partner",







    "ai_navigator"







]















def identify_tool(prompt: str) -> str:







    classifier_prompt = (







"You are a tool router. Given the user \







    request below, return the best matching tool "







        "from this list (exact match only):\n"







        f"{', '.join(TOOL_LIST)}\n"







        f"User: {prompt}\n"







        "Return only the tool name, no explanation."







    )







    return llm.invoke(classifier_prompt).content.strip().lower()















@router.post("/")







def master_chat_agent(chat: ChatMessage) -> None:







    session_id = chat.session_id or str(uuid4())







    history = conversation_memory.get(session_id, [])







full_context = (







    "\n".join([f"User: {m['user']}\nBot: {m['bot']}" for m in history[-5:]])"







)







    full_context += f"\nUser: {chat.message}\n"















    def classify_and_route(state) -> None:







        user_msg = state['input']







        inferred_tool = identify_tool(user_msg)







        state['tool'] = inferred_tool







        return state















    def run_tool_logic(state) -> None:







        message = state['input']







        tool = state['tool']







full_input = (







    "f"Context:\n{state['context']}\n\nRun the {tool} based on: {message}"







)







        tool_response = llm.invoke(full_input).content







        memory = conversation_memory.setdefault(session_id, [])







        memory.append({"user": message, "bot": tool_response})







        return {







            "session_id": session_id,







            "response": tool_response,







            "inferred_tool": tool







        }















    graph = StateGraph()







    graph.add_node("route", RunnableLambda(classify_and_route))







    graph.add_node("respond", RunnableLambda(run_tool_logic))







    graph.set_entry_point("route")







    graph.add_edge("route", "respond")







    graph.set_finish_point("respond")







    app = graph.compile()















    return app.invoke({"input": chat.message, "context": full_context})















@router.post("/feedback")







def submit_feedback(data: Feedback) -> None:







    feedback_log.append(data.dict())







    return {"status": "received"}







# fmt: on







# fmt: on















from app.services.content_creator import build_prompt as cc_prompt, run_llm as cc_run, format_output as cc_format







from app.services.business_partner import build_prompt as bp_prompt, run_llm as bp_run, format_output as bp_format







from app.services.tool_recommender import build_prompt as tr_prompt, run_llm as tr_run, format_output as tr_format































    if tool not in TOOL_MAP:







        return {"error": f"Unknown tool: {tool}"}







    state = ToolState(input=user_input, tool=tool)







    try:







        state = TOOL_MAP[tool]["build"](state)







        state = TOOL_MAP[tool]["run"](state)







        return TOOL_MAP[tool]["format"](state)







    except Exception as e:







        return {"error": str(e)}











from app.services.content_creator import classify_input as cc_classify, dispatch_prompt as cc_prompt, dispatch_llm as cc_run, dispatch_format as cc_format



from app.services.business_partner import build_prompt as bp_prompt, run_llm as bp_run, format_output as bp_format



from app.services.tool_recommender import build_prompt as tr_prompt, run_llm as tr_run, format_output as tr_format











    state = ToolState(input=user_input, tool=tool)



    if tool == "content_creator":





# === AUTO-INJECTED TOOL REGISTRY ===



from app.services.email_generator import build_prompt as email_generator_prompt, run_llm as email_generator_run, format_output as email_generator_format

from app.services.landing_page_writer import build_prompt as landing_page_writer_prompt, run_llm as landing_page_writer_run, format_output as landing_page_writer_format

from app.services.content_calendar import build_prompt as content_calendar_prompt, run_llm as content_calendar_run, format_output as content_calendar_format

from app.services.hook_generator import build_prompt as hook_generator_prompt, run_llm as hook_generator_run, format_output as hook_generator_format

from app.services.repurpose_tool import build_prompt as repurpose_tool_prompt, run_llm as repurpose_tool_run, format_output as repurpose_tool_format

from app.services.pitch_deck_writer import build_prompt as pitch_deck_writer_prompt, run_llm as pitch_deck_writer_run, format_output as pitch_deck_writer_format

from app.services.customer_persona_gen import build_prompt as customer_persona_gen_prompt, run_llm as customer_persona_gen_run, format_output as customer_persona_gen_format

from app.services.tool_comparison_gen import build_prompt as tool_comparison_gen_prompt, run_llm as tool_comparison_gen_run, format_output as tool_comparison_gen_format

from app.services.tool_recommender import build_prompt as tool_recommender_prompt, run_llm as tool_recommender_run, format_output as tool_recommender_format

from app.services.blog_generator import build_prompt as blog_generator_prompt, run_llm as blog_generator_run, format_output as blog_generator_format

from app.services.post_generator import build_prompt as post_generator_prompt, run_llm as post_generator_run, format_output as post_generator_format

from app.services.video_script import build_prompt as video_script_prompt, run_llm as video_script_run, format_output as video_script_format

from app.services.business_plan import build_prompt as business_plan_prompt, run_llm as business_plan_run, format_output as business_plan_format

from app.services.sales_plan import build_prompt as sales_plan_prompt, run_llm as sales_plan_run, format_output as sales_plan_format

from app.services.marketing_plan import build_prompt as marketing_plan_prompt, run_llm as marketing_plan_run, format_output as marketing_plan_format

from app.services.industry_analysis import build_prompt as industry_analysis_prompt, run_llm as industry_analysis_run, format_output as industry_analysis_format

from app.services.business_coach import build_prompt as business_coach_prompt, run_llm as business_coach_run, format_output as business_coach_format

from app.services.content_creator import build_prompt as content_creator_prompt, run_llm as content_creator_run, format_output as content_creator_format

from app.services.business_partner import build_prompt as business_partner_prompt, run_llm as business_partner_run, format_output as business_partner_format



TOOL_MAP = {

    "email_generator": {"build": email_generator_prompt, "run": email_generator_run, "format": email_generator_format},

    "landing_page_writer": {"build": landing_page_writer_prompt, "run": landing_page_writer_run, "format": landing_page_writer_format},

    "content_calendar": {"build": content_calendar_prompt, "run": content_calendar_run, "format": content_calendar_format},

    "hook_generator": {"build": hook_generator_prompt, "run": hook_generator_run, "format": hook_generator_format},

    "repurpose_tool": {"build": repurpose_tool_prompt, "run": repurpose_tool_run, "format": repurpose_tool_format},

    "pitch_deck_writer": {"build": pitch_deck_writer_prompt, "run": pitch_deck_writer_run, "format": pitch_deck_writer_format},

    "customer_persona_gen": {"build": customer_persona_gen_prompt, "run": customer_persona_gen_run, "format": customer_persona_gen_format},

    "tool_comparison_gen": {"build": tool_comparison_gen_prompt, "run": tool_comparison_gen_run, "format": tool_comparison_gen_format},

    "tool_recommender": {"build": tool_recommender_prompt, "run": tool_recommender_run, "format": tool_recommender_format},

    "blog_generator": {"build": blog_generator_prompt, "run": blog_generator_run, "format": blog_generator_format},

    "post_generator": {"build": post_generator_prompt, "run": post_generator_run, "format": post_generator_format},

    "video_script": {"build": video_script_prompt, "run": video_script_run, "format": video_script_format},

    "business_plan": {"build": business_plan_prompt, "run": business_plan_run, "format": business_plan_format},

    "sales_plan": {"build": sales_plan_prompt, "run": sales_plan_run, "format": sales_plan_format},

    "marketing_plan": {"build": marketing_plan_prompt, "run": marketing_plan_run, "format": marketing_plan_format},

    "industry_analysis": {"build": industry_analysis_prompt, "run": industry_analysis_run, "format": industry_analysis_format},

    "business_coach": {"build": business_coach_prompt, "run": business_coach_run, "format": business_coach_format},

    "content_creator": {"build": content_creator_prompt, "run": content_creator_run, "format": content_creator_format},

    "business_partner": {"build": business_partner_prompt, "run": business_partner_run, "format": business_partner_format},

}



from app.routers.content_creator_router import build_content_creator_router
from app.routers.business_partner_router import build_business_partner_router
from app.routers.ai_navigator_router import build_ai_navigator_router
def run_tool(tool: str, user_input: str):
    from app.api.chatbot import ToolState  # safe reload in scope
    if tool == "content_creator":
        graph = build_content_creator_router()
        state = {"input": user_input}
        result = graph.invoke(state)
        return result
    elif tool == "business_partner":
        graph = build_business_partner_router()
        state = {"input": user_input}
        result = graph.invoke(state)
        return result
    elif tool == "ai_navigator":
        graph = build_ai_navigator_router()
        state = {"input": user_input}
        result = graph.invoke(state)
        return result
    elif tool in TOOL_MAP:
        state = ToolState(input=user_input, tool=tool)
        try:
            state = TOOL_MAP[tool]["build"](state)
            state = TOOL_MAP[tool]["run"](state)
            return TOOL_MAP[tool]["format"](state)
        except Exception as e:
            return {"tool": tool, "error": str(e)}
    else:
        return {"error": f"Unknown tool: {tool}"}