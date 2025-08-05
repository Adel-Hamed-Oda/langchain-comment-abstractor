# this is my trial at a general OpenAI-based agent using langchain
# the main reason I made this file is to reduce all the difficult syntax and complicated code into a simpler
# 'list of commands' style of argument
#
# Usage:
#   * general: all functions in here depend on the proper initialization of the Model itself and
#           will not work without that, so please ensure you have a valid API key
#   * send: sends a message to the model and adds it to the list of commands, this can be
#           configured to be either a system message or a human message depending on the need
#   * process: processes the list of commands given to the AI model and pauses the program until the
#           response arrives, do note that I did attempt to make this messaging system asynchronus
#           but after testing with my own mini-program I realized that synching response output is a hassle
#   * receive: returns the response of the model as a string, the reason process and receive
#           are 2 different functions is to allow indirect communication with the AI in case there is no
#           current need to receive the response
#   * clear: clears the list of commands in case you need to create a new list
#
# thankyou for reading :)

import os
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage

DEFAULT_VERSION = "gpt-4o-mini"

class Model:
    def __init__(self, version: str = DEFAULT_VERSION, key: str = ""):
        self.usable = False
        self.model = None
        self.messages = []
        self.response = None

        if not os.environ.get("OPENAI_API_KEY"):
            if not key:
                raise ValueError("API key not found. Please provide a valid API key")
            os.environ["OPENAI_API_KEY"] = key
        
        try:
            self.model = init_chat_model(version, model_provider="openai", temperature = 0)
        except Exception:
            try:
                self.model = init_chat_model(DEFAULT_VERSION, model_provider="openai", temperature = 0)
                print(f"Invalid version '{version}', defaulting to {DEFAULT_VERSION}")
            except Exception:
                print(f"Invalid API key please enter a valid key")
                return
        
        self.usable = True

    def _check_usable(self):
        if not self.usable:
            raise RuntimeError("Model is not initialized properly")

    def send(self, message: str, role: str = "human"):
        self._check_usable()

        if role == "system":
            self.messages.append(SystemMessage(message))
        elif role == "human":
            self.messages.append(HumanMessage(message))
        else:
            raise ValueError(f"Invalid role: {role}. Use 'human' or 'system'")

    def process(self):
        self._check_usable()
        if not self.messages:
            raise ValueError("No messages to process")
        self.response = self.model.invoke(self.messages)

    def receive(self) -> str:
        self._check_usable()

        if not self.messages:
            return "No input has been provided"

        if not self.response:
            return "No response generated yet. Call `process()` first"

        return self.response.content

    def clear(self):
        self._check_usable()
        self.messages = []
        self.response = None