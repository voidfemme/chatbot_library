#!/usr/bin/env python3
from chatbot_library.agents.smart_agent import SmartAgent
from chatbot_library.utils.conversation_manager import ConversationManager


def main():
    conversation_manager = ConversationManager()
    smart_agent = SmartAgent(conversation_manager)
    while True:
        user_input = input(":: ")

        # Check if the user wants to print a message
        if user_input.startswith("print_message "):
            try:
                position = int(user_input.split(" ")[1])
                message = conversation_manager.get_message_at(position)
                print(f"Message at position {position}: {message.content}")
            except (ValueError, IndexError):
                print("Invalid position. Please enter a valid position.")
            continue

        response = smart_agent.get_response(user_input)

        print(response)


if __name__ == "__main__":
    main()
