import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class GRC:
    browser = None
    excel_file = None

    df_ori = pd.DataFrame()

    def __int__(self, excel_file):
        self.excel_file = excel_file
        self.readExcel()
        self.extractEngName()
        self.generateLink()
        self.setDriver()

    def readExcel(self):
        self.df_ori = pd.read_excel(self.excel_file, engine='openpyxl')

    '''
    Extract english name from Hit Name
    '''
    def extractEngName(self):
        self.df_ori['EN_HIT_NAME'] = self.df_ori['Hit Name'].str.replace(r'[^a-zA-Z\s]', '', regex=True).str.strip()

    '''
    Generate link by combine google search link with extracted english name
    '''
    def generateLink(self):
        self.df_ori['URL'] = 'https://www.google.com/search?q=' + self.df_ori['EN_HIT_NAME'].str.replace(' ', '+')

    def setDriver(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        caps = DesiredCapabilities.CHROME
        self.browser = webdriver.Chrome(desired_capabilities=caps, options=options)


if __name__ == '__main__':
    GRC().__int__(excel_file=r'test-file.xlsx')
