import logging
import os
from datetime import datetime

def setup_logger(project_root):
    # 1. Create a 'logs' folder if it doesn't exist
    log_dir = os.path.join(project_root, "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 2. Generate a filename based on the current run time
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(log_dir, f"test_run_{timestamp}.log")

    # 3. Configure the logger
    logger = logging.getLogger("AppiumTest")
    logger.setLevel(logging.INFO)

    # Create formatters (making it easier to read)
    # [TIME] [LEVEL] -> Your Message
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] -> %(message)s', datefmt='%H:%M:%S')

    # File Handler (Writes to the folder)
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    # Stream Handler (Prints to PyCharm console)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger, log_file