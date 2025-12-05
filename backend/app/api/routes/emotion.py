from __future__ import annotations

"""
Emotion Analysis Endpoint

Uses the same HuggingFace transformer models as defined in EmotionModel:
- distilbert-base-uncased-finetuned-sst-2-english (sentiment analysis)
- j-hartmann/emotion-english-distilroberta-base (emotion classification)

These models are accessed via HuggingFace Inference API instead of local loading
for faster cold-start performance. The EmotionModel class in 
app/core/models/emotion_model.py contains the local pipeline version.
"""

import httpx
from fastapi import APIRouter
from app.models.emotion import EmotionAnalyzeRequest, EmotionAnalyzeResponse
from app.core.config.settings import settings

router = APIRouter()

# HuggingFace Inference API configuration
# Uses the SAME models as EmotionModel in app/core/models/emotion_model.py
HF_API_TOKEN = settings.HF_API_TOKEN or ""
# New HuggingFace API endpoint (old api-inference.huggingface.co is deprecated)
HF_API_URL = "https://router.huggingface.co/hf-inference/models"

# Model IDs - matching those in EmotionModel class
SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"  # Same as EmotionModel.sentiment_pipe
EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"       # Same as EmotionModel.emotion_pipe


async def query_huggingface(model_id: str, text: str) -> dict:
    """
    Query HuggingFace Inference API for a specific model.
    
    Uses the same models as the local EmotionModel class but via API.
    """
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"} if HF_API_TOKEN else {}
    
    print(f"[HF API] Querying model: {model_id}")
    print(f"[HF API] Token present: {bool(HF_API_TOKEN)}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{HF_API_URL}/{model_id}",
                headers=headers,
                json={"inputs": text}
            )
            print(f"[HF API] Response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"[HF API] Error response: {response.text}")
                
            response.raise_for_status()
            result = response.json()
            print(f"[HF API] Result: {result}")
            return result
        except Exception as e:
            print(f"[HF API] Exception: {type(e).__name__}: {e}")
            raise


def extract_top_result(api_result: list) -> tuple[str, float]:
    """Extract the top label and score from HuggingFace API response."""
    if not api_result:
        return "neutral", 0.5
    
    # Handle nested list format [[{label, score}, ...]]
    if isinstance(api_result[0], list):
        results = api_result[0]
    else:
        results = api_result
    
    if not results:
        return "neutral", 0.5
        
    top = max(results, key=lambda x: x.get("score", 0))
    return top.get("label", "neutral").lower(), float(top.get("score", 0.5))


def estimate_emotional_state(sentiment: str, emotion: str) -> str:
    """
    Combine sentiment and emotion into a simplified emotional state.
    
    This mirrors the logic in EmotionModel.estimate_state() for consistency.
    """
    if sentiment == "negative" and emotion in {"fear", "sadness", "disgust"}:
        return "stressed"
    elif sentiment == "negative" and emotion == "anger":
        return "frustrated"
    elif sentiment == "positive" and emotion == "joy":
        return "excited"
    elif emotion == "surprise":
        return "surprised"
    else:
        return "neutral"


async def analyze_with_inference_api(text: str) -> dict:
    """
    Analyze emotion using HuggingFace Inference API.
    
    Uses:
    - distilbert-base-uncased-finetuned-sst-2-english for sentiment
    - j-hartmann/emotion-english-distilroberta-base for emotion
    
    These are the same models defined in EmotionModel class.
    """
    try:
        # Step 1: Get sentiment using distilbert
        sentiment_result = await query_huggingface(SENTIMENT_MODEL, text)
        sentiment_label, sentiment_score = extract_top_result(sentiment_result)
        
        # Step 2: Get emotion using emotion-english-distilroberta
        emotion_result = await query_huggingface(EMOTION_MODEL, text)
        emotion_label, emotion_score = extract_top_result(emotion_result)
        
        # Step 3: Estimate state (same logic as EmotionModel.estimate_state)
        state = estimate_emotional_state(sentiment_label, emotion_label)
        
        return {
            "state": state,
            "sentiment": sentiment_label,
            "emotion": emotion_label,
            "confidence": emotion_score,
        }
        
    except Exception as e:
        print(f"HuggingFace API error: {e}")
        # Return neutral on error - user should check API token
        return {
            "state": "neutral",
            "sentiment": "neutral",
            "emotion": "neutral",
            "confidence": 0.5,
        }


@router.post("/emotion/analyze", response_model=EmotionAnalyzeResponse)
async def analyze_emotion_endpoint(request: EmotionAnalyzeRequest):
    """
    Analyze the emotional state of a given text.
    
    Uses HuggingFace transformer models via Inference API:
    - distilbert-base-uncased-finetuned-sst-2-english (sentiment)
    - j-hartmann/emotion-english-distilroberta-base (emotion)
    
    Returns:
    - Emotional state (stressed, excited, neutral, frustrated, surprised)
    - Sentiment (positive, negative, neutral)
    - Primary emotion (joy, fear, anger, sadness, surprise, disgust, neutral)
    - Confidence score
    
    Note: Set HF_API_TOKEN in .env for faster response times.
    """
    result = await analyze_with_inference_api(request.text)
    
    return EmotionAnalyzeResponse(
        state=result["state"],
        sentiment=result["sentiment"],
        emotion=result["emotion"],
        confidence=result["confidence"],
    )
