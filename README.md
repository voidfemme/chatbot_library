# Chatbot Library

This chatbot library provides an easy-to-use interface for creating and interacting with chatbots. The library leverages OpenAI's GPT-3.5 model and includes several classes and utilities to create different types of chatbot agents. Additionally, it features a smart agent capable of web searches and webpage summarization.

## Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
   - [Conversation Manager](#conversation-manager)
   - [Agent](#agent)
   - [Amnesic Agent](#amnesic-agent)
   - [Smart Agent](#smart-agent)
3. [Examples](#examples)
4. [License](#licence)

## Installation

This library requires Python 3.6 or later. To install the required dependencies, run the following command in your terminal:

```bash
pip install -r requirements.txt
```

To use this library in your project as a local package, navigate to your project's root directory and run the following command:

```bash
pip intall -e /path/to/chatbot_library
```

Replace `/path/to/chatbot_library` with the actual path to the chatbot_library directory.

When importing the library, make sure to use the correct import statements. For example:

```python
from chatbot_library.agents.smart_agent import SmartAgent
```

Ensure that you have set the necessary API keys for Google's Custom Search API in your environment variables as GOOGLE_API_KEY and GOOGLE_CSE_ID, as well as the OPENAI_API_KEY which you can obtain from openAI

## Usage

### Conversation Manager

The ConversationManager class is responsible for managing the chatbot's conversation history, including appending messages, resetting the chat log, and more. It also handles the interaction with the OpenAI API to generate responses.

### Agent

The Agent class is an abstract base class for chatbot agents. It provides a foundation for creating different types of chatbot agents. The main method to override in derived classes is the get_response() method.

### Amnesic Agent

The AmnesicAgent is a chatbot agent that does not remember previous interactions. This agent is derived from the Agent class and is useful for situations where context from previous interactions is not needed.

### Smart Agent

The SmartAgent is a more advanced chatbot agent that can remember previous interactions and perform web searches using Google's Custom Search API. It also has the ability to fetch and summarize webpage content using BeautifulSoup. This agent is derived from the Agent class and is useful for more advanced applications.

## Examples

The following examples demonstrate how to use the various classes and agents in this library:

```python
from chatbot_library.utils.conversation_manager import ConversationManager
from smart_agent import AmnesicAgent, SmartAgent

# Initialize a conversation manager

conversation_manager = ConversationManager()

# Create an amnesic agent

amnesic_agent = AmnesicAgent(conversation_manager)

# Get a response from the amnesic agent

response = amnesic_agent.get_response("What is the capital of France?")
print(response)

# Create a smart agent with a personality

smart_agent = SmartAgent(conversation_manager, personality="I am a helpful chatbot.")

# Get a response from the smart agent

response = smart_agent.get_response("What is the capital of France?")
print(response)

# Perform a web search with the smart agent

search_results = smart_agent.search_google("best programming languages")
print(search_results)

# Summarize a webpage with the smart agent

summary = smart*agent.get_webpage_summary("https://en.wikipedia.org/wiki/Python*(programming_language)")
print(summary)

```

## License

This chatbot library is released under the GPL-3.0 License. See the LICENSE file for details.
