"""
RAG System Module
Main orchestrator that ties everything together
"""

import os
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from .extraction import extract_all_pdfs
from .processing import process_transactions, get_summary_stats
from .embeddings import create_semantic_documents, create_vector_store, load_vector_store
from .query_engine import query_structured_data, semantic_search

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'


class BankStatementRAG:
    """Complete RAG system for bank statements."""

    def __init__(self, config, force_refresh=False):
        """
        Initialize the RAG system.

        Args:
        config: Dictionary with configuration(paths, API keys)
        force_refresh: If True, re - extract PDFs and rebuild vector store
        """
        self.config = config
        self.openai_api_key = config['SECRETS'].get('OPENAI_API_KEY')
        self.pdf_dir = config['PATHS'].get('DATA_DIR')
        self.processed_dir = config['PATHS'].get('PROCESSED_DIR')
        self.vector_store_path = config['PATHS'].get('VECTORS_DIR')
        self.transactions_csv = config['PATHS'].get('TRANSACTIONS_CSV')

        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.vector_store_path, exist_ok=True)

        self.transactions_df = None
        self.vectorstore = None
        self.agent = None

        self._initialize(force_refresh)


    def _initialize(self, force_refresh):
        """Initialize all components."""
        # Check if we need to extract/process
        csv_exists = os.path.exists(self.transactions_csv)
        csv_has_data = False

        if csv_exists:
            try:
                temp_df = pd.read_csv(self.transactions_csv)
                csv_has_data = len(temp_df) > 0
            except:
                csv_has_data = False

        needs_extraction = force_refresh or not csv_has_data
        needs_vectors = force_refresh or not os.path.exists(
            os.path.join(self.vector_store_path, 'index.faiss')
        )

        if needs_extraction:
            print("Starting fresh extraction from PDFs...")
            self._extract_and_process()
        else:
            print("Loading existing transactions...")
            self.transactions_df = pd.read_csv(self.transactions_csv)
            self.transactions_df = process_transactions(self.transactions_df)
            print(f"   ✓ Loaded {len(self.transactions_df)} transactions")

        # Check if we have data
        if len(self.transactions_df) == 0:
            print("\n  WARNING: No transactions found!")
            print(f"   Make sure your PDF files are in: {self.pdf_dir}")
            print("   Force refresh with: BankStatementRAG(config, force_refresh=True)")
            return

        if needs_vectors:
            print("Building vector store...")
            self._build_vector_store()
        else:
            print("Loading existing vector store...")
            self.vectorstore = load_vector_store(
                self.openai_api_key,
                self.vector_store_path
            )
            print("   ✓ Vector store loaded")

        # Setup agent
        self._setup_agent()
        print("\nRAG system ready!\n")


    def _extract_and_process(self):
        """Extract PDFs and process transactions."""
        raw_df = extract_all_pdfs(self.pdf_dir)
        print(f"\n✓ Total transactions extracted: {len(raw_df)}")

        self.transactions_df = process_transactions(raw_df)
        self.transactions_df.to_csv(self.transactions_csv, index=False)
        print(f"✓ Processed transactions saved to {self.transactions_csv}")


    def _build_vector_store(self):
        """Build and save vector store."""
        documents = create_semantic_documents(self.transactions_df)
        self.vectorstore = create_vector_store(
            documents,
            self.openai_api_key,
            self.vector_store_path
        )


    def _setup_agent(self):
        """Setup the LangChain agent with tools."""

        def structured_query_tool(query: str) -> str:
            return query_structured_data(query, self.transactions_df)

        def semantic_search_tool(query: str) -> str:
            return semantic_search(self.vectorstore, query)

        tools = [
            Tool(
                name="StructuredQuery",
                func=structured_query_tool,
                description="Use this for queries about totals, sums, averages, counts, breakdowns, or any aggregation. Also use for time-based queries like 'last week', 'this month', or category queries."
            ),
            Tool(
                name="SemanticSearch",
                func=semantic_search_tool,
                description="Use this to find specific transactions by merchant name, description, or when looking for particular types of purchases."
            )
        ]

        llm = ChatOpenAI(
            temperature=0,
            openai_api_key=self.openai_api_key,
            model="gpt-4o-mini"
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful financial assistant analyzing bank transactions.
    
            You have access to two powerful tools:
            1. StructuredQuery: For calculations, aggregations, summaries, and filtering
            2. SemanticSearch: For finding specific transactions by merchant or description
    
            Guidelines:
            - Use StructuredQuery for "how much", "total", "sum", "average", "breakdown", time periods, or categories
            - Use SemanticSearch for finding specific merchants or transaction details
            - Always provide clear, formatted answers with dollar amounts and dates
            - Be conversational and helpful
            - Use emojis to make responses engaging"""),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_functions_agent(llm, tools, prompt)
        self.agent = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=False,
            handle_parsing_errors=True
        )


    def ask(self, question: str) -> str:
        """Ask a question about your bank transactions."""
        if self.agent is None:
            return " System not initialized. No transaction data available."

        result = self.agent.invoke({"input": question})
        return result['output']


    def get_stats(self):
        """Get summary statistics."""
        return get_summary_stats(self.transactions_df)


    def get_dataframe(self):
        """Get the raw transactions dataframe."""
        return self.transactions_df


if __name__ == "__main__":
    ...
