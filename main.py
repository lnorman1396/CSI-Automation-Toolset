import os
import importlib.util
import streamlit as st
import traceback
from typing import List
from streamlit_searchbox import st_searchbox

def import_module(module_name, module_path):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    st.sidebar.subheader("CSI - Automation Toolset")

    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Pages")
    subdirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and d != "tests"]

    pages = {}
    scripts = []  # List to store all script names
    for subdir in subdirs:
        subdir_path = os.path.join(base_dir, subdir)
        py_files = [f for f in os.listdir(subdir_path) if f.endswith(".py") and f != "__init__.py"]
        
        if not py_files:
            continue

        modules = []
        for py_file in py_files:
            module_name = f"pages.{subdir}.{py_file[:-3]}"
            module_path = os.path.join(subdir_path, py_file)
            mod = import_module(module_name, module_path)
            modules.append({"name": py_file[:-3], "function": mod.run})  

            scripts.append({"page": subdir.capitalize(), "script": py_file[:-3]})

        pages[subdir.capitalize()] = modules

    def search_scripts(search_term: str) -> List[str]:
        if search_term:
            return [script["script"] for script in scripts if search_term.lower() in script["script"].lower()]
        else:
            return []

    selected_script = st_searchbox(
        search_scripts,
        key="global_script_search",
    )

    selected_page = None
    selected_func = None

    if selected_script:
        for script in scripts:
            if script["script"] == selected_script:
                selected_page = script["page"]
                selected_func = script["script"]
                break

    page_list = list(pages.keys())
    selected_page = st.sidebar.selectbox(
        'Select a page:',
        page_list,
        index=page_list.index(selected_page) if selected_page else 0
    )

    options = {module["name"]: module["function"] for module in pages[selected_page]}
    script_list = list(options.keys())
    option = st.sidebar.selectbox(
        'Select Script',
        script_list,
        index=script_list.index(selected_func) if selected_func else 0
    )

    try:
        options[option]()
    except Exception as e:
        st.error(f"An error occurred while running the script: {e}")
        st.error("Please check the script and try again.")
        traceback.print_exc()

if __name__ == "__main__":
    main()
