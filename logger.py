# logger.py
import logging
import streamlit as st

class StreamlitHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        st.write(msg)

# Function to get the logger
def get_logger(name):
    # Create a logger
    logger = logging.getLogger(name)
    # We set the logger level to the "lowest" possible, 
    # as level control will be handled by the handler
    logger.setLevel(logging.DEBUG)

    # Create our custom handler
    streamlit_handler = StreamlitHandler()
    streamlit_handler.setLevel(logging.INFO)

    # We create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # We link the formatter to our handler
    streamlit_handler.setFormatter(formatter)

    # We link the handler to our logger
    logger.addHandler(streamlit_handler)

    return logger

