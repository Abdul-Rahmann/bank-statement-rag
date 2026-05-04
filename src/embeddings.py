"""Embeddings Module Creates and manages vector embeddings for semantic search """

import logging

from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

logger = logging.getLogger(__name__)


def create_semantic_documents(transactions_df):
    """
    Create rich, semantic documents for embedding. Each transaction becomes a detailed document.
    Uses vectorized operations instead of iterrows for better performance.
    """
    dates = transactions_df['Date']
    descriptions = transactions_df['Description']
    withdrawals = transactions_df['Withdrawals ($)']
    deposits = transactions_df['Deposits ($)']
    balances = transactions_df['Balance ($)']
    categories = transactions_df['Category']
    types = transactions_df['Type']
    months = transactions_df['Month']
    weeks = transactions_df['Week']
    years = transactions_df['Year']
    day_of_weeks = transactions_df['DayOfWeek']

    documents = []
    for date, desc, wd, dep, bal, cat, typ, mon, week, year, dow in zip(
        dates, descriptions, withdrawals, deposits, balances,
        categories, types, months, weeks, years, day_of_weeks
    ):
        amount = wd if wd > 0 else dep
        trans_type = 'spent' if wd > 0 else ('received' if dep > 0 else 'neutral')

        content = (
            f"Transaction on {date.strftime('%B %d, %Y')} ({dow}):\n"
            f"You {trans_type} ${amount:.2f} at {desc}.\n"
            f"Category: {cat}\n"
            f"Transaction Type: {typ}\n"
            f"Balance after transaction: ${bal:.2f}"
        )

        documents.append(Document(
            page_content=content,
            metadata={
                'date': date.strftime('%Y-%m-%d'),
                'description': desc,
                'amount': float(amount),
                'category': cat,
                'type': typ,
                'balance': float(bal),
                'month': str(mon),
                'week': str(week),
                'year': int(year),
                'day_of_week': dow
            }
        ))
    return documents

def create_vector_store(documents, openai_api_key, vector_store_path):
    """Create and save FAISS vector store."""
    logger.info("Creating vector embeddings for %d transactions...", len(documents))
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vectorstore = FAISS.from_documents(documents=documents, embedding=embeddings)
    vectorstore.save_local(vector_store_path)
    logger.info("Vector store saved to %s", vector_store_path)
    return vectorstore

def load_vector_store(openai_api_key, vector_store_path):
    """Load existing vector store."""
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    return FAISS.load_local(
        folder_path=vector_store_path,
        embeddings=embeddings,
        allow_dangerous_deserialization=True
    )

if __name__ == "__main__":
    ...
