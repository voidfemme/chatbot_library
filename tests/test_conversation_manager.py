import unittest
import os
from unittest.mock import patch
from chatbot_library.utils.conversation_manager import ConversationManager, Message


class TestConversationManager(unittest.TestCase):
    def setUp(self):
        self.conversation_manager = ConversationManager()

    def test_initialize_conversation(self):
        self.conversation_manager.initialize_conversation("Welcome to the chatbot.")
        self.assertEqual(len(self.conversation_manager.chat_log), 1)
        self.assertEqual(self.conversation_manager.chat_log[0].role, "system")
        self.assertEqual(
            self.conversation_manager.chat_log[0].content, "Welcome to the chatbot."
        )

    def test_append_messages(self):
        self.conversation_manager.append_system_message("System message.")
        self.conversation_manager.append_user_message("User message.")
        self.conversation_manager.append_bot_message("Bot message.")
        self.assertEqual(len(self.conversation_manager.chat_log), 3)
        self.assertEqual(self.conversation_manager.chat_log[1].role, "user")
        self.assertEqual(self.conversation_manager.chat_log[1].content, "User message.")

    @patch("openai.ChatCompletion.create")
    def test_get_chatbot_response(self, mock_openai_create):
        mock_openai_create.return_value = {
            "choices": [{"message": {"content": "Hello, how can I help you?"}}]
        }
        self.conversation_manager.append_user_message("Hello")
        response = self.conversation_manager.get_chatbot_response()
        self.assertEqual(response, "Hello, how can I help you?")

    def test_search_for_message(self):
        self.conversation_manager.append_user_message("Hi, how are you?")
        self.conversation_manager.append_bot_message("I'm doing well, thank you!")
        self.conversation_manager.append_user_message("What's the weather like?")
        self.conversation_manager.append_bot_message(
            "I'm not sure, I'm just a chatbot."
        )

        messages = self.conversation_manager.search_for_message("weather")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].role, "user")
        self.assertEqual(messages[0].content, "What's the weather like?")

    def test_save_and_load_chat_log(self):
        self.conversation_manager.append_user_message("Hi")
        self.conversation_manager.append_bot_message("Hello")
        self.conversation_manager.save_chat_log("test_chat_log.json")

        new_conversation_manager = ConversationManager()
        new_conversation_manager.load_chat_log("test_chat_log.json")
        self.assertEqual(len(new_conversation_manager.chat_log), 2)
        self.assertEqual(new_conversation_manager.chat_log[0].role, "user")
        self.assertEqual(new_conversation_manager.chat_log[0].content, "Hi")


class TestConversationManagerExtended(TestConversationManager):
    def test_num_tokens_from_messages(self):
        messages = [
            Message("user", "Hello!"),
            Message("assistant", "Hi there, how can I help you?"),
            Message("user", "Tell me a joke."),
            Message(
                "assistant",
                "Why did the chicken cross the road? To get to the other side!",
            ),
        ]
        tokens = self.conversation_manager.num_tokens_from_messages(messages)
        self.assertTrue(isinstance(tokens, int))
        self.assertGreater(tokens, 0)

    def test_trim_chat_log_to_token_limit(self):
        self.conversation_manager.max_tokens = 10
        for _ in range(20):
            self.conversation_manager.append_user_message("Hello!")
        self.conversation_manager.trim_chat_log_to_token_limit()
        tokens = self.conversation_manager.num_tokens_from_messages(
            self.conversation_manager.chat_log
        )
        self.assertLessEqual(tokens, self.conversation_manager.max_tokens)

    @patch("chatbot_library.utils.conversation_manager.tiktoken.encoding_for_model")
    def test_num_tokens_from_messages_model_not_found(self, mock_encoding_for_model):
        mock_encoding_for_model.side_effect = KeyError("Model not found")
        messages = [Message("user", "Hello!")]
        tokens = self.conversation_manager.num_tokens_from_messages(messages)
        self.assertTrue(isinstance(tokens, int))
        self.assertGreater(tokens, 0)

    def test_print_latest_message(self):
        self.conversation_manager.append_user_message("Hi")
        self.conversation_manager.append_bot_message("Hello")
        with patch("builtins.print") as mocked_print:
            self.conversation_manager.print_latest_message("user")
            mocked_print.assert_called_once()

    def test_print_chat_log(self):
        self.conversation_manager.append_user_message("Hi")
        self.conversation_manager.append_bot_message("Hello")
        with patch("builtins.print") as mocked_print:
            self.conversation_manager.print_chat_log()
            self.assertEqual(mocked_print.call_count, 2)

    def test_print_message(self):
        self.conversation_manager.append_user_message("Hi")
        self.conversation_manager.append_bot_message("Hello")
        with patch("builtins.print") as mocked_print:
            self.conversation_manager.print_message(1)
            mocked_print.assert_called_once()

    def tearDown(self):
        if os.path.exists("test_chat_log.json"):
            os.remove("test_chat_log.json")


if __name__ == "__main__":
    unittest.main()
