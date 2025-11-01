# Bank Statement RAG Bot

A smart chatbot that analyzes your bank statements and provides insights on your transactions using AI. Built with Python, LangChain, OpenAI GPT models, and FAISS for efficient vector search.

---

## Features

- **PDF Extraction**: Automatically extracts transactions from bank statement PDFs
- **Smart Categorization**: Intelligently categorizes transactions (groceries, dining, fitness, shopping, etc.)
- **Semantic Search**: Find transactions using natural language queries
- **Powerful Aggregations**: Get totals, averages, and breakdowns by category/time period
- **AI Assistant**: Ask questions in plain English and get detailed insights
- **Dual Interfaces**: Command-line interface and interactive Streamlit web app
- **Docker Support**: Easy deployment with Docker and Docker Compose

---

## Prerequisites

- Python 3.10+
- OpenAI API key
- Bank statement PDFs
- Docker & Docker Compose (optional, for containerized deployment)

---

## Quick Start

### Local Setup

1. **Clone and setup**
   ```bash
   git clone <your-repo-url>
   cd bank-statement-rag
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure**
   Create `config.json`:
   ```json
   {
     "OPENAI_API_KEY": "your-openai-api-key-here",
     "DATA_DIR": "data/raw",
     "PROCESSED_DIR": "data/processed",
     "VECTORS_DIR": "data/vectors"
   }
   ```

3. **Add PDFs and run**
   ```bash
   # Place PDF statements in data/raw/
   
   # First time (extract and process PDFs)
   python cli.py --refresh
   
   # Interactive CLI
   python cli.py
   
   # Streamlit web interface
   streamlit run streamlit_app.py
   ```

### Docker Setup

1. **Create `.env` file**
   ```bash
   OPENAI_API_KEY=your-openai-api-key-here
   ```

2. **Run**
   ```bash
   docker compose up --build
   ```
   Access at [http://localhost:8501](http://localhost:8501)

---

## Usage

### Command-Line Interface

```bash
# Interactive chat
python cli.py

# Single query
python cli.py --query "How much did I spend on groceries last month?"

# Force refresh (re-extract PDFs)
python cli.py --refresh
```

### Streamlit Web Interface

```bash
streamlit run streamlit_app.py
```

Features:
- Dashboard with spending visualizations
- Interactive chat
- Category breakdowns
- Transaction browser
- Export to CSV/Excel

### Python API

```python
import json
from src.rag_system import BankStatementRAG

# Load config
with open('config.json') as f:
    config = json.load(f)

# Initialize
rag = BankStatementRAG(config)

# Ask questions
answer = rag.ask("What were my top 5 purchases this year?")
print(answer)

# Get statistics
stats = rag.get_stats()

# Access dataframe
df = rag.get_dataframe()
```

---

## Example Queries

- "How much did I spend on groceries last month?"
- "What were my top 5 largest purchases this year?"
- "Show me all Amazon transactions"
- "Give me a category breakdown for this month"
- "How much did I spend on dining last week?"
- "What's my average spending per day?"
- "Show me my gym membership payments"

---

## Project Structure

```
bank-statement-rag/
├── src/
│   ├── __init__.py
│   ├── extraction.py       # PDF extraction logic
│   ├── processing.py       # Data processing & categorization
│   ├── embeddings.py       # Vector store management
│   ├── query_engine.py     # Query handling
│   └── rag_system.py       # Main orchestrator
├── data/
│   ├── raw/               # Your PDF statements (place here)
│   ├── processed/         # Extracted CSV
│   └── vectors/           # FAISS vector store
├── cli.py                 # Command-line interface
├── streamlit_app.py       # Web interface
├── Dockerfile             
├── docker-compose.yaml    
├── requirements.txt       
├── config.json            
└── README.md             
```

---

## Customization

### Adding Categories

Edit `src/processing.py`:

```python
categories = {
    'your_category': ['keyword1', 'keyword2'],
    'groceries': ['grocery', 'instacart', 'safeway'],
    # ... add more
}
```

### Changing AI Model

Edit `src/rag_system.py`:

```python
llm = ChatOpenAI(
    model="gpt-4"  # Options: gpt-4, gpt-4o, gpt-4o-mini
)
```

### Custom PDF Format

If your statements have different format, modify `src/extraction.py` extraction logic.

---

## Troubleshooting

**No transactions found:**
- Ensure PDFs are in `data/raw/`
- Run `python cli.py --refresh`
- Check PDF format matches extraction logic

**Empty results:**
- Force refresh to re-categorize
- Check category keywords in `src/processing.py`

**Import errors:**
- Activate virtual environment
- Reinstall: `pip install -r requirements.txt`

**Docker issues:**
- Verify `.env` file exists with valid API key
- Rebuild: `docker compose up --build`

---

## Architecture

```
PDF Files → Extraction → Processing → Vector Store
                                    ↓
                              Structured Data
                                    ↓
                          Query Engine (Agent)
                                    ↓
                    ┌──────────────┴──────────────┐
                    ↓                              ↓
           Structured Query                Semantic Search
           (Aggregations)                  (Vector Similarity)
                    ↓                              ↓
                    └──────────────┬──────────────┘
                                   ↓
                            AI Response
```

---

## Security

- Never commit `config.json` or `.env` with real API keys
- Keep PDF statements in `data/raw/` (gitignored by default)
- Use environment variables for production
- Vector store is local (not sent to OpenAI)

---

## Acknowledgments

- **OpenAI** - GPT models and embeddings
- **LangChain** - RAG orchestration
- **FAISS** - Vector similarity search
- **pdfplumber** - PDF parsing
- **Streamlit** - Web UI

---

**Questions or issues?** Open an issue on GitHub or contact abdulrahmanadetsi@gmail.com