# CSI-Automation-Toolset
A repo for the optibus CSI automation Initiative 

This repository contains the source code for a multipage Streamlit application that dynamically discovers Python scripts in subdirectories and allows the user to interactively select and execute these scripts.

## App Structure

The app is organized with a main script (`main.py`) that serves as the entry point, and a `pages` directory that contains subdirectories for different categories of scripts. Each subdirectory contains Python scripts that can be run in the Streamlit app. The structure is as follows:

my_app/
├── main.py
├── pages/
│ ├── validator/
│ │ ├── validator_script_1.py
│ │ ├── validator_script_2.py
│ │ ├── validator_script_3.py
│ ├── cleaner/
│ │ ├── cleaner_script_1.py
│ │ ├── cleaner_script_2.py
│ ├── translator/
│ │ ├── translator_script_1.py
│ │ ├── translator_script_2.py
│ ├── comparison/
│ │ ├── comparison_script_1.py
│ │ ├── comparison_script_2.py
│ └── collector/
│ ├── collector_script_1.py
│ ├── collector_script_2.py
│ ├── collector_script_3.py
│ ├── collector_script_4.py


Each Python script in the subdirectories of `pages` should contain a `run` function. This function is what will be executed when the script is selected in the Streamlit app.

## Usage

To use the app, simply run the following command in the terminal:

streamlit run main.py


The app will open in a web browser. In the sidebar, you can select a page (which corresponds to a subdirectory under pages), and then select a script to run. The output of the script's run function will be displayed in the main section of the page.

Contributing
To add a new script to the app, simply create a new Python file in the appropriate subdirectory under pages, and make sure that it contains a run function. The app will automatically discover the new script the next time it is run.

If you encounter any bugs or have any feature requests, please open an issue or submit a pull request. Contributions are welcome!

**Please Note, you can run your single scripts locally without cloning the repo, once tested, just include the file in the relevant directory in github. 
PLEASE ENSURE IT IS WRAPPED IN A RUN FUNCTION So the Main file can pick it up dynamically
