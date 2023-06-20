# logger.py
import logging
import streamlit as st



# define log_messages as a list
log_messages = []

class StreamlitLogger(logging.Logger):
    def __init__(self, name):
        super().__init__(name)

class StreamlitHandler(logging.Handler):
    def emit(self, record):
        global log_messages  # this is necessary to access the variable within the class method
        log_message = self.format(record)
        # Instead of writing the log message to Streamlit, add it to a global list
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
    global log_messages  # this is necessary to access the variable within the function
    return log_messages

