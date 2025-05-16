# Changelog for songbird_backend

## v1_0 - 2025-05-09
- Initial backend scaffolding
- All LangGraph tools implemented
- Contact and GovCon info routes live

## v1_1 - Added chatbot agent and full schema set

## v1_2 - Upgraded chatbot to Master Agent with tool inference

## v1_3 - Added WebSocket chat with real-time LLM streaming and tool routing

## v1_4 - Added token tracking and /metrics/tokens endpoint

## v1_5 - Added style tone mimicry module for session voice personalization
## v1_5 (cont.) - WebSocket flow now prompts for user voice/tone preferences and mimics sample URLs

## v1_6 - Refactored all tools with ToolState, token tracking, and modular LangGraph execution

## v1_7 - Patched WebSocket chatbot to support structured ToolState outputs and metadata streaming

## v1_8 - Added intent classifier + Strategy Agent routing to master WebSocket chatbot

## v1_9 - Enforced final voice/tone filtering on chatbot responses using LLM post-processing

## v1_10 - Added voice/tone presets and memory to Master Chatbot with full style descriptions

## v1_11 - Enabled OpenAPI documentation and added /strategy endpoint to support frontend integration and dev testing

## v1_12 - Added global exception handling with full traceback output for debugging
