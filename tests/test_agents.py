#!/usr/bin/env python3

import os
import pytest
import unittest.mock as mock
from chatbot_library.agents.smart_agent import Agent, AmnesicAgent, SmartAgent
from chatbot_library.utils.conversation_manager import ConversationManager

mock_conversation_manager = mock.Mock()
mock_conversation_manager.get_chatbot_response.return_value = "Hello, how are you?"


@pytest.fixture
def conversation_manager():
    api_key = os.environ["OPENAI_API_KEY"]


def test_agent_is_abstract(conversation_manager):
    with pytest.raises(TypeError):
        Agent(conversation_manager)


def test_amnesic_agent_get_response():
    conversation_manager = mock_conversation_manager
    amnesic_agent = AmnesicAgent(conversation_manager)
    message = "Hello, how are you?"
    response = amnesic_agent.get_response(message)

    assert isinstance(response, str)
    assert len(response) > 0


def test_smart_agent_get_response():
    conversation_manager = mock_conversation_manager
    smart_agent = SmartAgent(conversation_manager)
    message = "Hello, how are you?"
    response = smart_agent.get_response(message)

    assert isinstance(response, str)
    assert len(response) > 0


def test_smart_agent_search_google(monkeypatch, conversation_manager):
    monkeypatch.setenv("GOOGLE_API_KEY", os.environ["GOOGLE_API_KEY"])
    monkeypatch.setenv("GOOGLE_CSE_ID", os.environ["GOOGLE_CSE_ID"])

    smart_agent = SmartAgent(conversation_manager)
    query = "OpenAI GPT-3"
    results = smart_agent.search_google(query)

    assert isinstance(results, str)
    assert len(results) > 0


def test_smart_agent_get_webpage_summary(conversation_manager):
    smart_agent = SmartAgent(conversation_manager)
    url = "https://en.wikipedia.org/wiki/OpenAI"
    summary = smart_agent.get_webpage_summary(url)

    assert isinstance(summary, str)
    assert len(summary) > 0
