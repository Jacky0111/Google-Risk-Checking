import json
import pandas as pd
from time import sleep
from pathlib import Path
from datetime import datetime

from selenium import webdriver
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
    file_name = None
    input_file = None
    output_file = None
    window_width = None
    window_height = None
    current_date_time = None

    keywords = []
    node_list = []  # To store dom tree
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()
    df_ori = pd.DataFrame()

    def __init__(self, input_file):
        self.node_list.clear()
        self.input_file = input_file
        self.output_file = f"{Path(self.input_file).stem.replace(' ', '')}_OutputFile.xlsx"
        self.current_date_time = str(datetime.now().strftime("%H%M-%d-%b-%Y"))

    def runner(self):
        # # Step 1: Google boolean search hit name and store the URL to new output file.
        # self.readExcelCSV(self.input_file)
        # self.extractEngName()
        # self.generateLink()
        # self.googleSearchHitName()

        # Step 2: Screenshot the entire website and check the content of website with name and keywords provided.
        self.readExcelCSV(self.output_file)
        self.specificNameWebsite()
        self.Vips()

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
        self.df_ori['URL'] = 'https://www.google.com/search?q=' + self.df_ori['EN_HIT_NAME'].str.replace(' ', '+') + \
                             ' AND (~crime OR ~corruption OR ~money laundering OR ~bribe)'.replace(' ', '+')

    def googleSearchHitName(self):
        count = 0
        with GRC.setDriver() as driver:
            for index, row in self.df_ori.iterrows():
                table_items = GRC.extractHitNameResults(driver, row)
                table_items.index += 1 + count
                count += table_items.shape[0]
                table_items.index.name = 'No.'
                self.df1 = pd.concat([self.df1, table_items])

        self.df1.to_excel(self.output_file)

    def specificNameWebsite(self):
        with GRC.setDriver() as driver:
            self.df2['Node List'] = ''
            for index, row in self.df2.iterrows():
                self.file_name = 'C:/Screenshots/' + str(datetime.now().strftime("%H%M-%d-%b-%Y")) + '_' + \
                                 str(row['Alert ID']) + '_' + str(row['No.']) + '.jpeg'
                print('11111111111111111111111')
                self.getJavaScript(driver, row['URL'])
                print('22222222222222222222222')
                # self.df2.at[index, 'Node List'] = self.node_list

        # self.df2.to_csv('see.csv', index=False)

    '''
    Retrieve Java Script from the web page
    '''
    def getJavaScript(self, driver, url):
        print('333333333333333333333333333333333333333')
        driver.get(url)
        print('open')
        sleep(5)

        # # Before closing the web server make sure get all the information required
        # self.window_width = 1920
        # self.window_height = driver.execute_script('return document.body.parentNode.scrollHeight')
        #
        # self.output = Output()
        # self.output.screenshotImage(driver, self.window_width, self.window_height, self.file_name)
        #
        # # Read in DOM java script file as string
        # file = open('DOM/dom.js', 'r')
        # java_script = file.read()
        #
        # # Add additional javascript code to run our dom.js to JSON method
        # java_script += '\nreturn JSON.stringify(toJSON(document.getElementsByTagName("BODY")[0]));'
        #
        # # Run the javascript
        # x = driver.execute_script(java_script)
        #
        driver.close()
        # driver.quit()
        print('close')
        #
        # self.convertToDomTree(x)

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
            for i in range(len(child_nodes)):
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

        return node

    def Vips(self):
        print('Step 1: Visual Block Extraction---------------------------------------------------------------')
        vbe = VisualBlockExtraction()
        block = vbe.runner(self.node_list)
        block_list = vbe.block_list

        print(f'Number of Block List: {len(block_list)}')
        # self.output.blockOutput(block_list, self.file_name)
        # Output.textOutput(block_list, self.url)

        print('---------------------------------------------Done---------------------------------------------')

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
        # options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        caps = DesiredCapabilities.CHROME
        browser = webdriver.Chrome(desired_capabilities=caps, options=options)
        return browser


if __name__ == '__main__':
    grc = GRC(input_file=r'test_file.xlsx')
    grc.runner()

