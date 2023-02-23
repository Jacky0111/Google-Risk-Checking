import os
import json
import time
import requests
import functools
from random import randint
from datetime import datetime
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.common import UnexpectedAlertPresentException

from Output import Output
from DOM.DomNode import DomNode
# from VIPS.SeparatorWeight import SeparatorWeight
# from VIPS.SeparatorDetection import SeparatorDetection
from VIPS.VisualBlockExtraction import VisualBlockExtraction
# from VIPS.ContentStructureConstruction import ContentStructureConstruction


class Vips:
    PDoC = 6  # Permitted Degree of Coherence
    url = None
    skip = False
    output = None
    browser = None
    file_name = None
    window_width = None
    window_height = None
    node_list = []  # To store dom tree

    def __init__(self, url, output):
        self.url = url
        self.output = output
        self.node_list.clear()
        self.setFolderName()
        self.setDriver()
        self.getJavaScript()

    '''
    Execution function for Vips class including:
    1. Visual Block Extraction
    2. Visual Separator Detection
    3. Content Structure Construction
    '''
    def runner(self, skip):
        if skip:
            data = self.output.htmlTextOutput(match=None, accessible=False)
        else:
            print('Step 1: Visual Block Extraction---------------------------------------------------------------')
            vbe = VisualBlockExtraction()
            block = vbe.runner(self.node_list)
            block_list = vbe.block_list

            print(f'Number of Block List: {len(block_list)}')

            data = self.output.htmlTextOutput(block_list=block_list)

            print('---------------------------------------------Done---------------------------------------------')

        return data

    '''
    Each leaf node is checked whether it meets the granularity requirement. The common requirement must be DoC > PDoC
    @param blocks
    @return True if DoC > PDoC, False otherwise.
    '''
    def checkDoC(self, blocks):
        for ele in blocks:
            print(f'ele.DoC: {ele.DoC}, self.PDoC: {self.PDoC}')
            if ele.DoC > self.PDoC:
                print('ele.DoC > self.PDoC')
                return True
        print('ele.DoC < self.PDoC')
        return False

    '''
    Sort the separator list in ascending order.
    @param sep1
    @param sep2
    @return 1 if sep1 > sep2, -1 if sep1 < sep2, 0 otherwise.
    '''
    @staticmethod
    def separatorCompare(sep1, sep2):
        if sep1 < sep2:
            return -1
        elif sep1 > sep2:
            return 1
        else:
            return 0

    '''
    Set the folder name and make directory
    '''
    def setFolderName(self):
        pass
        # parse_url = urlparse(self.url)
        # path = r'Screenshots/' + parse_url.netloc + '_' + str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S')) + '/'
        # self.file_name = path + parse_url.netloc
        # os.makedirs(path)

    '''
    Set driver
    '''
    def setDriver(self):
        option = Options()
        option.add_argument('--headless')
        option.add_argument('--disable-gpu')
        option.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        caps = DesiredCapabilities.CHROME
        self.browser = webdriver.Chrome(desired_capabilities=caps, chrome_options=option)

    '''
    Retrieve Java Script from the web page
    '''
    def getJavaScript(self):
        self.browser.set_page_load_timeout(30)
        self.browser.get(self.url)
        time.sleep(randint(1, 5))

        # Before closing the web server make sure get all the information required
        try:
            self.window_width = 1920
            self.window_height = self.browser.execute_script('return document.body.parentNode.scrollHeight')
        except UnexpectedAlertPresentException:
            pass

        # output = Output()
        # output.screenshotImage(self.browser, self.window_width, self.window_height, self.file_name)

        # Read in DOM java script file as string
        file = open(r'DOM/dom.js', 'r')
        java_script = file.read()

        # Add additional javascript code to run our dom.js to JSON method
        java_script += '\nreturn JSON.stringify(toJSON(document.getElementsByTagName("BODY")[0]));'

        # Run the javascript
        x = self.browser.execute_script(java_script)

        self.browser.close()
        self.browser.quit()

        self.convertToDomTree(x)

    '''
    Use the JavaScript obtained from getJavaScript() to convert to DOM Tree (Recursive Function)
    @param obj
    @param parentNode 
    @return node
    '''
    def convertToDomTree(self, obj, parentNode=None):
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
            node.createTextNode(json_obj['nodeValue'], parentNode)
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
                        self.skip = True
                        return

        return node
