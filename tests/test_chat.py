import unittest
from unittest.mock import  patch

import chat


class TestChatRespond(unittest.IsolatedAsyncioTestCase):
    async def test_respond_empty_message(self):
        response = await chat.respond(" ", [])
        self.assertIn("Error:", response)
        self.assertIn("non-empty chat question", response)

    async def test_respond_success(self):
        async def handler():
            return "success-result"

        with patch.object(chat, "rag_wf") as mock_rag_wf:
            mock_rag_wf.run.return_value = handler()
            with patch("chat.draw_most_recent_execution") as mock_draw:
                response = await chat.respond("hello", [])

        self.assertEqual(response, "success-result")
        mock_rag_wf.run.assert_called_once_with(query="hello")
        mock_draw.assert_called_once()

    async def test_respond_unhandled_exception(self):
        with patch.object(chat, "rag_wf") as mock_rag_wf:
            mock_rag_wf.run.side_effect = ValueError("boom")
            response = await chat.respond("hello", [])
            self.assertTrue(response.startswith("Unhandled error:"))
