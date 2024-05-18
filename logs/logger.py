import logging
from rich import print


def get_logger(log_file, log_level):
    # Create logger object
    logger = logging.getLogger(log_file)
    logger.setLevel(log_level)

    # Set formatter for log messages
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Set up file handler for log messages
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Set up stream handler for log messages
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    
    return logger