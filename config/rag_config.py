import ssl
import urllib3
import os
import certifi

ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
import os
from dotenv import load_dotenv
from pinecone import Pinecone
from llama_index.core import Settings, VectorStoreIndex, get_response_synthesizer
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.response_synthesizers import ResponseMode
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.groq import Groq
from llama_index.vector_stores.pinecone import PineconeVectorStore
from domain.errors import DataLoadError, RagProjectError

# Load environment variables
try:
    load_dotenv()
except Exception as exc:
    raise DataLoadError("Failed to load environment variables") from exc


try:
    Settings.embed_model = CohereEmbedding(
        api_key=os.getenv("COHERE_API_KEY"),
        model_name="embed-multilingual-v3.0"
    )

    Settings.llm = Groq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.9
    )

    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    llm = Settings.llm
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
except Exception as exc:
    raise RagProjectError("Failed to initialize RAG configuration") from exc


