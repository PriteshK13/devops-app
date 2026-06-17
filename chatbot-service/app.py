from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from nlp_engine import process_message

app = FastAPI(
    title="AI Event Assistant Chatbot",
    description="Rule-based event planning assistant with LLM plug-in support.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str | None = None


class ChatResponseModel(BaseModel):
    reply: str
    intent: str
    confidence: float
    suggestions: list[str]


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "chatbot"}


@app.post("/api/chatbot", response_model=ChatResponseModel)
def chat(payload: ChatRequest):
    result = process_message(payload.message)
    return ChatResponseModel(
        reply=result.reply,
        intent=result.intent,
        confidence=result.confidence,
        suggestions=result.suggestions,
    )
