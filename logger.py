# logger.py
import logging
import streamlit as st

class StreamlitLogger(logging.Logger):
    def __init__(self, name):
        super().__init__(name)

    def emit(self, record):
        st.write(self.format(record))

# Function to get the logger
def get_logger(name):
    return StreamlitLogger(name)
