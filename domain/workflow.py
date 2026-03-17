import logging
from llama_index.core.workflow import Workflow, step, StartEvent, StopEvent, Context

from config.rag_config import llm, retriever, postprocessor, response_synthesizer
from config.route_config import selector, choices, structured_data_query_engine
from domain import events
from domain.errors import WorkflowError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


class RAGWorkflow(Workflow):

    @step
    async def start(self, ctx: Context, ev: StartEvent) -> events.RouterEvent | events.NoResultsEvent:
        try:
            query = ev.query.strip()
            if not query:
                logger.info("Start step received empty query")
                return events.NoResultsEvent(message="No nodes retrieved")
            await ctx.store.set("query", query)
            logger.info("Start step saved query to context")
            return events.RouterEvent()
        except Exception as exc:
            logger.exception("Start step failed")
            raise WorkflowError("Failed in start step") from exc

    @step
    async def route(self, ctx: Context, ev: events.RouterEvent) -> events.StructuredQueryEvent | events.RetrieveEvent:
        query = await ctx.store.get("query")
        result = selector.select(choices, query=query)
        selected_index = result.selections[0].index
        logger.info("Routing query '%s' to selection index %s", query, selected_index)
        if selected_index == 0:
            return events.StructuredQueryEvent()
        return events.RetrieveEvent()

    @step
    async def run_structured_query(
            self, ctx: Context, ev: events.StructuredQueryEvent
    ) -> events.StructuredResultEvent | events.RetrieveEvent:
        try:
            query = await ctx.store.get("query")
            response = structured_data_query_engine(query)
            logger.info("Structured query received for query '%s'", query)
            # fallback אם אין תשובה
            if "NOT_FOUND" in response:
                logger.info("Structured query engine returned NOT_FOUND")
                return events.RetrieveEvent()
            return events.StructuredResultEvent(answer=response)
        except Exception as exc:
            logger.exception("Structured query step failed")
            raise WorkflowError("Structured query step failed") from exc

    @step
    async def finalize_structured_answer(
            self, ctx: Context, ev: events.StructuredResultEvent
    ) -> StopEvent:
        try:
            query = await ctx.store.get("query")
            final = llm.complete(f"""
            Answer the question clearly based on the structured information.

            Question: {query}
            Information: {ev.answer}
            """)
            logger.info("Final structured answer generated")
            return StopEvent(result=str(final))
        except Exception as exc:
            logger.exception("Finalizing structured answer failed")
            raise WorkflowError("Finalizing structured answer failed") from exc



    @step
    async def retrieve(self, ctx: Context, ev: events.RetrieveEvent) -> events.RetrievedNodesEvent | events.NoResultsEvent:
        try:
            query = await ctx.store.get("query")
            nodes = retriever.retrieve(query)
            logger.info("Retriever returned %s nodes for query '%s'", len(nodes) if nodes else 0, query)
            if not nodes:
                return events.NoResultsEvent(
                    message="No nodes retrieved"
                )
            return events.RetrievedNodesEvent(
                nodes=nodes
            )
        except Exception as exc:
            logger.exception("Retriever step failed")
            raise WorkflowError("Retriever step failed") from exc


    @step
    async def filter_nodes(self, ctx: Context, ev: events.RetrievedNodesEvent) -> events.FilteredNodesEvent | events.NoResultsEvent:
        try:
            query = await ctx.store.get("query")
            filtered = postprocessor.postprocess_nodes(
                ev.nodes,
                query_str=query
            )
            logger.info("Postprocessor filtered nodes: %s", len(filtered) if filtered else 0)
            if not filtered:
                logger.warning("No relevant nodes found after postprocessing")
                return events.NoResultsEvent(
                    message="I can't find any relevant information in the documents."
                )
            return events.FilteredNodesEvent(
                nodes=filtered
            )
        except Exception as exc:
            logger.exception("Node postprocessing failed")
            raise WorkflowError("Node postprocessing failed") from exc


    @step
    async def synthesize(self, ctx: Context, ev: events.FilteredNodesEvent) -> StopEvent:
        try:
            query = await ctx.store.get("query")
            response = response_synthesizer.synthesize(
                query=query,
                nodes=ev.nodes
            )
            logger.info("Synthesized response for query '%s'", query)
            return StopEvent(
                result=str(response)
            )
        except Exception as exc:
            logger.exception("Response synthesis failed")
            raise WorkflowError("Response synthesis failed") from exc


    @step
    async def handle_no_results(self, ctx: Context, ev: events.NoResultsEvent) -> StopEvent:
        try:
            logger.info("No results event: %s", ev.message)
            return StopEvent(
                result=ev.message
            )
        except Exception as exc:
            logger.exception("No-results handler failed")
            raise WorkflowError("No-results handler failed") from exc