import os
import json
import openpyxl
import pandas as pd
from time import sleep
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options

from Output import Output
from DOM.DomNode import DomNode
from VIPS.VisualBlockExtraction import VisualBlockExtraction


class GRC:
    PDoC = 6  # Permitted Degree of Coherence
    url = None
    output = None
    window_width = None
    window_height = None
    current_date_time = None

    # File path
    input_file = None
    output_file = None
    final_file = None

    keywords = []
    node_list = []  # To store dom tree
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()
    df_ori = pd.DataFrame()

    def __init__(self, input_file):
        self.input_file = input_file
        self.output_file = f"{Path(self.input_file).stem.replace(' ', '')}_OutputFile.xlsx"
        self.final_file = f"{Path(self.output_file).stem.replace(' ', '')}_Final.xlsx"
        self.current_date_time = str(datetime.now().strftime("%H%M-%d-%b-%Y"))

    def runner(self):
        # # Step 1: Google boolean search hit name and store the URL to new output file.
        # self.readExcel(self.input_file)
        # self.extractEngName()
        # self.generateLink()
        # self.googleSearchHitName()

        # Step 2: Screenshot the entire website and check the content of website with name and keywords provided.
        self.readExcel(self.output_file)
        self.specificNameWebsite()

        # Step 3: Create clickable path text
        self.clickablePathText()

    def clickablePathText(self):
        # Load the workbook and worksheet
        workbook = openpyxl.load_workbook(self.final_file)
        worksheet = workbook.active

        # Loop through the rows of the worksheet and create a hyperlink for each file path
        for row in range(2, worksheet.max_row + 1):
            file_path = worksheet.cell(row=row, column=10).value
            hyperlink = openpyxl.worksheet.hyperlink.Hyperlink(ref=f"D{row}", target=file_path)
            worksheet.cell(row=row, column=10).hyperlink = hyperlink

        # Save the changes to the Excel file
        workbook.save(self.final_file)

    def readExcel(self, file):
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
        self.df_ori['URL'] = 'https://www.google.com/search?q=' + self.df_ori['EN_HIT_NAME'].str.replace(' ', '+') + \
                             ' AND (~crime OR ~corruption OR ~money laundering OR ~bribe)'.replace(' ', '+')

    '''
    Boolean search the hit name by using Chrome browser
    '''
    def googleSearchHitName(self):
        count = 0

        for index, row in self.df_ori.iterrows():
            driver = GRC.setDriver()
            table_items = GRC.extractHitNameResults(driver, row)
            table_items.index += 1 + count
            count += table_items.shape[0]
            table_items.index.name = 'No.'
            self.df1 = pd.concat([self.df1, table_items])
            self.df1.apply(lambda x: print(x), axis=1)

        self.df1.to_excel(self.output_file)

    def specificNameWebsite(self):
        for index, row in self.df2.iterrows():
            self.node_list.clear()
            driver = GRC.setDriver()
            date_time = datetime.now().strftime("%H%M-%d-%b-%Y")
            user_file_path = GRC.setUserReferenceFileName(str(date_time), str(row['Alert ID']), str(row['No.']))
            dev_file_path = GRC.setFolderName(row['URL'], str(date_time), str(row['Alert ID']), str(row['No.']))
            path_list = [user_file_path, dev_file_path]

            try:
                self.getJavaScript(driver, row['URL'], path_list)
            except TimeoutException:
                continue

            # Store text content from the website
            self.df2.loc[index, 'Text Content'] = self.Vips(path_list)

            # Store screenshot path from the website to excel as hyperlink format
            path_link = 'file://' + path_list[0] + '.png'
            self.df2.loc[index, 'Screenshot Path'] = path_link

            # Check if keyword exists in the content column
            self.df2['Text Content'] = self.df2['Text Content'].astype(str)
            self.df2['Match'] = self.df2.apply(lambda x: x['Hit Name'] in x['Text Content'], axis=1)

            self.df2['Keyword Hit?'] = self.df2['Text Content'].apply(lambda x: self.keywordsChecking(x))

        self.df2.to_excel(self.final_file, index=False)

    def Vips(self, path_list):
        print('Step 1: Visual Block Extraction---------------------------------------------------------------')
        vbe = VisualBlockExtraction()
        block = vbe.runner(self.node_list)
        block_list = vbe.block_list

        print(f'Number of Block List: {len(block_list)}')
        self.output.blockOutput(block_list, path_list[1])
        content = Output.textOutput(block_list)

        print('---------------------------------------------Done---------------------------------------------')
        return content

    '''
    Retrieve Java Script from the web page
    '''
    def getJavaScript(self, driver, url, path_list):
        driver.get(url)
        sleep(5)

        # Before closing the web server make sure get all the information required
        self.window_width = 1920
        self.window_height = driver.execute_script('return document.body.parentNode.scrollHeight')

        self.output = Output()
        self.output.screenshotImage(driver, self.window_width, self.window_height, path_list)

        # Read in DOM java script file as string
        file = open('DOM/dom.js', 'r')
        java_script = file.read()

        # Add additional javascript code to run our dom.js to JSON method
        java_script += '\nreturn JSON.stringify(toJSON(document.getElementsByTagName("BODY")[0]));'

        # Run the javascript
        x = driver.execute_script(java_script)

        driver.close()
        driver.quit()

        self.convertToDomTree(x)

    '''
    Use the JavaScript obtained from getJavaScript() to convert to DOM Tree (Recursive Function)
    @param obj
    @param parentNode 
    @return node
    '''
    def convertToDomTree(self, obj, parent_node=None):
        if isinstance(obj, str):
            # Use json lib to load our json string
            json_obj = json.loads(obj)
        else:
            json_obj = obj

        node_type = json_obj['nodeType']
        node = DomNode(node_type)

        # Element Node
        if node_type == 1:
            node.createElement(json_obj['tagName'])
            attributes = json_obj['attributes']
            if attributes is not None:
                node.setAttributes(attributes)
            visual_cues = json_obj['visual_cues']
            if visual_cues is not None:
                node.setVisualCues(visual_cues)
        # Text Node (Free Text)
        elif node_type == 3:
            node.createTextNode(json_obj['nodeValue'], parent_node)
            if node.parent_node is not None:
                visual_cues = node.parent_node.visual_cues
                if visual_cues is not None:
                    node.setVisualCues(visual_cues)

        self.node_list.append(node)
        if node_type == 1:
            child_nodes = json_obj['childNodes']
            if isinstance(child_nodes, str):
                return
            else:
                for i in range(len(child_nodes)):
                    try:
                        if child_nodes[i]['nodeType'] == 1:
                            node.appendChild(self.convertToDomTree(child_nodes[i], node))
                            print(f'NODE_{i}\n======\n{node.__str__()}')
                        elif child_nodes[i]['nodeType'] == 3:
                            try:
                                if not child_nodes[i]['nodeValue'].isspace():
                                    node.appendChild(self.convertToDomTree(child_nodes[i], node))
                                    print(f'NODE_{i}\n======\n{node.__str__()}')
                            except KeyError:
                                print('Key Error, abnormal text node')
                    except KeyError:
                        return

        return node

    def keywordsChecking(self, content):
        # Check if content is a string
        if isinstance(content, str):
            # Check if any keyword is in content
            matching = [k for k in self.keywords if k in content.lower()]

            # If there are any matching keywords, join them with comma and return
            if matching:
                return ', '.join(matching)
            # Return empty string otherwise
            else:
                return ''

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

        driver.close()
        driver.quit()

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

    '''
    Create a folder at C drive where every use can access from their pc and save screenshot to the folder
    '''
    @staticmethod
    def setUserReferenceFileName(dt, alert_id, number):
        return 'C:/Screenshots/' + dt + '_' + alert_id + '_' + number

    '''
    Set the folder name and make directory
    '''
    @staticmethod
    def setFolderName(url, dt, alert_id, number):
        parse_url = urlparse(url)
        path = r'Screenshots/' + dt + '_' + alert_id + '_' + number + '/'
        os.makedirs(path)
        return path + parse_url.netloc


if __name__ == '__main__':
    grc = GRC(input_file=r'test_file.xlsx')
    grc.runner()

