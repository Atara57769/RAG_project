from pathlib import Path

from llama_index.utils.workflow import draw_all_possible_flows

from app.chat import demo, logger, rag_wf
from domain.errors import RagProjectError


if __name__ == "__main__":
    try:
        draw_all_possible_flows(
            rag_wf,
            filename=str(
                Path("../workflow_visualizations/rag_workflow.html").resolve()
            ),
        )
        demo.launch()
    except Exception as exc:
        logger.exception("Gradio launch failed")
        raise RagProjectError("Gradio failed to start.") from exc