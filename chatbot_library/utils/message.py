#!/usr/bin/env python3

"""
message.py

This module defines the Message class used for representing chatbot messages and their embeddings.
"""

import time
from typing import List, Dict

from openai import OpenAIError
import openai
from sklearn.metrics.pairwise import cosine_similarity


class Message:
    """
    Represents a chatbot message with a role (e.g., 'user', 'bot') and content.
    """

    def __init__(self, role: str, content: str) -> None:
        self.role = role
        self.content = content
        self.embedding = self.get_embedding(self.content)

    def __repr__(self) -> str:
        return f"{self.role}: {self.content}"

    def get_embedding(
        self, content: str, engine: str = "text-embedding-ada-002"
    ) -> List[float]:
        """
        Retrieves the message content's embedding using the specified engine.

        :param content: A string representing the message content.
        :param engine: A string representing the name of the engine to use for generating the embedding.
        :return: A list of floats representing the message content's embedding.
        """
        content = content.encode(encoding="ASCII", errors="ignore").decode()
        response = self.call_with_rate_limit_retry(
            openai.Embedding.create, input=content, engine=engine
        )
        embedding = response["data"][0]["embedding"]  # this is a normal list
        return embedding

    def call_with_rate_limit_retry(self, func, *args, **kwargs):
        """
        Calls the given function and retries if a rate limit is exceeded.

        :param func: The function to call.
        :param args: Positional arguments for the function.
        :param kwargs: Keyword arguments for the function.
        :return: The result of the function call.
        """
        delay_seconds = 10
        while True:
            try:
                return func(*args, **kwargs)
            except OpenAIError as e:
                if e.code == "rate_limit":
                    print(f"Rate limit exceeded, waiting for {delay_seconds} seconds")
                    time.sleep(delay_seconds)
                else:
                    raise

    def semantic_similarity(self, message_to_compare: str) -> float:
        """
        Calculates the semantic similarity between the current message and another message.

        :param message_to_compare: A string representing the message content to compare.
        :return: A float representing the semantic similarity between the two messages.
        """
        message_embedding = self.get_embedding(message_to_compare)
        similarity = cosine_similarity([self.embedding], [message_embedding])[0][0]
        return similarity

    def to_dict(self):
        """
        Converts the Message object to a dictionary.

        :return: A dictionary representing the Message object.
        """
        return {"role": self.role, "content": self.content}

    @classmethod
    def from_dict(cls, data: Dict[str, str]):
        """
        Creates a Message object from a dictionary representation.

        :param data: A dictionary containing 'role' and 'content' keys.
        :return: A Message object.
        """
        return cls(data["role"], data["content"])
