import logging

import gradio as gr
from pathlib import Path
import workflow

from llama_index.utils.workflow import draw_all_possible_flows, draw_most_recent_execution
from errors import RagProjectError, QueryError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Create workflow
rag_wf = workflow.RAGWorkflow(timeout=120)
draw_all_possible_flows(
    rag_wf,
    filename=str(
        Path("workflow_visualizations/rag_workflow.html").resolve()
    ),
)

# Gradio response with exception handling
async def respond(message, history):
    try:
        if not message or not str(message).strip():
            raise QueryError("A non-empty chat question is required.")

        handler = rag_wf.run(query=message)
        result = await handler
        draw_most_recent_execution(
            handler,
            filename=str(Path("workflow_visualizations/last_execution.html").resolve()),
        )
        return str(result)
    except RagProjectError as e:
        return f"Error: {e}"
    except Exception as e:
        # Catch all unexpected workflow exceptions
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