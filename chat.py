import gradio as gr
from pathlib import Path
import workflow

from llama_index.utils.workflow import draw_all_possible_flows, draw_most_recent_execution

# Create workflow
rag_wf = workflow.RAGWorkflow(timeout=120)
draw_all_possible_flows(
    rag_wf,
    filename=str(
        Path("rag_workflow.html").resolve()
    ),
)

# Gradio
async def respond(message, history):
    handler = rag_wf.run(query=message)
    result = await handler

    draw_most_recent_execution(
        handler,
        filename=str(Path("last_execution.html").resolve()),
    )

    return str(result)





demo = gr.ChatInterface(
    fn=respond,
    title="RAG Chat with Event-Driven Workflow"
)


if __name__ == "__main__":
    demo.launch()