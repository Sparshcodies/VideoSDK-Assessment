from abc import ABC, abstractmethod
from videosdk import Stream

class Intelligence(ABC):
    @abstractmethod
    def __init__(self):
        """Initialize the Intelligence interface."""
        pass

    @abstractmethod
    def generate(self, text: str, sender_name: str):
        """generate new message based on text."""
        pass
