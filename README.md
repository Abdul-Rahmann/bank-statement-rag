# Bank Statement RAG Bot

This project implements a Retrieval-Augmented Generation (RAG) chatbot that analyzes bank statements and provides insights on transactions. The pipeline uses Python, LangChain, OpenAI's GPT models, FAISS for vector similarity search, and Docker for containerized deployment.

---

## Features

- Ingests bank statement data from text files
- Embeds transaction data using OpenAI embeddings
- Stores embeddings in FAISS vector store for efficient retrieval
- Provides an interactive QA interface for transaction insights
- Deploys easily with Docker and Docker Compose

---

## Prerequisites

- Python 3.10+
- Docker & Docker Compose installed
- OpenAI API key (set in `.env` file)

---

## Setup

1. Clone the repository
2. Create a `.env` file with your OpenAI API key:
`OPENAI_API_KEY= openai_api_key`
3. Build and run with Docker Compose:
`docker compose up –build`
4. Access the app at [localhost:8501](http://localhost:8501) if using Streamlit UI, or interact via CLI.

---

## Usage

- Place your `bank_statement.txt` in the project directory.
- The container runs the pipeline, allowing you to ask questions about transactions and receive detailed insights.

---

## Project structure
`
├── app.py             # Main application script 
├── Dockerfile         # Docker build configuration 
├── docker-compose.yaml # Orchestrates container deployment 
├── .env               # Environment variables (API keys) └── bank_statement.txt # Your bank statement data
`

---

## License

This project is open source. Feel free to customize and extend it for your needs.

---

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for feature requests or bugs.

---

## Acknowledgments

- OpenAI for LLM and embedding services
- LangChain for orchestration
- FAISS for vector similarity search

---

This README provides a clear overview for others to set up, run, and extend your RAG pipeline. Would you like me to generate the `app.py` code or additional sections?




