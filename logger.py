# logger.py
import logging
import streamlit as st

log_messages = []

class StreamlitLogger(logging.Logger):
    def __init__(self, name):
        super().__init__(name)

class StreamlitHandler(logging.Handler):
    def emit(self, record):
        log_message = self.format(record)
        # append log_message to log_messages list
        log_messages.append(log_message)

# Function to get the logger
def get_logger(name):
    logger = StreamlitLogger(name)
    handler = StreamlitHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

# Function to get the log messages
def get_log_messages():
    # return log_messages
    return log_messages

