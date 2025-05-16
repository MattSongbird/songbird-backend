from fastapi import APIRouter, WebSocket, WebSocketDisconnect



from langchain_openai import ChatOpenAI



from uuid import uuid4



import json



import os







# Attempt to import style_tone and token_tracker, handle if not found initially



try:



    from app.core.style_tone import extract_text_from_url, summarize_style



except ImportError:



    print("Warning: app.core.style_tone not found. Style/tone features might be affected.")



    async def extract_text_from_url(url):



        print(f"Dummy extract_text_from_url called for {url}")



        return "Dummy sample text from URL."



    async def summarize_style(text):



        print(f"Dummy summarize_style called for text: {text[:50]}...")



        return "Dummy voice summary."







try:



    from app.utils.token_tracker import track_tokens



except ImportError:



    print("Warning: app.utils.token_tracker not found. Token tracking will be disabled.")



    def track_tokens(session_id, prompt, response):



        print(f"Dummy track_tokens called for session {session_id}.")







router = APIRouter()



llm = ChatOpenAI(model="gpt-4", temperature=0.7, streaming=True) # Ensure OPENAI_API_KEY is set







session_memory = {}



feedback_log = []







SUPPORTED_TOOLS = [



    "post generator", "blog generator", "video script generator",



    "business coach", "business plan creator", "sales plan creator",



    "marketing plan creator", "industry analysis tool", "ai tool recommender"



]



def identify_tool(prompt: str) -> str:



    classifier_prompt = f"""You are a tool router. Given the user request below, return the best matching tool from this list (exact match only):



{', '.join(SUPPORTED_TOOLS)}



User: {prompt}



Return only the tool name, no explanation."""



    try:



        result = llm.invoke(classifier_prompt)



        if hasattr(result, 'content'):



            return result.content.strip().lower()



        elif isinstance(result, str):



            return result.strip().lower()



        else:



            print(f"Unexpected LLM result type for tool identification: {type(result)}")



            return "general query"



    except Exception as e:



        print(f"Error in identify_tool: {e}")



        return "general query"







@router.websocket("/ws/chat")



async def websocket_chat(websocket: WebSocket):



    await websocket.accept()



    session_id = str(uuid4())



    session_memory.setdefault(session_id, {"chat_history": [], "voice_style": "neutral-professional"})







    if not session_memory[session_id].get("voice_style_confirmed"):



        await websocket.send_json({



            "type": "request_voice_style",



            "message": "Would you like me to apply a specific voice or tone? You can also share a link to writing that matches your style."



        })



        try:



            voice_response_text = await websocket.receive_text()



            voice_data = json.loads(voice_response_text)







            if voice_data.get("type") == "voice_style_response":



                session_memory[session_id]["voice_style"] = voice_data.get("style", "neutral-professional")



                session_memory[session_id]["reference_url"] = voice_data.get("reference_url")



                session_memory[session_id]["voice_style_confirmed"] = True







                if session_memory[session_id]["reference_url"]:



                    sample_text = await extract_text_from_url(session_memory[session_id]["reference_url"])



                    voice_summary = await summarize_style(sample_text)



                    session_memory[session_id]["voice_summary"] = voice_summary



                    await websocket.send_json({



                        "type": "voice_style_summary",



                        "message": f"I’ve analyzed your sample: {voice_summary}"



                    })



                else:



                    await websocket.send_json({



                        "type": "acknowledge_voice_style",



                        "message": f"Got it — I’ll use a {session_memory[session_id]['voice_style']} tone moving forward."



                    })



        except Exception as e:



            print(f"Error processing voice style response: {e}")



            session_memory[session_id]["voice_style"] = "neutral-professional"



            session_memory[session_id]["voice_style_confirmed"] = True



            await websocket.send_json({



                "type": "acknowledge_voice_style",



                "message": "I’ll use a neutral-professional tone for now. Let me know if you’d like something different."



            })







    try:



        while True:



            data = await websocket.receive_text()



            try:



                payload = json.loads(data)



            except json.JSONDecodeError:



                await websocket.send_json({"type": "error", "message": "Invalid JSON"})



                continue







            if payload.get("type") == "chat":



                user_msg = payload.get("message", "")



                # Use session_id established at connection, not from payload for security/consistency



                history = session_memory[session_id].get("chat_history", [])



                context = "\n".join([f"User: {m['user']}\nBot: {m['bot']}" for m in history[-5:]])



                context += f"\nUser: {user_msg}\n"







                tool_identified = identify_tool(user_msg)







                prompt_for_llm = f"Context:\n{context}\n\nRun the {tool_identified} based on: {user_msg}"



                full_response_content = ""



                



                await websocket.send_json({



                    "type": "agent_tool_identified",



                    "tool": tool_identified



                })







                async for chunk_obj in llm.astream(prompt_for_llm):



                    chunk_content = chunk_obj.content if hasattr(chunk_obj, 'content') else str(chunk_obj)



                    await websocket.send_json({



                        "type": "agent_chunk",



                        "content": chunk_content



                    })



                    full_response_content += chunk_content



                



                track_tokens(session_id, prompt_for_llm, full_response_content)



                session_memory[session_id]["chat_history"].append({



                    "user": user_msg,



                    "bot": full_response_content



                })



                await websocket.send_json({



                    "type": "agent_done",



                    "content": full_response_content # Send the complete message once done



                })







            elif payload.get("type") == "feedback":



                feedback_log.append({



                    "session_id": session_id, # Use established session_id



                    "rating": payload.get("rating"),



                    "message": payload.get("message", "")



                })



                await websocket.send_json({"type": "ack", "message": "feedback received"})



            else:



                await websocket.send_json({"type": "error", "message": "Unknown message type"})







    except WebSocketDisconnect:



        print(f"WebSocket disconnected for session: {session_id}")



    except Exception as e:



        print(f"Error in WebSocket handler for session {session_id}: {e}")



        try:



            await websocket.send_json({"type": "error", "message": f"An internal error occurred: {str(e)}"})



        except Exception as send_err:



            print(f"Failed to send error to client: {send_err}")



    finally:



        # Clean up session if necessary, though for in-memory it might not be critical



        # if session_id in session_memory:



        #     del session_memory[session_id]



        print(f"Session {session_id} ended.")
