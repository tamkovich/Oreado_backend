import logging
import os


def get_logger(name):
    # todo: logging cookbook
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler = logging.FileHandler(os.path.join("loggers", name+"_log.log"))
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # console_handler = logging.StreamHandler()
    # console_handler.setFormatter(console_handler)
    # console_handler.setFormatter(formatter)
    # logger.addHandler(console_handler)

    return logger


def log(logger, **kwargs):
    # todo: logging cookbook
    """
    :param logger: logging Object
    :param kwargs: contains everything to make logging.log func works
     - level
       [Level	  Numeric value
        CRITICAL  50
        ERROR	  40
        WARNING	  30
        INFO	  20
        DEBUG	  10
        NOTSET	  0]
     - msg
     - *args
     - **kwargs
    :return: None
    """
    if logger:
        logger.log(**kwargs)
