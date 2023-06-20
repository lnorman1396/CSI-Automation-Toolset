
import streamlit as st

class Instructions:
    instructions = 'Enter your existing imports by pasting into text area, Click the button to convert, and paste the output back into your code including the custom import method at the top'
    link = '#'

class Description:
    title = "Schedule Comparison"
    description = "This is a script that uses the Optibus API amd compares schedules from optibus urls to create an excel file, highlighting the savings between scenarios"
    icon = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRmaLtoRAJT4nxBOCBs_mQapmWJv3gxDjaYIQ&usqp=CAU"
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
