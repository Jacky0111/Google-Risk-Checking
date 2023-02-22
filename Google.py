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
    df = pd.DataFrame()
    df_ori = pd.read_excel(r'test-file.xlsx', engine='openpyxl')

    # Extract english name from Hit Name
    df_ori['EN_HIT_NAME'] = df_ori['Hit Name'].str.replace(r'[^a-zA-Z\s]', '').str.strip()

    # Combine google search link with extracted english name
    df_ori['URL'] = 'https://www.google.com/search?q=' + df_ori['EN_HIT_NAME'].str.replace(' ', '+')

    for index1, row in df_ori.iterrows():
        alert_id = row[1]
        hit_name = row[2]
        country = row[3]
        entry_cat = row[4]
        entry_sub_cat = row[5]
        ent_id = row[6]

        driver = setDriver()
        driver.get(row['URL'])
        sleep(5)

        search_results = driver.find_elements(By.XPATH, "//div[contains(@class, 'yuRUbf')]/a")

        # Print the search result links
        for index2, link in enumerate(search_results):
            url = link.get_attribute('href')

            table_items = {'Alert ID': alert_id,
                           'Hit Name': hit_name,
                           'Country': country,
                           'Entry-category': entry_cat,
                           'Entry-subcategory': entry_sub_cat,
                           'Ent Id': ent_id,
                           'URL': url
                           }

            print(index2)
            print('----------')
            print(table_items)

            df = pd.concat([df, pd.DataFrame([table_items])])

        # Close the browser window
        driver.close()
        driver.quit()

    df.to_csv('output_file.csv', index=False, encoding='utf-8')


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
