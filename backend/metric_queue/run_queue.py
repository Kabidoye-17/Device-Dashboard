from metric_queue.queue_manager import UploaderQueue
from utils.logger import get_logger

logger = get_logger('QueueRunner')

def main():
    try:
        queue = UploaderQueue()
        queue.run()
    except Exception as e:
        logger.error(f"Failed to start metrics collection: {str(e)}")
        raise

if __name__ == "__main__":
    main()
