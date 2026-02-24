"""Configuration module for Chatbot-Lux application."""

# File paths
STATS_FILE = "stats_file.json"
DEFAULT_KNOWLEDGE_FILES = ["knowledge_base.json", "personality.json", "facts.json"]

# Learning and matching parameters
AUTO_SAVE_INTERVAL = 5  # Number of questions between auto-saves
EXACT_MATCH_THRESHOLD = 1.0  # Score for exact question matches

# Fuzzy matching thresholds
FUZZY_MATCH_THRESHOLD_LEARN_MODE = 0.5  # More permissive in learning mode
FUZZY_MATCH_THRESHOLD_NORMAL_MODE = 0.7  # Standard mode threshold

# Rating thresholds
RATING_THRESHOLD_GOOD = 8  # Rating above this indicates good answer
RATING_THRESHOLD_BAD = 5  # Rating below this indicates bad answer
FEEDBACK_SCORE_THRESHOLD = 0.8  # Score threshold to request feedback in learn mode

# Display options
ENABLE_AUTO_SAVE_MESSAGES = True  # Show "Auto_save" messages in console
