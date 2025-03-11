from abc import ABC, abstractmethod

class BaseCollector(ABC):
    """Base interface for all collectors."""
    
    @abstractmethod
    def __init__(self):
        self.latest_metrics = {}

    @abstractmethod
    def collect_metrics(self):
        """Collect metrics and return as dictionary."""
        pass

    @abstractmethod
    def get_latest_metrics(self):
        """Return the latest collected metrics."""
        pass
