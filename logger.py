# logger.py
import logging
import streamlit as st

class StreamlitLogger(logging.Logger):
    def __init__(self, name):
        super().__init__(name)

    def emit(self, record):
        log_message = self.format(record)
        # Instead of writing the log message to Streamlit, add it to a global list
        global log_messages
        log_messages.append(log_message)

def get_logger(name):
    logger = logging.getLogger(name)

    if (logger.hasHandlers()):
        logger.handlers.clear()

    logger.setLevel(logging.DEBUG)
    handler = StreamlitHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    return logger
