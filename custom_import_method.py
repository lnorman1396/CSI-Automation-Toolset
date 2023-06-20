# logger.py
import logging
import streamlit as st

log_messages = []

class StreamlitLogger(logging.Logger):
    def __init__(self, name):
        super().__init__(name)

class StreamlitHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.log_messages = []

    def emit(self, record):
        log_entry = self.format(record)
        self.log_messages.append(log_entry)

    def get_logs(self):
        return self.log_messages

    def clear_logs(self):
        self.log_messages = []

# Function to get the logger
def get_logger(name):
    logger = logging.getLogger(name)
    logger.handlers = []  # Remove all existing handlers
    logger.setLevel(logging.INFO)
    handler = StreamlitHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    return logger, handler

# Function to get the log messages
def get_log_messages():
    # return log_messages
    return log_messages

