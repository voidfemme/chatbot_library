#!/usr/bin/env python3
from colored import fg, attr
from typing import List, Dict
from chatbot_library.utils.message import Message
import json
import tiktoken
import openai
import sys
import logging

CHAT_LOG_FILE = "chat_log.json"


class ConversationManager:
    def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 1.0) -> None:
        # Create a logger instance
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s = %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Main attributes
        self.max_tokens: int = 2000
        self.chat_log: list = []
        self.temperature = temperature
        self.model = model
        self.system_message = None

    def get_message_at(self, position: int) -> Message:
        return self.chat_log[position]

    def reset_chat_log(self) -> None:
        self.chat_log = []

    def initialize_conversation(self, system_message: str) -> None:
        self.system_message = Message("system", system_message)
        self.chat_log = [self.system_message]

    def messages_objs_to_dicts(self, messages: List[Message]) -> List[Dict[str, str]]:
        return [msg.to_dict() for msg in messages]

    def num_tokens_from_messages(self, messages, model="gpt-3.5-turbo-0301"):
        """Returns the number of tokens used by a list of messages."""
        messages_as_dicts = self.messages_objs_to_dicts(messages)
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if model == "gpt-3.5-turbo":
            print(
                "Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301."
            )
            return self.num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
        elif model == "gpt-4":
            print(
                "Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314."
            )
            return self.num_tokens_from_messages(messages, model="gpt-4-0314")
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = (
                4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            )
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif model == "gpt-4-0314":
            tokens_per_message = 3
            tokens_per_name = 1
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
            )
        num_tokens = 0
        for message in messages_as_dicts:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

    def get_chatbot_response(self, message: str = "") -> str:
        try:
            if message != "":
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=self.messages_objs_to_dicts(self.chat_log),
                    temperature=self.temperature,
                )
            else:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=self.messages_objs_to_dicts(self.chat_log),
                    temperature=self.temperature,
                )
            content = response["choices"][0]["message"]["content"]
            self.append_bot_message(content)
            return content

        except Exception as e:
            print(f"Error generating asssistant response: {e}", file=sys.stderr)
            return ""

    def print_latest_message(self, role: str) -> None:
        filtered_messages = [
            msg for msg in self.chat_log if msg.role.lower() == role.lower()
        ]
        if not filtered_messages:
            print(f"No messages found for role '{role}'.")
            return

        latest_message = filtered_messages[-1]
        message_content = latest_message.content
        match role.lower():
            case "user":
                color = fg("yellow")
            case "system":
                color = fg("blue")
            case "assistant":
                color = fg("green")
            case _:
                color = fg("white")

        print(f"{color}{message_content}{attr('reset')}")

    def print_chat_log(self) -> None:
        yellow = fg("yellow")
        green = fg("green")
        blue = fg("blue")
        reset = attr("reset")

        for message in self.chat_log:
            if message.role.lower() == "assistant":
                print(f"{yellow}{message.content}{reset}\n")
            elif message.role.lower() == "system":
                print(f"{blue}{message.content}{reset}\n")
            else:
                print(f"{green}{message.content}{reset}\n")

    def print_message(self, message_id: int) -> None:
        print(self.chat_log[message_id])

    def append_system_message(self, message: str) -> None:
        self.system_message = Message("system", message)
        self.chat_log.append(self.system_message)
        self.logger.info(
            f"System message appended with {self.num_tokens_from_messages([Message('system', message)])} "
            + f"tokens. Total tokens: {self.num_tokens_from_messages(self.chat_log)}"
        )

    def append_user_message(self, message: str) -> None:
        self.chat_log.append(Message("user", message))
        self.trim_chat_log_to_token_limit()
        self.logger.info(
            f"User message appended with {self.num_tokens_from_messages([Message('system', message)])} "
            + f"tokens. Total tokens: {self.num_tokens_from_messages(self.chat_log)}"
        )

    def append_bot_message(self, message: str) -> None:
        self.chat_log.append(Message("assistant", message))
        self.trim_chat_log_to_token_limit()
        self.logger.info(
            f"Bot message appended with {self.num_tokens_from_messages([Message('system', message)])} "
            + f"tokens. Total tokens: {self.num_tokens_from_messages(self.chat_log)}"
        )

    def trim_chat_log_to_token_limit(self) -> None:
        total_tokens = self.num_tokens_from_messages(self.chat_log)
        tokens_to_remove = total_tokens - self.max_tokens

        while tokens_to_remove > 0 and len(self.chat_log) > 1:
            # Remove the second message to leave the system message at the beginning of the conversation.
            removed_message = self.chat_log.pop(1)
            tokens_removed = self.num_tokens_from_messages([removed_message])
            tokens_to_remove -= tokens_removed
            self.logger.info(
                f"Message removed with {tokens_removed} tokens. Remaining tokens: {self.num_tokens_from_messages(self.chat_log)}"
            )

    def save_chat_log(self, file_path: str = CHAT_LOG_FILE) -> None:
        with open(file_path, "w") as f:
            json.dump(self.messages_objs_to_dicts(self.chat_log), f, indent=4)

    def load_chat_log(self, file_path: str = CHAT_LOG_FILE) -> None:
        with open(file_path, "r") as f:
            chat_log_data = json.load(f)
            self.chat_log = [Message.from_dict(msg_data) for msg_data in chat_log_data]

    def search_for_message(self, query: str) -> List[Message]:
        query = query.lower()
        filtered_messages = [
            msg for msg in self.chat_log if query in msg.content.lower()
        ]
        return filtered_messages
