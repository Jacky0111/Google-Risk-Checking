import pandas as pd
from time import sleep
from pathlib import Path
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options

from VIPS.Vips import Vips
from VIPS.VisualBlockExtraction import VisualBlockExtraction


class GRC:
    file_name = None
    input_file = None
    output_file = None
    current_date_time = None
    keywords = list()
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()
    df_ori = pd.DataFrame()

    def __init__(self, input_file):
        self.input_file = input_file
        self.output_file = f"{Path(self.input_file).stem.replace(' ', '')}_OutputFile.xlsx"
        self.current_date_time = str(datetime.now().strftime("%H%M-%d-%b-%Y"))

    def runner(self):
        # Step 1: Google boolean search hit name and store the URL to new output file.
        self.readExcelCSV(self.input_file)
        self.extractEngName()
        self.generateLink()
        self.googleSearchHitName()

        # Step 2: Screenshot the entire website and check the content of website with name and keywords provided.
        # self.readExcelCSV(self.output_file)
        # self.specificNameWebsite()

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
                table_items.insert(0, 'Index Number', index + 1)
                table_items.index = table_items.index + 1
                table_items.index.name = 'No.'
                self.df1 = pd.concat([self.df1, table_items])

        self.df1.to_excel(self.output_file)

    def specificNameWebsite(self):
        with GRC.setDriver() as driver:
            for index, row in self.df2.iterrows():
                self.file_name = 'C:/Screenshots/' + str(datetime.now().strftime("%H%M-%d-%b-%Y")) + '/' + str(self.row) + '.jpeg'
                self.setFileName()

    def setFileName(self):
        pass

    @staticmethod
    def extractHitNameResults(driver, row):
        no, alert_id, hit_name, country, entry_cat, entry_sub_cat, ent_id, url = row[0:8]

        driver.get(url)
        sleep(5)

        search_results = driver.find_elements(By.XPATH, "//div[contains(@class, 'yuRUbf')]/a")

        # Create a list of dictionaries for each row in the search results
        table_items_list = [{'No': no,
                             'Alert ID': alert_id,
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
    grc = GRC(input_file=r'test_file.xlsx')
    grc.runner()

