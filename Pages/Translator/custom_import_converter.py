
import streamlit as st

class Instructions:
    instructions = 'Enter the depot name, Paste in schedule 1 and schedule 2, check the domain is supported by the api call, run the script'
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

    user_input = st.text_area("Paste your standard Python import statements here:", height=100, placeholder='**import streamlit as st**')

    if st.button('Convert'):
        result = process_imports(user_input)
        st.code(result)
