# Chatbot-Lux Data Format Documentation

This document describes the JSON data structures used by Chatbot-Lux.

## Knowledge Base Files

### Structure
Knowledge base files contain question-answer pairs with metadata:

```json
[
  {
    "q": "What is Python?",
    "a": "Python is a high-level programming language.",
    "learned_at": "2024-01-15 10:30:45",
    "source": "knowledge_base.json"
  },
  {
    "q": "How do I install Python?",
    "a": "Visit python.org and download the latest version.",
    "learned_at": "2024-01-16 14:22:10",
    "source": "knowledge_base.json"
  }
]
```

### Field Descriptions

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `q` | string | The question or query text | ✅ |
| `a` | string | The chatbot's answer to the question | ✅ |
| `learned_at` | string | ISO 8601 timestamp when the answer was learned (YYYY-MM-DD HH:MM:SS) | ✅ |
| `source` | string | The filename where this entry is stored | ✅ |

## Statistics File (`stats_file.json`)

Tracks chatbot learning and performance metrics.

### Structure
```json
{
  "total_questions": 42,
  "relevant_answers": 38,
  "irrelevant_answers": 4,
  "new_learnings": 5,
  "history": [
    {
      "q": "What is AI?",
      "rating": 9,
      "relevant": true
    },
    {
      "q": "Explain machine learning",
      "ancienne_reponse": "Old answer text",
      "rating": 3,
      "amelioration": true
    }
  ]
}
```

### Field Descriptions

#### Top Level
| Field | Type | Description |
|-------|------|-------------|
| `total_questions` | integer | Total number of questions processed |
| `relevant_answers` | integer | Number of questions answered successfully |
| `irrelevant_answers` | integer | Number of questions not answered (unknown) |
| `new_learnings` | integer | Number of new Q&A pairs learned |
| `history` | array | List of user feedback records |

#### History Entry (Good Answer)
| Field | Type | Description |
|-------|------|-------------|
| `q` | string | The question |
| `rating` | integer | User's rating (1-10, >8 = positive) |
| `relevant` | boolean | Whether answer was relevant (true for rating >= 8) |

#### History Entry (Answer Correction)
| Field | Type | Description |
|-------|------|-------------|
| `q` | string | The question |
| `ancienne_reponse` | string | The previous incorrect answer |
| `rating` | integer | User's rating (<5 = negative) |
| `amelioration` | boolean | Whether user provided corrected answer (always true) |

## Configuration File (`config.py`)

Contains tunable parameters for the chatbot behavior. See config.py for all settings.

### Key Parameters
- `AUTO_SAVE_INTERVAL`: Save after every N questions
- `FUZZY_MATCH_THRESHOLD_LEARN_MODE`: Fuzzy match sensitivity in learn mode (0-1)
- `FUZZY_MATCH_THRESHOLD_NORMAL_MODE`: Fuzzy match sensitivity in normal mode (0-1)
- `RATING_THRESHOLD_GOOD`: Rating threshold for positive feedback (≥8 default)
- `RATING_THRESHOLD_BAD`: Rating threshold for negative feedback (<5 default)

## File Organization

### Typical Project Structure
```
chatbot-lux/
├── lux_chatbot.py          # Main application
├── config.py               # Configuration constants
├── knowledge_base.json     # Primary knowledge base (read/write)
├── personality.json        # Personality traits (read-only)
├── facts.json              # Additional facts (read-only)
├── stats_file.json         # Statistics (auto-generated)
├── README.md               # User documentation
└── DATA_FORMAT.md          # This file
```

### Loading Priority
Files are loaded in the order specified to `IntelligentChatbot()`. Later files override earlier ones for duplicate questions.

### Auto-Save Behavior
- Only the **first file** in the list is written to during learning
- Other files are read-only (reference knowledge)
- Statistics are always saved to `stats_file.json`

## Data Validation Rules

### Knowledge Base Entries
- `q` (question): Non-empty string, max 500 characters recommended
- `a` (answer): Non-empty string, max 2000 characters recommended
- `learned_at`: Must be valid ISO 8601 format (YYYY-MM-DD HH:MM:SS)
- `source`: Must match one of the loaded knowledge files

### Statistics
- All numeric fields must be non-negative integers
- Timestamps in history follow same format as knowledge entries
- Rating values must be between 1-10

## Examples

### Adding a New Q&A Pair
When using `--learn` mode and teaching a new answer:
1. User asks an unknown question
2. Chatbot asks for the answer
3. New entry is created with current timestamp
4. Entry is appended to primary knowledge file
5. Stats `new_learnings` counter is incremented

### Rating an Answer
After chatbot provides an answer:
1. Score is calculated (0.0 = no match, 1.0 = exact match)
2. If score < 0.8 in learn mode, user is asked to rate (1-10)
3. If rating < 5: User corrects the answer, `amelioration` flag set
4. If rating >= 8: Feedback recorded as relevant
5. History entry is added to stats file
