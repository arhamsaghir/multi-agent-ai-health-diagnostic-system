"""Chat API routes — conversational symptom checking with memory and safety guardrails."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import time
import uuid
from loguru import logger

from src.llm.openai_client import OpenAIClient

router = APIRouter(prefix="/chat", tags=["chat"])

# In-memory conversation store (use Redis in production)
_conversations: dict[str, list[dict]] = {}

# Global OpenAI client (lazy-loaded)
_openai_client = None

# Safety keywords that trigger medical escalation
SAFETY_KEYWORDS = [
    "emergency", "call 911", "ambulance", "heart attack", "stroke",
    "can't breathe", "severe chest pain", "unconscious", "bleeding",
    "suicidal", "overdose", "poisoning",
]

# Medical disclaimer
DISCLAIMER = "I am an AI health assistant, not a doctor. This information is for educational purposes only. Always consult a healthcare professional for medical advice."


def get_openai_client() -> OpenAIClient:
    """Get or create the OpenAI client."""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClient()
    return _openai_client


class ChatMessageRequest(BaseModel):
    """Request for a chat message."""
    message: str = Field(..., description="User's message")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID (creates new if omitted)")


class ChatMessageResponse(BaseModel):
    """Response from chat message."""
    conversation_id: str
    response: str
    safety_alert: bool = False
    safety_message: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)


class ConversationSummary(BaseModel):
    """Summary of a conversation."""
    conversation_id: str
    message_count: int
    created_at: float
    last_message_at: float


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest):
    """Send a message and get an AI response.

    Handles conversation memory and safety guardrails.
    Escalates to emergency guidance if safety keywords detected.
    """
    # Create or retrieve conversation
    conv_id = request.conversation_id or str(uuid.uuid4())
    if conv_id not in _conversations:
        _conversations[conv_id] = []

    # Check for safety keywords
    safety_alert = False
    safety_message = None
    msg_lower = request.message.lower()
    for keyword in SAFETY_KEYWORDS:
        if keyword in msg_lower:
            safety_alert = True
            safety_message = (
                "⚠️ SAFETY ALERT: Your symptoms may indicate a medical emergency. "
                "Please call your local emergency number (911, 999, or 112) or go to "
                "the nearest emergency room immediately. Do not wait for online advice."
            )
            logger.warning(f"Safety alert triggered in conversation {conv_id}: {keyword}")
            break

    # Add user message to history
    _conversations[conv_id].append({
        "role": "user",
        "content": request.message,
        "timestamp": time.time(),
    })

    # Build system message with safety guardrails
    system_message = f"""You are a helpful, cautious medical AI assistant for a health diagnostic system.

IMPORTANT RULES:
1. {DISCLAIMER}
2. Never make definitive diagnoses — always say "possible" or "may indicate"
3. Recommend seeing a doctor for any moderate or severe symptoms
4. Be empathetic but factual
5. If the user describes emergency symptoms, advise them to seek immediate medical care
6. Keep responses concise (2-4 paragraphs)
7. Use simple, patient-friendly language
8. If asked about specific medications, say to consult a pharmacist or doctor

Previous conversation context:"""

    # Add conversation history (last 10 messages for context)
    history = _conversations[conv_id][-10:]
    messages = [{"role": "system", "content": system_message}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    try:
        client = get_openai_client()

        # Build prompt from conversation history
        conversation_text = "\n".join([
            f"{m['role']}: {m['content']}" for m in history
        ])

        response_text = client.generate(
            prompt=request.message,
            system_message=f"{system_message}\n\n{conversation_text}",
            temperature=0.7,
            max_tokens=512,
        )

        # Add assistant response to history
        _conversations[conv_id].append({
            "role": "assistant",
            "content": response_text,
            "timestamp": time.time(),
        })

        return ChatMessageResponse(
            conversation_id=conv_id,
            response=response_text,
            safety_alert=safety_alert,
            safety_message=safety_message,
        )
    except Exception as e:
        logger.error(f"Chat message failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.get("/conversations")
async def list_conversations() -> list[ConversationSummary]:
    """List all active conversations."""
    summaries = []
    for conv_id, messages in _conversations.items():
        if messages:
            summaries.append(ConversationSummary(
                conversation_id=conv_id,
                message_count=len(messages),
                created_at=messages[0].get("timestamp", 0),
                last_message_at=messages[-1].get("timestamp", 0),
            ))
    return summaries


@router.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str) -> list[dict]:
    """Get full conversation history."""
    if conversation_id not in _conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return _conversations[conversation_id]


@router.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str) -> dict:
    """Delete a conversation."""
    if conversation_id not in _conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    del _conversations[conversation_id]
    return {"status": "deleted", "conversation_id": conversation_id}


@router.post("/conversation/{conversation_id}/summarize")
async def summarize_conversation(conversation_id: str) -> dict:
    """Generate a summary of the conversation for medical records."""
    if conversation_id not in _conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = _conversations[conversation_id]
    if not messages:
        return {"summary": "No messages in conversation"}

    try:
        client = get_openai_client()
        conversation_text = "\n".join([
            f"{m['role']}: {m['content']}" for m in messages
        ])

        prompt = f"""Summarize this medical chat conversation in 2-3 sentences, focusing on:
1. Main symptoms discussed
2. Key advice given
3. Any recommendations to see a doctor

Conversation:
{conversation_text}"""

        summary = client.generate(prompt, temperature=0.3, max_tokens=200)
        return {"summary": summary, "message_count": len(messages)}
    except Exception as e:
        logger.error(f"Conversation summarization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")
