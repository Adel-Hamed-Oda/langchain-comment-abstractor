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
            print(f"Invalid version '{version}', defaulting to {DEFAULT_VERSION}")
            self.model = init_chat_model(DEFAULT_VERSION, model_provider="openai", temperature = 0)
        
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