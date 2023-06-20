
import streamlit as st

def _import(full_name, error_messages):
    try:
        parts = full_name.split('.')
        module = __import__(parts[0])

        for part in parts[1:]:
            module = getattr(module, part)

        return module
    except ImportError as e:
        error_messages.append(f"Failed to import: {full_name}")
        return None
    except AttributeError as e:
        error_messages.append(f"Failed to import: {parts}")
        return None

def import_with_logs(full_name):
    error_messages = []
    module = _import(full_name, error_messages)

    if error_messages:
        expander = st.sidebar.expander('log')
        for msg in error_messages:
            expander.write(msg)

    return module
