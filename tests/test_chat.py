import unittest
from unittest.mock import patch, AsyncMock

from app import chat


class TestChatRespond(unittest.IsolatedAsyncioTestCase):

    async def test_respond_empty_message(self):
        response = await chat.respond(" ", [])

        self.assertIn("Error:", response)
        self.assertIn("non-empty chat question", response)

    async def test_respond_success(self):
        with patch.object(chat, "rag_service") as mock_service:
            mock_service.handle_query = AsyncMock(return_value="success-result")

            response = await chat.respond("hello", [])

        self.assertEqual(response, "success-result")
        mock_service.handle_query.assert_awaited_once_with("hello")

    async def test_respond_unhandled_exception(self):
        with patch.object(chat, "rag_service") as mock_service:
            mock_service.handle_query = AsyncMock(side_effect=Exception("boom"))

            response = await chat.respond("hello", [])

        self.assertTrue(response.startswith("Unhandled error:"))