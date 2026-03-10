import os
import urllib3
from dotenv import load_dotenv
from pinecone import Pinecone
from llama_index.core import Settings, VectorStoreIndex, get_response_synthesizer
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.response_synthesizers import ResponseMode
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.groq import Groq
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import PydanticSingleSelector
from llama_index.core.tools import QueryEngineTool
from llama_index.core.query_engine import CustomQueryEngine
import json

urllib3.disable_warnings()

load_dotenv()

STRUCTURED_DATA = json.loads(
    open("structured_data.json", encoding="utf-8").read()
)

Settings.embed_model = CohereEmbedding(
    api_key=os.getenv("COHERE_API_KEY"),
    model_name="embed-multilingual-v3.0"
)

Settings.llm = Groq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.9
)

llm = Settings.llm

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
pinecone_index = pc.Index("rag-index")

vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store
)


retriever = index.as_retriever(similarity_top_k=5)

postprocessor = SimilarityPostprocessor(similarity_cutoff=0.30)

response_synthesizer = get_response_synthesizer(
    response_mode=ResponseMode.COMPACT
)

class StructuredJSONQueryEngine(CustomQueryEngine):
    def custom_query(self, query_str: str):
        data = STRUCTURED_DATA
        prompt = f"""
        You are an assistant that answers questions using structured project data.

        The data contains these sections:
        - decisions: architecture or design decisions
        - rules: system rules or constraints
        - warnings: potential issues or risks
        - dependencies: relationships between components

        Structured data:
        {json.dumps(data, indent=2, ensure_ascii=False)}

        User question:
        {query_str}

        Instructions:
        - Only use the information from the structured data.
        - If the answer is not in the data, say that the information is not available.
        - Be concise and clear.
        """
        response = llm.complete(prompt)
        return str(response)

list_tool = QueryEngineTool.from_defaults(
    query_engine=StructuredJSONQueryEngine(),
    description="Useful for summarization questions about decisions, rules, warnings, and dependencies",
)

class SemanticRoutingEngine(CustomQueryEngine):
    def custom_query(self, query_str: str):
        return "semantic"

semantic_tool = QueryEngineTool.from_defaults(
    query_engine=SemanticRoutingEngine(),
    description="Useful for retrieving specific context about code, architecture, and documentation",
)

router_query_engine = RouterQueryEngine(
    selector=PydanticSingleSelector.from_defaults(),
    query_engine_tools=[list_tool, semantic_tool],
)