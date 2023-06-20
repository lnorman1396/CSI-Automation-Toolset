# logger.py
import logging
import streamlit as st

class StreamlitHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        st.write(msg)

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