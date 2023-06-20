# logger.py
import streamlit as st
def _import(full_name, expander):
    try:
        parts = full_name.split('.')
        module = __import__(parts[0])

        for part in parts[1:]:
            module = getattr(module, part)

        return module
    except ImportError as e:
        expander.write(f"Failed to import: {full_name}")
        return None
    except AttributeError as e:
        expander.write(f"Failed to import: {parts}")
        return None
