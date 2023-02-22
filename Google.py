import re
import pandas as pd
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def main():
    df = pd.read_excel(r'Hit-Name-List-for-January-2023-(ACP).xlsx', engine='openpyxl')

    # Extract english name from Hit Name
    df['EN_HIT_NAME'] = df['Hit Name'].apply(lambda x: re.sub(r'[^a-zA-Z\s]', '', x))
    df['EN_HIT_NAME'] = df['EN_HIT_NAME'].apply(lambda x: x.strip())

    search_name = lambda name: 'https://www.google.com/search?q=' + name.replace(' ', '+')
    df['URL'] = df['EN_HIT_NAME'].apply(search_name)

    for index, row in df.iterrows():
        driver = setDriver()
        driver.get(row['URL'])
        sleep(5)

        search_results = driver.find_elements(By.XPATH, "//div[contains(@class, 'yuRUbf')]/a")

        # Print the search result links
        for index, link in enumerate(search_results):
            url = link.get_attribute('href')
            print(index + 1, url)

        # Close the browser window
        driver.close()
        driver.quit()


def setDriver():
    option = Options()
    option.add_argument('--headless')
    option.add_argument('--disable-gpu')
    option.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
    browser = webdriver.Chrome(options=option)
    return browser


def extractKeywordURL():
    pass


if __name__ == '__main__':
    main()
