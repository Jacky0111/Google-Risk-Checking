import os
import sys

import pandas as pd
from pathlib import Path
from urllib.parse import unquote, urlparse

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
    uploaded_file = None

    def __init__(self):
        Deployment.header()
        self.uploadFile()

    def runner(self):
        if self.uploaded_file is not None:
            file_path = self.uploaded_file.name
            grc = GRC(file_path)
            grc.runner()
        # try:
        #     self.output_name = f"{Path(self.uploaded_file.name).stem.replace(' ', '')}_OutputFile.csv"
        #     st.write(self.output_name)
        # except AttributeError:
        #     pass

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

        if self.uploaded_file is not None:
            # Read the Excel file into a dictionary of dataframes, with Sheet1 and Keywords List as keys
            try:
                df_dict = pd.read_excel(self.uploaded_file, engine='openpyxl', sheet_name=['Sheet1', 'Keywords List'])
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

    '''
    Display uploaded file
    '''
    def display(self):
        st.write(f'Rows: {self.df.shape[0]}')
        st.write(f'Columns: {self.df.shape[1]}')
        st.write(self.df)
        # st.write(self.keywords)


if __name__ == '__main__':
    if runtime.exists():
        dep = Deployment()
        dep.runner()
    else:
        sys.argv = ['streamlit', 'run', 'app.py']
        sys.exit(stcli.main())
