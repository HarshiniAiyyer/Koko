from __future__ import annotations

from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse, EmotionalStateResponse
from app.core.emotion_engine import analyze_emotion
from app.core.personality_engine import apply_personality
from app.core.models import LLMClient

router = APIRouter()

# Initialize LLM client (lazy loaded)
llm_client = LLMClient()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint that processes user message through the full pipeline:
    1. Analyze emotion
    2. Generate neutral reply (LLM)
    3. Apply personality transformation
    
    Returns styled reply with emotional context and persona information.
    """
    try:
        # Step 1: Analyze emotion
        emotional_state = analyze_emotion(request.message)
        
        # Step 2: Generate neutral reply using LLM
        neutral_prompt = f"""You are a helpful AI assistant. Respond to this user message in a neutral, factual tone:

User: {request.message}

User: {request.message}

34: Provide a helpful, informative response without any specific personality or emotional coloring.
35: IMPORTANT: Keep your response extremely concise. Maximum 2-3 sentences. Do not ramble."""

        neutral_reply = llm_client.generate(
            user_prompt=neutral_prompt,
            system_prompt="You are a helpful assistant. Be extremely concise and informative.",
            temperature=0.3,
            max_tokens=256
        )
        
        # Step 3: Apply personality
        personality_result = apply_personality(
            neutral_reply=neutral_reply,
            emotional_state=emotional_state,
            requested_persona=request.requested_persona,
            llm_client=llm_client,
        )
        
        # Step 4: Build response
        return ChatResponse(
            reply=personality_result["after"],
            emotional_state=EmotionalStateResponse(
                state=emotional_state["state"],
                sentiment=emotional_state["sentiment"],
                emotion=emotional_state["emotion"],
                confidence=emotional_state["confidence"],
            ),
            persona_used=personality_result["persona_name"],
            reason=personality_result["reason"],
            neutral_reply=personality_result["before"],
        )
        
    except Exception as e:
        print(f"Chat Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")
