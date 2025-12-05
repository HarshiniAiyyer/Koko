# ----------------------------------------------
# Constants shared across memory, emotion, and personality engines
# ----------------------------------------------

# --- Memory Tiers ---
MEMORY_TIERS = {
    "surface": "facts_and_preferences",
    "pattern": "behavioral_patterns",
    "deep": "emotional_core",
}

# --- Confidence Levels ---
CONFIDENCE_LEVELS = ["high", "medium", "low"]

# --- Emotion Labels ---
# Based on common open-source emotion classifiers
EMOTIONS = [
    "joy",
    "sadness",
    "anger",
    "fear",
    "surprise",
    "disgust",
    "neutral",
]

# --- Personality Axes ---
PERSONALITY_AXES = [
    "warmth",
    "energy",
    "formality",
    "directness",
    "humor",
    "depth",
]

# --- Persona Profiles (names only) ---
PERSONA_PROFILES = [
    "calm_mentor",
    "witty_friend",
    "therapist",
]
