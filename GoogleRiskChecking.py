import pandas as pd
from time import sleep
from pathlib import Path
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from VIPS.Vips import Vips


class GRC:
    input_file = None
    output_file = None
    current_date_time = None
    keywords = list()
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()
    df_ori = pd.DataFrame()

    def __int__(self, input_file):
        self.input_file = input_file
        self.output_file = f"{Path(self.input_file).stem.replace(' ', '')}_OutputFile.xlsx"
        self.current_date_time = str(datetime.now().strftime("%H%M-%d-%b-%Y"))
        # self.readExcelCSV(self.input_file)
        # self.extractEngName()
        # self.generateLink()
        # self.googleSearchHitName()
        self.readExcelCSV(self.output_file)
        self.specificNameWebsite()

    def readExcelCSV(self, file):
        try:
            df_dict = pd.read_excel(file, engine='openpyxl', sheet_name=['Sheet1', 'Keywords List'])
            self.df_ori = df_dict['Sheet1']
            self.keywords = df_dict['Keywords List']['Keywords'].tolist()
        except ValueError:
            self.df2 = pd.read_excel(file)

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

    def googleSearchHitName(self):
        with GRC.setDriver() as driver:
            for index, row in self.df_ori.iterrows():
                table_items = GRC.extractHitNameResults(driver, row)
                self.df1 = pd.concat([self.df1, table_items])

        self.df1.to_excel(self.output_file, index=False)

    def specificNameWebsite(self):
        with GRC.setDriver() as driver:
            for index, row in self.df2.iterrows():
                vips = Vips(row['URL'], driver)
                # vips.runner()

    @staticmethod
    def extractHitNameResults(driver, row):
        alert_id, hit_name, country, entry_cat, entry_sub_cat, ent_id, url = row[1:8]

        driver.get(url)
        sleep(5)

        search_results = driver.find_elements(By.XPATH, "//div[contains(@class, 'yuRUbf')]/a")

        # Create a list of dictionaries for each row in the search results
        table_items_list = [{'Alert ID': alert_id,
                             'Hit Name': hit_name,
                             'Country': country,
                             'Entry-category': entry_cat,
                             'Entry-subcategory': entry_sub_cat,
                             'Ent Id': ent_id,
                             'URL': link.get_attribute('href')
                             } for link in search_results]

        return pd.DataFrame(table_items_list)

    @staticmethod
    def setDriver():
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        caps = DesiredCapabilities.CHROME
        browser = webdriver.Chrome(desired_capabilities=caps, options=options)
        return browser


if __name__ == '__main__':
    GRC().__int__(input_file=r'test_file.xlsx')
