# Chatbot-Lux 🤖

A locally-hosted intelligent chatbot created with Python that learns from user interactions and improves its responses over time.

## Features

- **Local-First Design**: Runs entirely on your machine, no cloud dependency
- **Learning Capability**: Learn new questions and answers in real-time via `--learn` mode
- **Fuzzy Matching**: Intelligent question matching for similar queries
- **Auto-Save**: Automatically saves knowledge and statistics at configurable intervals
- **Statistics Tracking**: Monitor chatbot performance and learning progress
- **Multi-Source Knowledge**: Load knowledge from multiple JSON files
- **Rating System**: Users can rate answers to improve future responses

## Quick Start

### Installation

1. **Clone or download this project**

2. **Install dependencies** (Python 3.8+):
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the chatbot**:
   ```bash
   # Normal mode
   python lux_chatbot.py
   
   # Learning mode (can teach new answers)
   python lux_chatbot.py --learn
   ```

## Usage Guide

### Normal Mode
In normal mode, the chatbot answers questions based on its knowledge base:

```bash
python lux_chatbot.py
```

```
🤖 CHATBOT INTELLIGENT
==============================================================
💬 MODE NORMAL
   Utilisez --learn au lancement pour activer le mode apprentissage

🧑 Vous : What is Python?
🤖 Chatbot : Python is a high-level programming language.
```

### Learning Mode
In learning mode, you can teach the chatbot new information:

```bash
python lux_chatbot.py --learn
```

When the chatbot doesn't know an answer:
```
🤖 Chatbot : Je ne sais pas répondre à cette question.
   🌟 Mode apprentissage : Enseignez-moi la réponse !
   Quelle devrait être la réponse ? : Python is awesome!
   ✅ J'ai appris cette nouvelle information !
```

You can also rate answers to help improve responses:
```
📊 Score de pertinence : 0.75
🔍 Mode apprentissage actif - Aidez-moi à m'améliorer !
   Notez la pertinence de cette réponse (1-10) : 6
   🤔 Désolé ! Pouvez-vous me donner la bonne réponse ?
```

## Special Commands

Use these commands during chatbot interaction:

| Command | Description |
|---------|-------------|
| `/stats` | Display learning statistics |
| `/count` | Show number of questions processed |
| `/sources` | List loaded knowledge files and entry counts |
| `/save` | Manually save knowledge and statistics |
| `/quit` | Exit the chatbot and show final stats |

Example:
```
🧑 Vous : /stats
📈 STATISTIQUES D'APPRENTISSAGE
==============================================================
📊 Questions totales : 42
✅ Réponses pertinentes : 38
❌ Réponses non pertinentes : 4
🎯 Taux de pertinence : 90.5%
📚 Nouveaux apprentissages : 5
📁 Base de connaissances : 18 entrées
==============================================================
```

## Project Structure

```
chatbot-lux/
├── lux_chatbot.py          # Main chatbot application
├── config.py               # Configuration constants
├── knowledge_base.json     # Primary knowledge base (read/write)
├── personality.json        # Personality traits (read-only)
├── facts.json              # Additional facts (read-only)
├── stats_file.json         # Statistics (auto-generated)
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── DATA_FORMAT.md          # JSON data structure documentation
└── LICENSE                 # MIT License
```

## Data Files

### knowledge_base.json
The primary knowledge base file. Questions and answers are stored as JSON entries:

```json
[
  {
    "q": "What is Python?",
    "a": "Python is a high-level programming language.",
    "learned_at": "2024-01-15 10:30:45",
    "source": "knowledge_base.json"
  }
]
```

See [DATA_FORMAT.md](DATA_FORMAT.md) for complete schema documentation.

### personality.json & facts.json
Additional knowledge files that are loaded read-only. They provide supplementary information without being modified during learning.

### stats_file.json
Auto-generated file tracking:
- Total questions processed
- Successful vs. failed answers
- Learning history
- User feedback

## Configuration

Edit `config.py` to customize chatbot behavior:

```python
AUTO_SAVE_INTERVAL = 5  # Save after every 5 questions
FUZZY_MATCH_THRESHOLD_LEARN_MODE = 0.5  # More lenient matching
FUZZY_MATCH_THRESHOLD_NORMAL_MODE = 0.7  # Standard matching
RATING_THRESHOLD_GOOD = 8  # Rating >= 8 is positive feedback
RATING_THRESHOLD_BAD = 5  # Rating < 5 triggers correction
```

See [config.py](config.py) for all available options.

## How It Works

### Question Matching
1. **Exact Match**: Checks for identical questions (100% score)
2. **Fuzzy Match**: Uses difflib to find similar questions based on thresholds
3. **Not Found**: If no match exceeds threshold, returns "I don't know"

### Learning Process
1. User asks unknown question
2. Chatbot requests the correct answer
3. New Q&A pair is added to primary knowledge file
4. Answer is associated with source file and timestamp
5. Statistics are updated

### Feedback Loop
1. User rates chatbot's answer (1-10)
2. If rating < 5: User provides correction
3. If rating >= 8: Feedback recorded as relevant
4. History is saved for analysis

## Performance Characteristics

- **Startup Time**: ~100ms (loads all knowledge files)
- **Query Time**: ~50-100ms for most questions
- **Memory Usage**: < 10MB for typical knowledge bases
- **Scalability**: Tested with 100+ Q&A pairs

For optimal performance with large knowledge bases (1000+), consider using RapidFuzz (already in requirements.txt).

## Troubleshooting

### Knowledge not being saved
- Ensure you have write permission in the project directory
- Check that `knowledge_base.json` is writable
- Use `/save` command to manually save

### Fuzzy matching too strict/lenient
- Adjust thresholds in `config.py`
- `FUZZY_MATCH_THRESHOLD_LEARN_MODE`: Lower = more matches
- `FUZZY_MATCH_THRESHOLD_NORMAL_MODE`: Lower = more matches

### File format errors
- Check that JSON files are valid (use JSON validator online)
- Ensure all required fields are present (see DATA_FORMAT.md)
- Look for non-UTF-8 characters

## Development

### Adding Features
1. Extend the `IntelligentChatbot` class
2. Add new configuration constants to `config.py`
3. Document changes in relevant markdown files

### Running Tests
Currently no automated tests. Consider adding:
- Unit tests for fuzzy matching
- Integration tests for save/load functionality
- Performance benchmarks

### Contributing
Improvements welcome! Areas for enhancement:
- Performance optimization for large knowledge bases
- Better NLP/semantic matching
- Multi-language support
- Web interface
- Database backend

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Language Support

Currently optimized for French and English. Easily adaptable to other languages by translating:
- Console output messages
- Prompt strings
- Documentation

## Changelog

### v1.0.0 (Current)
- Initial release
- Learning mode with user feedback
- Multi-file knowledge base support
- Statistics tracking
- Auto-save functionality
- Performance optimizations with type hints

## Future Roadmap

- [ ] Web UI interface
- [ ] Advanced NLP using transformers
- [ ] Semantic similarity matching
- [ ] Database backend (SQLite/PostgreSQL)
- [ ] API endpoint
- [ ] Conversation history
- [ ] User context awareness
- [ ] Multi-language support

## Getting Help

- Review [DATA_FORMAT.md](DATA_FORMAT.md) for data structure questions
- Check [config.py](config.py) for configuration options
- See comments in [lux_chatbot.py](lux_chatbot.py) for code documentation
