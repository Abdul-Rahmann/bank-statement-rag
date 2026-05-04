"""Tests for src/embeddings.py."""

from src.embeddings import create_semantic_documents
from src.processing import process_transactions


class TestCreateSemanticDocuments:
    def test_creates_documents(self, sample_transactions_df):
        df = process_transactions(sample_transactions_df)
        docs = create_semantic_documents(df)
        assert len(docs) == len(df)

    def test_document_has_metadata(self, sample_transactions_df):
        df = process_transactions(sample_transactions_df)
        docs = create_semantic_documents(df)
        doc = docs[0]
        assert "date" in doc.metadata
        assert "description" in doc.metadata
        assert "amount" in doc.metadata
        assert "category" in doc.metadata

    def test_document_content_includes_description(self, sample_transactions_df):
        df = process_transactions(sample_transactions_df)
        docs = create_semantic_documents(df)
        # DataFrame is sorted by date descending, find the doc for first original row
        first_desc = sample_transactions_df.iloc[0]["Description"]
        assert any(first_desc in doc.page_content for doc in docs)
