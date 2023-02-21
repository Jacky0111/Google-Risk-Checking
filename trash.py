import re
import pandas as pd
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def main():
    # Create a new instance of the Chrome web driver
    service = Service('/path/to/chromedriver')
    driver = webdriver.Chrome(service=service)

    # Load the search keywords from a DataFrame
    df = pd.read_excel(r'Hit Name List for January 2023 (ACP).xlsx', engine='openpyxl')
    search_keywords = df['Hit Name'].tolist()

    # Type in each search keyword and get the search results
    for keyword in search_keywords:
        print(f'Current Keyword: {keyword}')

        keyword = re.sub(r'\s+', '+', keyword)

        driver = webdriver.Chrome(service=service)
        driver.get(f'https://www.google.com/search?q=%22{keyword}%22')

        # Find the search bar element
        # search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'q')))
        # search_box.clear()
        # search_box.send_keys(f'"{keyword}"')  # type in the search keyword
        # search_box.send_keys(Keys.RETURN)  # submit the search query
        #
        # link = driver.find_element(By.XPATH, '/html/body/div[1]/div')
        # print(link.text)

        # Wait for the page to load
        sleep(3)

        # Find all the search result links on the page
        search_results = driver.find_elements(By.XPATH, "//div[contains(@class, 'yuRUbf')]/a")

        # Print the search result links
        for index, link in enumerate(search_results):
            url = link.get_attribute('href')
            print(index + 1, url)

        # Close the browser window
        driver.close()
        driver.quit()


if __name__ == '__main__':
    main()

