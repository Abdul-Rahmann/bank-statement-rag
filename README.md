## Bank Statement RAG Bot

A smart chatbot that analyzes your bank statements and provides insights on your transactions using AI. Built with Python, LangChain, OpenAI GPT models, and FAISS for efficient vector search.

---

## Features

- **PDF Extraction**: Automatically extracts transactions from bank statement PDFs
- **Smart Categorization**: Intelligently categorizes transactions (groceries, dining, fitness, shopping, etc.)
- **Semantic Search**: Find transactions using natural language queries
- **Powerful Aggregations**: Get totals, averages, and breakdowns by category/time period
- **AI Assistant**: Ask questions in plain English and get detailed insights
- **Interactive Visualizations**: Dashboard with charts and graphs for spending patterns
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
   Create `config.yml`:
   ```yaml
   # Bank Statement RAG Configuration
   
   # Categories for transaction classification
   CATEGORIES:
     groceries: [grocery, instacart, safeway, walmart, superstore]
     dining: [restaurant, cafe, coffee, starbucks, tim hortons]
     shopping: [amazon, amzn, ebay, store, retail]
     transportation: [uber, lyft, gas, petro, shell, transit]
     utilities: [hydro, electric, water, internet, phone, rogers, bell]
     entertainment: [netflix, spotify, disney, cinema, theatre, game]
     health: [pharmacy, medical, dental, doctor, hospital, clinic]
     fitness: [gym, fitness, yoga, crossfit, membership, workout]
     office: [staples, office, supplies]
     transfer: [transfer, e-transfer, interac]
   
   # Data paths
   PATHS:
     DATA_DIR: data/raw
     VECTORS_DIR: data/vectors/vectorstore
     PROCESSED_DIR: data/processed
     TRANSACTIONS_CSV: data/processed/transactions.csv
   
   # API Keys (use environment variables)
   SECRETS:
     OPENAI_API_KEY: ${OPENAI_API_KEY}
   ```
   
   Create `.env` file (recommended for security):
   ```bash
   OPENAI_API_KEY=your-openai-api-key-here
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

2. **Create `config.yml`** (see Local Setup for full config)

3. **Place PDFs in data/raw/**
   ```bash
   mkdir -p data/raw
   cp /path/to/statements/*.pdf data/raw/
   ```

4. **Build and run**
   ```bash
   docker compose build
   docker compose up -d
   ```

5. **Access the app**
   - Streamlit: [http://localhost:8501](http://localhost:8501)
   - Logs: `docker compose logs -f`

**Useful Docker commands:**
```bash
# Stop
docker compose down

# Restart
docker compose restart

# Run CLI inside container
docker compose exec app python cli.py --query "Your question"

# Force refresh
docker compose exec app python cli.py --refresh
```

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

**Features:**
- **Dashboard Tab**: Visual overview with 4 interactive charts
  - Spending over time (daily/weekly/monthly/yearly)
  - Category breakdown pie chart
  - Top merchants bar chart
  - Transaction frequency heatmap
- **Chat Tab**: Interactive AI assistant for natural language queries
- **Transactions Tab**: Browse, filter, and export transactions
- **Settings Tab**: System configuration and data management

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

**General Spending:**
- "How much did I spend on groceries last month?"
- "What were my top 5 largest purchases this year?"
- "What's my average spending per day?"
- "Give me a category breakdown for this month"

**Specific Merchants:**
- "Show me all Amazon transactions"
- "How much did I spend at Starbucks?"
- "What's my Uber spending trend?"

**Comparisons:**
- "Compare my monthly spending"
- "How does this month compare to last month?"
- "Show me spending patterns over time"

**Category Analysis:**
- "How much on fitness last year?"
- "Show me my dining expenses"
- "What's my entertainment spending?"

---

## Project Structure

```
bank-statement-rag/
├── src/
│   ├── __init__.py
│   ├── extraction.py       # PDF extraction logic
│   ├── processing.py       # Data processing & categorization
│   ├── embeddings.py       # Vector store management
│   ├── query_engine.py     # Query handling (structured + semantic)
│   └── rag_system.py       # Main orchestrator
├── streamlit_app/
│   ├── __init__.py
│   ├── app.py              # Main Streamlit app
│   ├── config.py           # App configuration & styling
│   ├── charts.py           # Chart creation functions
│   ├── utils.py            # Helper functions
│   └── pages/
│       ├── dashboard.py    # Dashboard page
│       ├── chat.py         # Chat interface page
│       ├── transactions.py # Transaction browser page
│       └── settings.py     # Settings page
├── data/
│   ├── raw/               # Your PDF statements (place here)
│   ├── processed/         # Extracted CSV
│   └── vectors/           # FAISS vector store
├── cli.py                 # Command-line interface
├── streamlit_app.py       # Streamlit launcher
├── config.yml             # Configuration file (YAML)
├── .env                   # Environment variables (API keys)
├── Dockerfile             
├── docker-compose.yaml    
├── requirements.txt       
└── README.md             
```

---

## Customization

### Adding Categories

Categories are now configured in `config.yml`:

```yaml
CATEGORIES:
  your_category: [keyword1, keyword2, keyword3]
  groceries: [grocery, instacart, safeway, walmart]
  # ... add more
```

Simply add your custom category and keywords to the YAML file. The system will automatically use them for categorization.

**Example: Adding a "pets" category**
```yaml
CATEGORIES:
  pets: [petsmart, petco, vet, veterinary, pet food]
  groceries: [grocery, instacart, safeway]
  # ... other categories
```

No code changes needed - just update the config and run `python cli.py --refresh` to re-categorize transactions.

### Changing AI Model

Edit `src/rag_system.py`:

```python
llm = ChatOpenAI(
    model="gpt-4"  # Options: gpt-4, gpt-4o, gpt-4o-mini
)
```

### Custom PDF Format

If your statements have different format, modify the extraction logic in `src/extraction.py`:

```python
def extract_transactions_from_page(lines, extracted_year):
    # Customize based on your PDF structure
    # Adjust regex patterns and parsing logic
    ...
```

### Changing Data Paths

Update paths in `config.yml`:

```yaml
PATHS:
  DATA_DIR: custom/path/to/pdfs
  VECTORS_DIR: custom/path/to/vectors
  PROCESSED_DIR: custom/path/to/processed
  TRANSACTIONS_CSV: custom/path/to/transactions.csv
```

### Adding Chart Types

Edit `streamlit_app/charts.py` to add new visualization functions:

```python
def create_your_custom_chart(df):
    # Create your custom Plotly chart
    fig = go.Figure()
    # ... add traces
    return fig
```

---

## Troubleshooting

**No transactions found:**
- Ensure PDFs are in `data/raw/`
- Run `python cli.py --refresh`
- Check PDF format matches extraction logic in `src/extraction.py`

**Config file errors:**
- Ensure `config.yml` exists in root directory
- Check YAML syntax (no tabs, proper indentation)
- Verify environment variables in `.env` file
- Test with: `python -c "from src.config import get_config; print(get_config())"`

**Empty results:**
- Force refresh to re-categorize: `python cli.py --refresh`
- Check category keywords in `config.yml` under `CATEGORIES`
- Add missing merchants to relevant categories
- Verify transactions are being extracted correctly

**Import errors:**
- Activate virtual environment: `source venv/bin/activate`
- Reinstall: `pip install -r requirements.txt`
- Ensure Python 3.10+ is being used

**Docker issues:**
- Verify `.env` file exists with valid API key
- Rebuild containers: `docker compose up --build`
- Check Docker logs: `docker compose logs`

**Streamlit errors:**
- Make sure you're running from project root
- Clear Streamlit cache: `streamlit cache clear`
- Check browser console for JavaScript errors

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

### How It Works

1. **Extraction**: PDFs are parsed and transactions are extracted into structured data
2. **Processing**: Transactions are cleaned, categorized, and enriched with metadata
3. **Embedding**: Transaction descriptions are converted to vector embeddings for semantic search
4. **Query**: User queries are processed by an AI agent that intelligently decides:
   - Use structured queries for aggregations (totals, averages, counts)
   - Use semantic search for finding specific transactions by description
5. **Response**: Detailed text answers with relevant transaction details

### Components

- **Extraction Layer**: Parses PDF statements into structured data
- **Processing Layer**: Cleans, categorizes, and enriches transactions
- **Embedding Layer**: Creates vector representations for semantic search
- **Query Layer**: Handles both structured and semantic queries
- **Interface Layer**: Modular Streamlit web app and CLI

---

## Technologies Used

- **Python 3.11**: Core programming language
- **LangChain**: RAG orchestration and agent framework
- **OpenAI GPT-4**: Language model for natural language understanding
- **FAISS**: Fast vector similarity search
- **pdfplumber**: Robust PDF text extraction
- **Streamlit**: Interactive web interface
- **Plotly**: Interactive data visualizations
- **Pandas**: Data manipulation and analysis
- **Docker**: Containerized deployment

---

## Security Best Practices

- Never commit `config.json` or `.env` with real API keys
- Keep PDF statements in `data/raw/` (gitignored by default)
- Use environment variables for production deployments
- Vector store data is stored locally (not sent to OpenAI)
- Sensitive transaction data stays on your machine
- Regularly update dependencies for security patches

---

## Performance

- **Extraction**: ~100-200 transactions/second
- **Vector Store**: Sub-100ms similarity search
- **Query Response**: 1-3 seconds (depends on LLM and complexity)
- **Chart Rendering**: <200ms per chart
- **Storage**: ~1MB per 1000 transactions

---

## Roadmap

Future enhancements planned:
- Budget tracking and alerts
- Spending predictions using ML
- Multi-account support
- Receipt attachment support
- Mobile app interface
- Scheduled email reports
- Recurring transaction detection
- Anomaly detection for unusual spending
- Bank API integration for auto-sync

---

## Acknowledgments

- **OpenAI** - GPT models and embeddings
- **LangChain** - RAG orchestration framework
- **FAISS** - Vector similarity search
- **pdfplumber** - PDF parsing
- **Streamlit** - Rapid web UI development
- **Plotly** - Interactive visualizations

---

## Contributing

Contributions are welcome! Areas where you can help:
- Support for different bank statement formats
- Additional categorization rules
- New visualization types
- Performance optimizations
- Documentation improvements
- Bug fixes

---

## License

This project is open source under the MIT License.

---

**Questions or issues?** Open an issue on GitHub or contact abdulrahmanadetsi@gmail.com


[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)  