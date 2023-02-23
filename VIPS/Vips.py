import os
import json
import time
import requests
import functools
from urllib.parse import urlparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from Output import Output
from DOM.DomNode import DomNode
from VIPS.VisualBlockExtraction import VisualBlockExtraction


class Vips:
    PDoC = 6  # Permitted Degree of Coherence
    url = None
    output = None
    browser = None
    file_name = None
    window_width = None
    window_height = None
    node_list = []  # To store dom tree

    def __init__(self, url, browser):
        self.url = url
        self.browser = browser
        self.node_list.clear()
        self.setFileName()
        self.getJavaScript()

    '''
    Execution function for Vips class including:
    1. Visual Block Extraction
    2. Visual Separator Detection
    3. Content Structure Construction
    '''

    def runner(self):
        print('Step 1: Visual Block Extraction---------------------------------------------------------------')
        vbe = VisualBlockExtraction()
        block = vbe.runner(self.node_list)
        block_list = vbe.block_list

        print(f'Number of Block List: {len(block_list)}')
        self.output.blockOutput(block_list, self.file_name)
        Output.textOutput(block_list, self.url)

        print('---------------------------------------------Done---------------------------------------------')

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

    def setFileName(self):
        parse_url = urlparse(self.url)
        path = r'Screenshots/' + parse_url.netloc + '_' + str(datetime.now().strftime("%H%M-%d-%b-%Y")) + '/'
        self.file_name = 'C:/Screenshots/' + str(datetime.now().strftime("%H%M-%d-%b-%Y")) + '/' + str(self.row) + '.pdf'

        os.makedirs(path)

    '''
    Retrieve Java Script from the web page
    '''

    def getJavaScript(self):
        self.browser.get(self.url)
        time.sleep(10)

        # Before closing the web server make sure get all the information required
        self.window_width = 1920
        self.window_height = self.browser.execute_script('return document.body.parentNode.scrollHeight')

        self.output = Output()
        self.output.screenshotImage(self.browser, self.window_width, self.window_height, self.file_name)

        # Read in DOM java script file as string
        file = open('DOM/dom.js', 'r')
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
