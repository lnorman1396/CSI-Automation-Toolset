
import streamlit as st

class Instructions:
    instructions = 'Enter your existing imports by pasting into text area, Click the button to convert, and paste the output back into your code including the custom import method at the top'
    link = '#'

class Description:
    title = "Custom Import"
    description = "This is a script translates your imports into special imports handled by this script"
    icon = "https://www.google.com/url?sa=i&url=https%3A%2F%2Ftriumph.com.au%2Fsolutions%2Fsolutions-by-industry%2Fimport-export%2F&psig=AOvVaw3nUd_4YYXydWFnc1GMtBWq&ust=1687354987583000&source=images&cd=vfe&ved=0CBAQjRxqFwoTCODaqKr90f8CFQAAAAAdAAAAABAD"
    author = 'Luke Norman'

def run():

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

    user_input = st.text_area("Paste your standard Python import statements here:", height=200, placeholder='import streamlit as st')

    if st.button('Convert'):
        result = process_imports(user_input)
        st.code(result)
