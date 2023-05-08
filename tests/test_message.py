import unittest
from unittest.mock import patch
from chatbot_library.utils.message import Message


class TestMessage(unittest.TestCase):
    def test_repr(self):
        msg = Message("user", "Hello, how are you?")
        self.assertEqual(repr(msg), "user: Hello, how are you?")

    def test_to_dict(self):
        msg = Message("user", "Hello, how are you?")
        self.assertEqual(
            msg.to_dict(), {"role": "user", "content": "Hello, how are you?"}
        )

    def test_from_dict(self):
        data = {"role": "user", "content": "Hello, how are you?"}
        msg = Message.from_dict(data)
        self.assertEqual(repr(msg), "user: Hello, how are you?")

    @patch("chatbot_library.utils.message.Message.call_with_rate_limit_retry")
    def test_get_embedding(self, mock_call_with_rate_limit_retry):
        mock_call_with_rate_limit_retry.return_value = {
            "data": [{"embedding": [0.1, 0.2, 0.3]}]
        }
        msg = Message("user", "Hello, how are you?")
        embedding = msg.get_embedding("Hello, how are you?")
        self.assertEqual(embedding, [0.1, 0.2, 0.3])

    @patch("chatbot_library.utils.message.Message.call_with_rate_limit_retry")
    def test_semantic_similarity(self, mock_call_with_rate_limit_retry):
        mock_call_with_rate_limit_retry.return_value = {
            "data": [{"embedding": [0.1, 0.2, 0.3]}]
        }
        msg1 = Message("user", "Hello, how are you?")
        msg2_content = "Hi, what's up?"
        similarity = msg1.semantic_similarity(msg2_content)
        self.assertIsInstance(similarity, float)


if __name__ == "__main__":
    unittest.main()
