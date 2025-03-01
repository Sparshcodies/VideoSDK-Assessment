from abc import ABC, abstractmethod
from typing import Iterator, Union

class TTS(ABC):
    @abstractmethod
    def __init__(self):
        """Initialize the TTS interface."""
        pass

    @abstractmethod
    def generate(self, text: Union[str, Iterator[str]]):
        """Start the text-to-speech listening process."""
        pass


