import logging
import gradio as gr
from pathlib import Path
import workflow

from llama_index.utils.workflow import draw_all_possible_flows
from errors import RagProjectError, QueryError
from rag_service import RagService

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

rag_wf = workflow.RAGWorkflow(timeout=120)

# Draw static workflow
draw_all_possible_flows(
    rag_wf,
    filename=str(
        Path("workflow_visualizations/rag_workflow.html").resolve()
    ),
)

rag_service = RagService(rag_wf)


async def respond(message, history):
    try:
        return await rag_service.handle_query(message)

    except QueryError as e:
        return f"Error: {e}"

    except RagProjectError as e:
        return f"Error: {e}"

    except Exception as e:
        logger.exception("Unhandled workflow exception")
        return f"Unhandled error: {e}"


demo = gr.ChatInterface(
    fn=respond,
    title="RAG Chat with Event-Driven Workflow"
)


if __name__ == "__main__":
    try:
        demo.launch()
    except Exception as exc:
        logger.exception("Gradio launch failed")
        raise RagProjectError("Gradio failed to start.") from exc