import time
import pandas as pd
from random import randint


class Output:
    key = None  # keyword
    url = None
    match = None  # match keyword
    alert_id = None
    file_name = None
    url_format = None  # HTML or PDF format

    def __init__(self, alert_id, key=None, url=None, file_name=None, url_format=None):
        self.alert_id = alert_id
        self.key = key.strip()
        self.url = url
        self.file_name = file_name
        self.url_format = url_format

    """
    Screenshot the web page.
    @param browser
    @param default_width
    @param default_height
    @param screenshot_path
    """

    @staticmethod
    def screenshotImage(browser, default_width, default_height, screenshot_path):
        # Set window dimension
        print('-------------------------------------Set Window Dimension-------------------------------------')
        browser.set_window_size(default_width, default_height)
        time.sleep(randint(1, 5))

        # Get screenshot
        print('----------------------------------------Get Screenshot----------------------------------------')
        browser.save_screenshot(f'{screenshot_path}.png')

    '''
    Draw the blocks.
    @param block_list
    @param file_name
    @param i
    '''

    @staticmethod
    def blockOutput(block_list, file_name, i=1):
        print('------------------------------------------Draw Block------------------------------------------')

    '''
    Draw the horizontal and vertical separators.
    @param sep_list
    @param file_name
    @param direction
    @param i
    '''

    @staticmethod
    def separatorOutput():
        print('----------------------------------------Draw Separator----------------------------------------')

    '''
    Assign the weight of separator inside the particular block
    '''

    @staticmethod
    def weightOutput():
        print('------------------------------------Assign Separator Weight-----------------------------------')

    '''
    Store the obtained news content into csv file and remove duplicates.
    @param block_list
    '''

    @staticmethod
    def newsTextOutput():
        print('-----------------------------------Store News Content to CSV----------------------------------')

    '''
    Use external links from CoralISEM for checking
    @param match
    @param accessible
    @param block_list
    '''

    def htmlTextOutput(self, match=False, accessible=True, block_list=None):
        self.match = match
        block_list = [] if block_list is None else block_list

        if self.match is not None:
            for block in block_list:
                for box in block.boxes:
                    if box.node_type == 3 and self.key.upper() in box.node_value.upper():
                        self.match = True
                        break

        table_items = {'Alert ID': self.alert_id,
                       'Keyword': self.key,
                       'Source Web Link': self.url,
                       'Accessible': accessible,
                       'Format': self.url_format,
                       'Match': self.match
                       }
        return pd.DataFrame([table_items])

        # Output.storeData(table_items, self.file_name)

    '''
    Use external links (PDF) from CoralISEM for checking
    @param req
    @param accessible
    '''

    def pdfTextOutput(self, pdf_path, accessible=True):
        try:
            doc = fitz.open(pdf_path)
        except FileDataError:
            accessible = False
            self.match = None
        else:
            for page in doc:
                if self.key in page.get_text():
                    self.match = True
                    break
                else:
                    self.match = False

        table_items = {'Alert ID': self.alert_id,
                       'Keyword': self.key,
                       'Source Web Link': self.url,
                       'Accessible': accessible,
                       'Format': self.url_format,
                       'Match': self.match
                       }

        return pd.DataFrame([table_items])

        # Output.storeData(table_items, self.file_name)

    '''
    Store the DataFrame into csv file
    @param items
    @param file_name
    '''

    @staticmethod
    def storeData(items, file_name):
        print('--------------------------------------Store Data to CSV---------------------------------------')

        text_list = [items]

        current = pd.DataFrame(text_list)
        try:
            before = pd.read_csv(file_name)
            data = pd.concat([before, current])
            print(data.tail(10))
            print('Shape    : ', data.shape)
            print()
        except FileNotFoundError:
            data = current

        data.to_csv(file_name, index=False, encoding='utf-8')
