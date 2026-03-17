import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from workflow import RAGWorkflow
import events


class TestRAGWorkflow(unittest.IsolatedAsyncioTestCase):

    async def test_start_empty_query(self):
        wf = RAGWorkflow()
        ev = SimpleNamespace(query="  ")

        result = await wf.start(AsyncMock(), ev)

        self.assertIsInstance(result, events.NoResultsEvent)
        self.assertEqual(result.message, "No nodes retrieved")

    async def test_start_valid_query(self):
        wf = RAGWorkflow()
        mock_ctx = AsyncMock()
        mock_ctx.store = AsyncMock()
        mock_ctx.store.set = AsyncMock()

        ev = SimpleNamespace(query="Find docs")

        result = await wf.start(mock_ctx, ev)

        self.assertIsInstance(result, events.RouterEvent)
        mock_ctx.store.set.assert_awaited_once_with("query", "Find docs")

    async def test_route_to_structured(self):
        wf = RAGWorkflow()
        mock_ctx = AsyncMock()
        mock_ctx.store.get = AsyncMock(return_value="Find docs")

        with patch("workflow.selector.select") as mock_select:
            mock_select.return_value = SimpleNamespace(
                selections=[SimpleNamespace(index=0)]
            )

            next_event = await wf.route(mock_ctx, SimpleNamespace())

        self.assertIsInstance(next_event, events.StructuredQueryEvent)

    async def test_route_to_retrieve(self):
        wf = RAGWorkflow()
        mock_ctx = AsyncMock()
        mock_ctx.store.get = AsyncMock(return_value="Find docs")

        with patch("workflow.selector.select") as mock_select:
            mock_select.return_value = SimpleNamespace(
                selections=[SimpleNamespace(index=1)]
            )

            next_event = await wf.route(mock_ctx, SimpleNamespace())

        self.assertIsInstance(next_event, events.RetrieveEvent)

    async def test_run_structured_query_success(self):
        wf = RAGWorkflow()
        mock_ctx = AsyncMock()
        mock_ctx.store.get = AsyncMock(return_value="Find docs")

        with patch("workflow.structured_data_query_engine", return_value="answer"):
            next_event = await wf.run_structured_query(mock_ctx, SimpleNamespace())

        self.assertIsInstance(next_event, events.StructuredResultEvent)
        self.assertEqual(next_event.answer, "answer")

    async def test_run_structured_query_not_found_fallback(self):
        wf = RAGWorkflow()
        mock_ctx = AsyncMock()
        mock_ctx.store.get = AsyncMock(return_value="Find docs")

        with patch("workflow.structured_data_query_engine", return_value="NOT_FOUND"):
            next_event = await wf.run_structured_query(mock_ctx, SimpleNamespace())

        self.assertIsInstance(next_event, events.RetrieveEvent)

    async def test_run_structured_query_raises(self):
        wf = RAGWorkflow()
        mock_ctx = AsyncMock()
        mock_ctx.store.get = AsyncMock(return_value="Find docs")

        with patch(
            "workflow.structured_data_query_engine",
            side_effect=ValueError("oops"),
        ):
            with self.assertRaises(Exception):
                await wf.run_structured_query(mock_ctx, SimpleNamespace())

    async def test_finalize_structured_answer(self):
        wf = RAGWorkflow()
        mock_ctx = AsyncMock()
        mock_ctx.store.get = AsyncMock(return_value="Find docs")

        ev = events.StructuredResultEvent(answer="found info")

        with patch("workflow.llm") as mock_llm:
            mock_llm.complete.return_value = "final answer"

            stop = await wf.finalize_structured_answer(mock_ctx, ev)

        self.assertEqual(stop.result, "final answer")