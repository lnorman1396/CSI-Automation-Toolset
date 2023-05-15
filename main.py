import os
import importlib.util
import streamlit as st

def import_module(module_name, module_path):
    """
    Dynamically import a Python module.

    Args:
        module_name (str): The name of the module to import.
        module_path (str): The file system path to the module.

    Returns:
        module: The imported module.
    """
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    """
    The main function of the Streamlit app.

    This function is responsible for discovering the Python modules in the
    subdirectories of the "pages" directory, and presenting these modules
    to the user through selectboxes in the Streamlit app.
    """
    st.sidebar.subheader("CSI - Automation Toolset")

    # Discover modules
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pages")
    subdirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and d != "tests"]
    st.write(base_dir)

    pages = {}
    for subdir in subdirs:
        subdir_path = os.path.join(base_dir, subdir)
        py_files = [f for f in os.listdir(subdir_path) if f.endswith(".py") and f != "__init__.py"]
        
        # Skip directories that don't contain any Python files
        if not py_files:
            continue

        modules = []
        for py_file in py_files:
            module_name = f"pages.{subdir}.{py_file[:-3]}"
            module_path = os.path.join(subdir_path, py_file)
            mod = import_module(module_name, module_path)
            modules.append({"name": py_file[:-3], "function": mod.run})  # Assuming each module has a run function
        pages[subdir.capitalize()] = modules

    selected_page = st.sidebar.selectbox(
        'Select a page:',
        list(pages.keys()),
    )

    options = {module["name"]: module["function"] for module in pages[selected_page]}
    option = st.sidebar.selectbox(
        'Select Script',
        list(options.keys()),
    )

    try:
        options[option]()
    except Exception as e:
        st.error(f"An error occurred while running the script: {e}")
        st.error("Please check the script and try again.")

if __name__ == "__main__":
    main()
