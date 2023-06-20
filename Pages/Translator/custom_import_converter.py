
import streamlit as st

def run():
    st.title('Python Import Converter')

    def process_imports(imports):
        lines = imports.split('\n')
        new_imports = []
        for line in lines:
            if line.startswith('import'):
                modules = line[7:].split(',')
                for module in modules:
                    module = module.strip()
                    new_imports.append(f'{module} = _import("{module}")')
            elif line.startswith('from'):
                parts = line.split(' ')
                module = parts[1]
                submodules = parts[3].split(',')
                for sub in submodules:
                    sub = sub.strip()
                    new_imports.append(f'{sub} = _import("{module}.{sub}")')
        return '\n'.join(new_imports)

    user_input = st.text_area("Paste your standard Python import statements here:")

    if st.button('Convert'):
        result = process_imports(user_input)
        st.code(result)
