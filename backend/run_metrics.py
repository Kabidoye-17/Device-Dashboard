from metric_queue.queue_manager import UploaderQueue
import argparse

def main():
    parser = argparse.ArgumentParser(description='Run metrics collection and upload')
    parser.add_argument('--server', 
                       default='https://kabidoye17.pythonanywhere.com',
                       help='PythonAnywhere server URL')
    parser.add_argument('--interval',
                       type=int,
                       default=10,
                       help='Collection interval in seconds')
    
    args = parser.parse_args()
    
    # Initialize and run the queue
    queue = UploaderQueue(args.server, args.interval)
    queue.run()

if __name__ == "__main__":
    main()
