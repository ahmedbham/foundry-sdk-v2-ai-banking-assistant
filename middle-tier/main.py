from fastapi import FastAPI
from pydantic import BaseModel

from agents.supervisor_agent import create_handoff_workflow

app = FastAPI(title="Banking Assistant Middle Tier")


class ChatRequest(BaseModel):
    message: str
    user_id: str = "user1"


@app.post("/chat")
async def chat(request: ChatRequest):
    workflow = create_handoff_workflow()
    prompt = f"[User ID: {request.user_id}] {request.message}"
    result = await workflow.run(prompt)

    # Extract the final response from workflow outputs
    outputs = result.get_outputs()
    if outputs:
        last_output = outputs[-1]
        # Output may be an AgentResponse (has .text) or a list of Messages
        if hasattr(last_output, 'text') and last_output.text:
            return {"response": last_output.text}
        if isinstance(last_output, list):
            for msg in reversed(last_output):
                if msg.role == "assistant" and msg.text:
                    return {"response": msg.text}

    return {"response": "I'm sorry, I couldn't process your request."}


@app.get("/health")
def health():
    return {"status": "ok"}
