from abc import ABC, abstractmethod
from videosdk import Stream

class STT(ABC):
    @abstractmethod
    def __init__(self):
        """Initialize the STT interface."""
        pass

    @abstractmethod
    def start(self, peer_id, peer_name, stream: Stream):
        """Start the speech-to-text listening process."""
        pass

    @abstractmethod
    def stop(self, peer_id):
        """Stop the speech-to-text listening process."""
        pass

