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
