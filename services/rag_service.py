import logging
from pathlib import Path

from llama_index.utils.workflow import draw_most_recent_execution
from domain.errors import RagProjectError, QueryError

logger = logging.getLogger(__name__)


class RagService:
    def __init__(self, workflow):
        self.workflow = workflow


    async def handle_query(self, query: str) -> str:
        try:
            if not query or not str(query).strip():
                raise QueryError("A non-empty chat question is required.")

            handler = self.workflow.run(query=query)
            result = await handler


            draw_most_recent_execution(
                handler,
                filename=str(
                    Path("../workflow_visualizations/last_execution.html").resolve()
                ),
            )

            return str(result)

        except RagProjectError:
            raise

        except Exception as exc:
            logger.exception("Unhandled error in RagService")
            raise RagProjectError("RAG service failed") from exc