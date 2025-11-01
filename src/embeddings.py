"""Embeddings Module Creates and manages vector embeddings for semantic search """

from langchain.docstore.document import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

def create_semantic_documents(transactions_df):
    """
    Create rich, semantic documents for embedding. Each transaction becomes a detailed document.
    """
    documents = []

    for idx, row in transactions_df.iterrows():
        amount = row['Withdrawals ($)'] if row['Withdrawals ($)'] > 0 else row['Deposits ($)']
        trans_type = 'spent' if row['Withdrawals ($)'] > 0 else 'received'

        # Create natural language description
        content = f"""
        Transaction on {row['Date'].strftime('%B %d, %Y')} ({row['DayOfWeek']}):
        You {trans_type} ${amount: .2f} at {row['Description']}.
        Category: {row['Category']}
        Transaction Type: {row['Type']}
        Balance after transaction: ${row['Balance ($)']: .2f}
        """

        documents.append(Document(
            page_content=content,
            metadata={
                'date': row['Date'].strftime('%Y-%m-%d'),
                'description': row['Description'],
                'amount': float(amount),
                'category': row['Category'],
                'type': row['Type'],
                'balance': float(row['Balance ($)']),
                'month': str(row['Month']),
                'week': str(row['Week']),
                'year': int(row['Year']),
                'day_of_week': row['DayOfWeek']
            }
        ))
    return documents

def create_vector_store(documents, openai_api_key, vector_store_path):
    """Create and save FAISS vector store."""
    print(f"\nCreating vector embeddings for {len(documents)} transactions...")
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vectorstore = FAISS.from_documents(documents=documents, embedding=embeddings)
    vectorstore.save_local(vector_store_path)
    print(f"   ✓ Vector store saved to {vector_store_path}")
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