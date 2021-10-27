import log_setup

FORMATTER = logging.Formatter("%(levelname)s::%(asctime)s::: %(message)s")


def get_console_handler():
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_console_handler())

    return logger
