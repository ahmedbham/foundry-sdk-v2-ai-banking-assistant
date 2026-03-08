from fastapi import FastAPI
from pydantic import BaseModel

from agents.account_agent import create_account_agent

app = FastAPI(title="Banking Assistant Middle Tier")


class ChatRequest(BaseModel):
    message: str
    user_id: str = "user1"


@app.post("/chat")
async def chat(request: ChatRequest):
    agent = create_account_agent()
    prompt = f"[User ID: {request.user_id}] {request.message}"
    response = await agent.run(prompt)
    return {"response": response.text}


@app.get("/health")
def health():
    return {"status": "ok"}
