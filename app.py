import os
import sys
import tempfile
import webbrowser
import pandas as pd
import streamlit as st
from streamlit import runtime
from streamlit.web import cli as stcli

from GoogleRiskChecking import GRC

st.set_page_config(layout="wide")
pd.set_option('display.max_columns', None)


class Deployment:
    df = pd.DataFrame()

    keywords = None
    output_name = None
    import_fp = None
    uploaded_file = None

    def __init__(self):
        Deployment.header()
        self.df = pd.DataFrame()
        self.uploadFile()

    def runner(self):
        if self.uploaded_file is not None:
            grc = GRC(self.import_fp)
            f_path, self.df = grc.runner()
            self.display()

            st.write(f'Done! Files saved at {f_path}')
            # Create a clickable text that opens the folder when clicked
            # folder_link = f'<a href="file://{f_path}" target="_blank">Open Folder</a>'
            # if st.markdown(folder_link, unsafe_allow_html=True):
            Deployment.openFolder(f_path)

            # # Create a button in Streamlit
            # if st.button('Open Folder'):
            #     # Call the open_folder function with the folder path as an argument
            #     Deployment.openFolder(f_path)
            #     st.stop()

    '''
    Print header
    '''
    @staticmethod
    def header():
        st.write('# Google Risk Checking')

    '''
    Upload csv or xlsx file
    '''
    def uploadFile(self):
        self.uploaded_file = st.file_uploader("Upload your input XLSX file", type=['xlsx'])
        saved_path = r'C:\Users\CP1\Documents\GitHub\Compliance-HRC\Archive'

        # Check if the directory exists, and create it if it does not
        if not os.path.exists(saved_path):
            os.makedirs(saved_path)

        if self.uploaded_file is not None:
            # Create a temporary file to save the uploaded file
            with tempfile.NamedTemporaryFile(prefix=self.uploaded_file.name[0:-5],
                                             suffix=".xlsx",
                                             delete=False,
                                             dir=r'C:\Users\CP1\Documents\GitHub\Compliance-HRC\Archive') as tmp_file:
                # Write the contents of the uploaded file to the temporary file
                tmp_file.write(self.uploaded_file.read())

                # Get the file path of the temporary file
                self.import_fp = tmp_file.name

                # Read the Excel file into a dictionary of dataframes, with Sheet1 and Keywords List as keys
                try:
                    df_dict = pd.read_excel(self.import_fp, engine='openpyxl', sheet_name=['Sheet1', 'Keywords List'])
                    # Extract the Sheet1 dataframe and the list of keywords from the Keywords List dataframe
                    self.df = df_dict['Sheet1']
                    self.keywords = df_dict['Keywords List']['Keywords'].tolist()
                    self.display()
                except ValueError as e:
                    if str(e) == "Worksheet named 'Keywords List' not found":
                        st.warning(
                            "The uploaded file does not contain a worksheet named 'Keywords List'. Please upload a valid file.")
                    else:
                        st.error(f"An error occurred while reading the file: {e}")
                    st.stop()
        else:
            # Clear all variables and pause the app
            st.session_state.clear()
            print(self.df)
            st.stop()

    '''
    Display uploaded file
    '''
    def display(self):
        st.write(f'Rows: {self.df.shape[0]}')
        st.write(f'Columns: {self.df.shape[1]}')
        st.write(self.df)
        # st.write(self.keywords)

    '''
    Open file explorer window for a given folder path
    '''
    @staticmethod
    def openFolder(folder_path):
        webbrowser.open_new(folder_path)


if __name__ == '__main__':
    if runtime.exists():
        # If the runtime environment exists, create a Deployment object and start the runner
        dep = Deployment()
        dep.runner()
    else:
        # If the runtime environment doesn't exist, start the Streamlit application
        sys.argv = ['streamlit', 'run', 'app.py']
        sys.exit(stcli.main())

# This code checks for the presence of a specific runtime environment and launches a Streamlit application if the
# environment doesn't exist. The 'runtime' object is used to check for the environment, and the 'exists()' function
# returns True if the environment is present and False otherwise. If the environment exists, a Deployment object is
# created and its 'runner()' method is called. Otherwise, the Streamlit application is started using the 'sys.argv' and
# 'stcli.main()' functions.

