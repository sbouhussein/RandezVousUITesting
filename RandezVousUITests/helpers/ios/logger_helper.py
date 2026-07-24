import logging
import os
import threading


def setup_logger(project_root):
    log_dir = os.path.join(project_root, "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Use a fixed name instead of a timestamp to ensure it overwrites
    log_file = os.path.join(log_dir, "latest_execution.log")

    logger = logging.getLogger("RandezVousTest")
    # Clear out any old handlers if the logger was already initialized
    # (prevents duplicate logs in some IDEs)
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] -> %(message)s', datefmt='%H:%M:%S')

    # mode='w' tells Python to overwrite the file rather than adding to it
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger, log_file


def log_process_output(process, logger, prefix="[APPIUM]"):
    """Reads process output in a thread and pipes it to the logger."""

    def reader():
        for line in iter(process.stdout.readline, ""):
            if line:
                logger.info(f"{prefix} {line.strip()}")
        process.stdout.close()

    thread = threading.Thread(target=reader, daemon=True)
    thread.start()
    return thread