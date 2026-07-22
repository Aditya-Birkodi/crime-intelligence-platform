"""ETL stage: document_builder.

Builds RAG documents for Catalyst NoSQL + QuickML (see docs/ai/rag_document_schema.md).
"""

from etl.document_builder.pipeline import DocumentBuilderPipeline, build_rag_text_blob

__all__ = ["DocumentBuilderPipeline", "build_rag_text_blob"]
