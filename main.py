import os
import importlib.util
import streamlit as st
import traceback
from typing import List
from streamlit_searchbox import st_searchbox
from streamlit_pagination import pagination_component
from auth import auth



def import_module(module_name, module_path):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def get_script_descriptions():
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Pages")
    subdirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and d != "tests"]

    descriptions = []
    for subdir in subdirs:
        subdir_path = os.path.join(base_dir, subdir)
        py_files = [f for f in os.listdir(subdir_path) if f.endswith(".py") and f != "__init__.py"]
        
        if not py_files:
            continue

        for py_file in py_files:
            module_name = f"pages.{subdir}.{py_file[:-3]}"
            module_path = os.path.join(subdir_path, py_file)
            mod = import_module(module_name, module_path)

            # Check if the module has a class named 'Description'
            if hasattr(mod, 'Description'):
                desc = mod.Description()
                title = getattr(desc, 'title', 'No title')
                description = getattr(desc, 'description', 'No description')
                icon = getattr(desc, 'icon', 'No icon')
                author = getattr(desc, 'author', '')  # Get the author, or an empty string if it doesn't exist

                descriptions.append((title, description, icon, author))

    return descriptions

def home_page():
    st.write("Welcome to CSI - Automation Toolset!")
    st.caption("This is an application that runs scripts from organised subdirectories within the optibus organisation")
    st.caption("You can search all scripts in the top global search bar")
    st.caption("To contribute to the scripts, please find the github repo [here](https://github.com/lnorman1396/CSI-Automation-Toolset)")
    st.caption("To find a video example of how to integrate an existing script, click [here](https://drive.google.com/file/d/1JlrUiPZBbthUc-xYd7qEVXe9xk2tzNWx/view?usp=sharing)")
    st.markdown('')
    
    descriptions = get_script_descriptions()

    # Define the number of cards per page
    cards_per_page = 6

    # Calculate the number of pages
    num_pages = len(descriptions) // cards_per_page
    if len(descriptions) % cards_per_page != 0:
        num_pages += 1

    # Initialize page_number in Session State
    if 'page_number' not in st.session_state:
        st.session_state.page_number = 0

   

    # Calculate the range of descriptions for the current page
    start = st.session_state.page_number * cards_per_page
    end = start + cards_per_page
        
    num_descriptions_on_current_page = min(end, len(descriptions)) - start

    st.markdown(f'**Script Previews**: {num_descriptions_on_current_page} / {len(descriptions)}')

    # Display the cards for the current page
    for i in range(start, min(end, len(descriptions)), 3):
        cols = st.columns(3)
        for j in range(3):
            index = i + j
            if index < min(end, len(descriptions)):
                title, description, icon, author = descriptions[index]

                # Create a preview card for the script
                # Calculate whether the description is too long
                is_description_too_long = len(description) > 100  # Adjust this value based on your needs

                # Conditionally include the ellipsis in the markdown
                ellipsis_html = '<span style="position: absolute; bottom: 0; right: 10px; padding-left: 10px; background-color: white;">...</span>' if is_description_too_long else ''

                # Calculate font size based on the length of the description
                
                description_tooltip = description if len(description) > 110 else ""
                description_display = description[:110] + "..." if len(description) > 110 else description

                cols[j].markdown(f"""
                    <div style="border: 1px solid #ddd; padding: 20px; margin-bottom: 10px; height: 180px; overflow: hidden; border-radius: 10px; background-color: #fff;">
                        <div>
                            <div style="display: flex; align-items: center; padding: 3px;">
                                <img src="{icon}" alt="icon" style="width: 30px; height: 30px; margin-right: 10px;">
                                <h6 style="font-size: 0.8em;">{title}</h6>
                            </div>
                            <p style="font-size: 0.8em; margin: 0; opacity: 0.7; font-style: italic;">Author: {author}</p>
                        </div>
                        <p style="position: relative; font-size: 0.9em; height: 100px;">
                            <span style="position: absolute; line-height: 1.2em; max-height: 4.8em; display: inline-block; word-wrap: break-word; padding-bottom:10px;" title="{description_tooltip}">{description_display}</span>
                        </p>
                    </div>
                """, unsafe_allow_html=True)

    

     # Add a next button and a previous button
    prev ,next, page_indicator = st.columns([.1,.1, .8])
        
    page_indicator.write(f"Page: {st.session_state.page_number + 1} of {num_pages}")

    if next.button("Next"):
        if st.session_state.page_number + 1 > num_pages - 1:
            st.session_state.page_number = 0
        else:
            st.session_state.page_number += 1

    if prev.button("Back"):
        if st.session_state.page_number - 1 < 0:
            st.session_state.page_number = num_pages - 1
        else:
            st.session_state.page_number -= 1


def generate_card(title, description, icon, author):
    # Calculate the number of lines in the description based on an average of 50 characters per line
    lines_in_description = len(description) // 20

    # Calculate the height of the card based on the number of lines in the description
    card_height = max(180, 20 * lines_in_description)  # Adjust these values based on your needs

    # Calculate the height of the paragraph containing the description as a percentage of the total card height
    description_height = int(card_height * 0.6)  # Adjust this value based on your needs

    card = f"""
        <div style="border: 1px solid #ddd; padding: 10px; margin-bottom: 10px; height: {card_height}px; overflow: hidden; border-radius: 10px; background-color: #fff;">
            <div>
                <div style="display: flex; align-items: center;">
                    <img src="{icon}" alt="icon" style="width: 40px; height: 40px; margin-right: 10px;">
                    <h6>{title}</h6>
                </div>
                <p style="font-size: 0.8em; margin: 0; opacity: 0.7; font-style: italic;">Author: {author}</p>
            </div>
            <p style="position: relative; height: {description_height}px;">
                <span style="position: absolute; line-height: 1.2em; max-height: 4.8em; display: inline-block; word-wrap: break-word;">{description}</span>
            </p>
        </div>
    """
    return card





def get_script_description(script_name):
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Pages")
    subdirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and d != "tests"]

    for subdir in subdirs:
        subdir_path = os.path.join(base_dir, subdir)
        py_files = [f for f in os.listdir(subdir_path) if f.endswith(".py") and f != "__init__.py"]
        
        if not py_files:
            continue

        for py_file in py_files:
            if py_file[:-3] == script_name:
                module_name = f"pages.{subdir}.{py_file[:-3]}"
                module_path = os.path.join(subdir_path, py_file)
                mod = import_module(module_name, module_path)

                # Check if the module has a class named 'Description'
                if hasattr(mod, 'Description'):
                    desc = mod.Description()
                    title = getattr(desc, 'title', 'No title')
                    description = getattr(desc, 'description', 'No description')
                    icon = getattr(desc, 'icon', 'No icon')
                    author = getattr(desc, 'author', '')  # Get the author, or an empty string if it doesn't exist

                    return title, description, icon, author

    return 'No title', 'No description', 'No icon', ''

def get_script_instructions(script_name):
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Pages")
    subdirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and d != "tests"]

    for subdir in subdirs:
        subdir_path = os.path.join(base_dir, subdir)
        py_files = [f for f in os.listdir(subdir_path) if f.endswith(".py") and f != "__init__.py"]
        
        if not py_files:
            continue

        for py_file in py_files:
            if py_file[:-3] == script_name:
                module_name = f"pages.{subdir}.{py_file[:-3]}"
                module_path = os.path.join(subdir_path, py_file)
                mod = import_module(module_name, module_path)

                # Check if the module has a class named 'Instructions'
                if hasattr(mod, 'Instructions'):
                    inst = mod.Instructions()
                    instructions = getattr(inst, 'instructions', 'No instructions')
                    link = getattr(inst, 'link', 'No link')
                

                    return instructions, link

    return 'No instructions', 'No link'

def generate_instructions_card(instructions, link):
    # Use a static icon
    icon = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSLlvf8qTqvuO7YUaN17vfVxHlaO3twzt3Jnw&usqp=CAU"  # Replace with the URL of your static icon

    card = f"""
        <div style="border: 1px solid #ddd; padding: 10px; margin-bottom: 10px; height: 180px; overflow: hidden; border-radius: 10px; background-color: #fff;">
            <div>
                <div style="display: flex; align-items: center;">
                    <img src="{icon}" alt="icon" style="width: 40px; height: 40px; margin-right: 10px;">
                    <h6>Instructions</h6>
                </div>
                <p style="font-size: 0.8em; margin: 0; opacity: 0.7; font-style: italic;">{instructions}</p>
            </div>
            <p style="position: relative; height: 100px;">
                <a href="{link}" target="_blank">Confluence Link</a>
            </p>
        </div>
    """
    return card



def main():
    st.markdown("""
            <style>
                   .block-container {
                        padding-top: 2rem;
                        padding-bottom: 0rem;
                        padding-left: 0rem;
                        padding-right: 0rem;
                    }
            </style>
            """, unsafe_allow_html=True)
   
   
    email = auth()
    if email is None:
        return
    elif "optibus" not in email:
        st.error("You must have an Optibus email to use this app.")
        return
    
    full_name = ' '.join([part.capitalize() for part in email.split('@')[0].split('.')])
    sidebar_logo = """
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding-bottom: 30px;">
             <img src="https://softr-assets-eu-prod.s3.eu-central-1.amazonaws.com/applications/8f7af9fb-a550-425d-b327-48195c193a5f/assets/4c301aa0-5435-4c45-be89-dffc52dab690.svg" alt="Optibus Logo" style="width: 50px; height: auto; margin-bottom: 20px;">
         </div>
                """
    st.sidebar.markdown(sidebar_logo, unsafe_allow_html=True)
    st.sidebar.caption(f"Welcome: {full_name}")
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Pages")
    subdirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and d != "tests"]

    pages = {"Home": [{"name": "Home", "function": home_page}]}  # Initialize pages with Home page
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

    st.caption('🔍 Global Search (all scripts in repo)')
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
        # Generate and display the card for the selected script
    if selected_page != "Home":
        title, description, icon, author = get_script_description(option)  # You'll need to implement this function
        if title != 'No title':  # Check if a description class was found
            card = generate_card(title, description, icon, author)
            st.sidebar.markdown(card, unsafe_allow_html=True)

        instructions, link = get_script_instructions(option)
        if instructions != 'No instructions':  # Check if an Instructions class was found
            card = generate_instructions_card(instructions, link)
            st.sidebar.markdown(card, unsafe_allow_html=True)

    

    # main.py
    from logger import get_logger

    logger = get_logger('streamlit_logger')
    logger.setLevel(logging.ERROR)

    try:
        # Set logger level to INFO when running a script
        logger.setLevel(logging.INFO)
        options[option]()
        # Set logger level back to ERROR afterwards
        logger.setLevel(logging.ERROR)
    except Exception as e:
        st.error(f"An error occurred while running the script: {e}")
        st.error("Please check the script and try again.")
        traceback.print_exc()
        
if __name__ == "__main__":
    main()
