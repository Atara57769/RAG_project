from llama_index.core.workflow import Workflow, step, StartEvent, StopEvent, Context
import events
from config.rag_config import llm, retriever, postprocessor, response_synthesizer
from config.route_config import selector, choices, structured_data_query_engine


class RAGWorkflow(Workflow):

    @step
    async def start(self, ctx: Context, ev: StartEvent) -> events.RouterEvent | events.NoResultsEvent:
        query = ev.query.strip()
        if not query:
            return events.NoResultsEvent(message="No nodes retrieved")
        await ctx.store.set("query", query)
        return events.RouterEvent()

    @step
    async def route(self, ctx: Context, ev: events.RouterEvent) -> events.StructuredQueryEvent | events.RetrieveEvent:

        query = await ctx.store.get("query")

        result = selector.select(choices, query=query)
        selected_index = result.selections[0].index

        if selected_index == 0:
            return events.StructuredQueryEvent()

        return events.RetrieveEvent()

    @step
    async def run_structured_query(
            self, ctx: Context, ev: events.StructuredQueryEvent
    ) -> events.StructuredResultEvent | events.RetrieveEvent:

        query = await ctx.store.get("query")


        response = structured_data_query_engine(query)

        # fallback אם אין תשובה
        if "NOT_FOUND" in response:
            return events.RetrieveEvent()

        return events.StructuredResultEvent(answer=response)

    @step
    async def finalize_structured_answer(
            self, ctx: Context, ev: events.StructuredResultEvent
    ) -> StopEvent:

        query = await ctx.store.get("query")

        final = llm.complete(f"""
        Answer the question clearly based on the structured information.

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