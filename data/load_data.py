import logging
import os

from dotenv import load_dotenv

from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.core import SimpleDirectoryReader, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import StorageContext
from pinecone import Pinecone
import urllib3
from domain.errors import DataLoadError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

urllib3.disable_warnings()


def build_vector_index():
    try:
        load_dotenv()
        # 1️⃣ Load documents
        documents = SimpleDirectoryReader("docs").load_data()

        # 2️⃣ Split documents into chunks
        node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=20)
        nodes = node_parser.get_nodes_from_documents(
            documents,
            show_progress=True
        )

        # 3️⃣ Add metadata
        for node in nodes:
            file_name = node.metadata.get("file_name")
            node.metadata["file"] = file_name

        # 4️⃣ Configure Cohere embeddings
        Settings.embed_model = CohereEmbedding(
            api_key=os.getenv("COHERE_API_KEY"),
            model_name="embed-multilingual-v3.0"
        )

        # 5️⃣ Connect to Pinecone
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        pinecone_index = pc.Index("rag-index")

        vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store
        )

        # 6️⃣ Store vectors in Pinecone
        index = VectorStoreIndex(
            nodes,
            storage_context=storage_context
        )
        logger.info("Vector index built successfully.")
        return index
    except Exception as exc:
        logger.exception("Failed to build vector index")
        raise DataLoadError("Failed to build vector index") from exc


if __name__ == "__main__":
    try:
        build_vector_index()
    except Exception as exc:
        logger.exception("Error building index")

