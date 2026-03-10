import json

from llama_index.core.query_engine import router_query_engine
from llama_index.core.workflow import Workflow, step, StartEvent, StopEvent, Context
import events
from global_settings import *



class RAGWorkflow(Workflow):

    @step
    async def start(self, ctx: Context, ev: StartEvent) -> events.RouterEvent | events.NoResultsEvent:
        query = ev.query.strip()
        if not query:
            return events.NoResultsEvent(message="No nodes retrieved")
        await ctx.store.set("query", query)
        return events.RouterEvent()

    @step
    async def route(self, ctx: Context, ev: events.RouterEvent) -> events.StructuredAnswerEvent | events.RetrieveEvent:
        query = await ctx.store.get("query")

        response = router_query_engine.query(query)
        selected = response.metadata.get("selector_result")

        # אם הRouter בחר את list_tool (index 0) → JSON
        if selected and selected.selections[0].index == 0:
            return events.StructuredAnswerEvent(answer=str(response))

        # אחרת → מסלול סמנטי
        return events.RetrieveEvent()

    @step
    async def handle_structured(self, ctx: Context, ev: events.StructuredAnswerEvent) -> StopEvent:
        query = await ctx.store.get("query")

        final = llm.complete(f"""
            Based on the following information, answer the user's question clearly.
        
            Question: {query}
            Information: {ev.answer}
            """)
        return StopEvent(result=str(final))


    @step
    async def retrieve(self, ctx: Context, ev: events.RetrieveEvent) -> events.RetrievedNodesEvent | events.NoResultsEvent:

        query = await ctx.store.get("query")

        nodes = retriever.retrieve(query)

        if not nodes:
            return events.NoResultsEvent(
                message="No nodes retrieved"
            )

        return events.RetrievedNodesEvent(
            nodes=nodes
        )


    @step
    async def filter_nodes(self, ctx: Context, ev: events.RetrievedNodesEvent) -> events.FilteredNodesEvent | events.NoResultsEvent:

        query = await ctx.store.get("query")

        filtered = postprocessor.postprocess_nodes(
            ev.nodes,
            query_str=query
        )

        if not filtered:
            return events.NoResultsEvent(
                message="I can't find any relevant information in the documents."
            )

        return events.FilteredNodesEvent(
            nodes=filtered
        )


    @step
    async def synthesize(self, ctx: Context, ev: events.FilteredNodesEvent) -> StopEvent:

        query = await ctx.store.get("query")

        response = response_synthesizer.synthesize(
            query=query,
            nodes=ev.nodes
        )

        return StopEvent(
            result=str(response)
        )


    @step
    async def handle_no_results(self, ctx: Context, ev: events.NoResultsEvent) -> StopEvent:

        return StopEvent(
            result=ev.message
        )