
import streamlit as st

def _import(full_name):
    try:
        parts = full_name.split('.')
        module = __import__(parts[0])

        for part in parts[1:]:
            module = getattr(module, part)

        return module
    except ImportError as e:
        
        return None
    except AttributeError as e:
       
        return None
