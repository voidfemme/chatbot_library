#!/usr/bin/env python3
"""
smart_agent.py 

This module defines the Agent classes used for interacting with the chatbot library.
"""
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup, FeatureNotFound
from chatbot_library.utils.conversation_manager import ConversationManager
from googleapiclient.discovery import build
import os
import requests


class Agent(ABC):
    """
    Abstract base class for chatbot agents.
    """

    def __init__(
        self,
        conversation_manager: ConversationManager,
        temperature: float = 1.0,
    ):
        self.conversation_manager = conversation_manager
        self.temperature = temperature

    @abstractmethod
    def get_response(self, message: str) -> str:
        """
        Returns a response to the given message.

        :param message: A string representing the user's message.
        :return: A string representing the chatbot's response.
        """
        pass


class AmnesicAgent(Agent):
    """
    Amnesic agent that doesn't remember previous interactions.
    """

    def __init__(
        self,
        conversation_manager: ConversationManager,
        temperature: float = 1,
    ):
        super().__init__(conversation_manager, temperature)

    def get_response(self, message: str) -> str:
        self.conversation_manager.append_user_message(message)
        response = self.conversation_manager.get_chatbot_response()
        self.conversation_manager.reset_chat_log()
        return response


class SmartAgent(Agent):
    """
    Smart agent that can remember previous interactions and perform web searches.
    """

    def __init__(
        self,
        conversation_manager: ConversationManager,
        temperature: float = 1.0,
        personality: str = "",
    ) -> None:
        super().__init__(conversation_manager, temperature)
        self.personality = personality
        if personality:
            conversation_manager.initialize_conversation(self.personality)

    def get_response(self, message: str) -> str:
        self.conversation_manager.append_user_message(message)
        response = self.conversation_manager.get_chatbot_response()
        return response

    def search_google(self, query: str) -> str:
        """
        Searches Google ofr the given query and returns the top 3 results.

        :param query: A string representing the search query
        :return: A formatted string containing the top 3 search results.
        """
        api_key = os.environ["GOOGLE_API_KEY"]
        cse_id = os.environ["GOOGLE_CSE_ID"]
        service = build("customsearch", "v1", developerKey=api_key)
        results = service.cse().list(q=query, cx=cse_id, num=3).execute()

        top_results = results.get("items", [])
        formatted_results = ""

        for i, result in enumerate(top_results[:3]):
            title = result.get("title", "No title available")
            link = result.get("link", "No link available")
            formatted_results += f"{i + 1}. {title}\n{link}\n\n"

        return formatted_results.strip()

    def get_webpage_summary(self, url: str) -> str:
        """
        Retrieves a webpage summary by fetching its content and asking the chatbot to summarize it.

        :param url: A string representing the URL of the webpage.
        :return: A string representing the summary of the webpage content.
        """
        try:
            response = requests.get(url)
            try:
                soup = BeautifulSoup(response.text, features="xml")
            except FeatureNotFound:
                soup = BeautifulSoup(response.text, "html.parser")
            print(f"BeautifulSoup: {soup}\n\n")
            text = " ".join([p.get_text() for p in soup.find_all("p")])
            summary = self.get_response(f"Please summarize the following text: {text}")
            return summary
        except Exception as e:
            return f"An error occurred while trying to fetch and summarize the webpage content: {e}"
