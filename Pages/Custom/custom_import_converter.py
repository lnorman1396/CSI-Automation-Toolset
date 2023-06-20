

import streamlit as st

class Instructions:
    instructions = 'Enter your existing imports by pasting into text area, Click the button to convert, and paste the output back into your code including the custom import method at the top'
    link = '#'

class Description:
    title = "Custom Import"
    description = "This is a script translates your imports into special imports handled by this script"
    icon = "https://triumph.com.au/wp-content/uploads/2020/08/import-export-icon-17.png"
    author = 'Luke Norman'

def run():
    st.info("**This is specific to this app only**")

    def process_imports(raw_imports):
        lines = raw_imports.split("\n")
        processed_imports = []
    
        for line in lines:
            # Handle import with alias
            if " as " in line:
                module, alias = line.split(" as ")
                processed_imports.append(f"{alias.strip()} = _import('{module.split('import ')[-1].strip()}')")
            # Handle normal import
            elif "import " in line and "from" not in line:
                package = line.split("import ")[-1]
                processed_imports.append(f"{package.strip()} = _import('{package.strip()}')")
            # Handle from-import statement
            elif "from " in line:
                path, names = line.split(" from ")[-1].split(" import ")
                names = [name.strip() for name in names.split(',')]
                for name in names:
                    processed_imports.append(f"{name} = _import('{path.strip()}.{name}')")

    return "\n".join(processed_imports)
    
        return "\n".join(processed_imports)

    user_input = st.text_area("Paste your standard Python import statements here:", height=200, placeholder='import streamlit as st')

    if st.button('Convert'):
        result = process_imports(user_input)
        st.code(f"from custom_import_method import _import\n\n{result}")
