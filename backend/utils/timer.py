import time
from utils.logger import get_logger

logger = get_logger(__name__)

class Timer:
    def __init__(self, name):
        self.name = name
    
    def __enter__(self):
        self.start = time.perf_counter()
        logger.info(f"Starting timer for {self.name}")
    
    def __exit__(self, exc_type, exc_value, traceback):
        elapsed_time = (time.perf_counter() - self.start) * 1000  
        logger.info(f"Timer for {self.name} ended. Elapsed time: {elapsed_time:.2f} milliseconds")