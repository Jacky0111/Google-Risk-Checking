import pandas as pd
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Create a new instance of the Chrome web driver
driver = webdriver.Chrome('/path/to/chromedriver')

# Open Chrome
driver.get('https://www.google.com')

# Find the search bar element and type in your search keyword
search_box = driver.find_element(By.NAME, 'q')
search_box.send_keys(f'"Lim Chia Chung"')

# Submit the search query by sending the Enter key
search_box.send_keys(Keys.RETURN)

# Wait for the page to load
sleep(3)

# Find all the search result links on the page
search_results = driver.find_elements(By.XPATH, "//div[contains(@class, 'yuRUbf')]/a")

# Click on each search result link
for link in search_results:
    url = link.get_attribute('href')
    print(url)

# Close the browser window
driver.close()

