"""Custom exception types for the RAG project."""

class RagProjectError(Exception):
    """Base custom exception for RAG project domain errors."""
    pass


class DataLoadError(RagProjectError):
    """Raised when structured data or vector store loading fails."""
    pass


class WorkflowError(RagProjectError):
    """Raised during workflow execution errors."""
    pass


class QueryError(RagProjectError):
    """Raised for invalid user queries."""
    pass
