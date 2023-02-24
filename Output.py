import os
import cv2
import time
import pandas as pd
from pathlib import Path


class Output:
    ''''
    Screenshot the web page.
    @param browser
    @param default_width
    @param default_height
    @param screenshot_path
    '''''
    @staticmethod
    def screenshotImage(browser, default_width, default_height, path_list):
        # Set window dimension
        print('-------------------------------------Set Window Dimension-------------------------------------')
        browser.set_window_size(default_width, default_height)
        time.sleep(10)

        # Get screenshot
        print('----------------------------------------Get Screenshot----------------------------------------')
        for screenshot_path in path_list:
            parent_dir = Path(screenshot_path).parent
            os.makedirs(parent_dir, exist_ok=True)
            browser.save_screenshot(f'{screenshot_path}.jpeg')

    '''
    Draw the blocks.
    @param block_list
    @param file_name
    @param i
    '''
    @staticmethod
    def blockOutput(block_list, file_name, i=1):
        print('------------------------------------------Draw Block------------------------------------------')

        img = cv2.imread(f'{file_name}.jpeg')
        red = (0, 0, 255)
        font = cv2.FONT_HERSHEY_SIMPLEX

        for block in block_list:
            if block.isVisualBlock:
                coordinate = (int(block.x), int(block.y), int(block.x + block.width), int(block.y + block.height))

                start_point = (coordinate[0], coordinate[1])
                end_point = (coordinate[2], coordinate[1])
                img = cv2.line(img, start_point, end_point, red, thickness=1)

                start_point = (coordinate[2], coordinate[1])
                end_point = (coordinate[2], coordinate[3])
                img = cv2.line(img, start_point, end_point, red, thickness=1)

                start_point = (coordinate[2], coordinate[3])
                end_point = (coordinate[0], coordinate[3])
                img = cv2.line(img, start_point, end_point, red, thickness=1)

                start_point = (coordinate[0], coordinate[3])
                end_point = (coordinate[0], coordinate[1])
                img = cv2.line(img, start_point, end_point, red, thickness=1)

                img = cv2.putText(img, str(block.identity), (coordinate[0], coordinate[3]), font, 0.5, red, 1)
        path = f'{file_name}_Block_{str(i)}.jpeg'
        cv2.imwrite(path, img)

    '''
    Draw the horizontal and vertical separators.
    @param sep_list
    @param file_name
    @param direction
    @param i
    '''
    @staticmethod
    def separatorOutput(sep_list, file_name, direction, i):
        print('----------------------------------------Draw Separator----------------------------------------')

        img = cv2.imread(f'{file_name}_Block_{str(i)}.png')
        blue = (255, 0, 0)

        for ele in sep_list:
            start_point = (int(ele.x), int(ele.y))
            end_point = (int(ele.x + ele.width), int(ele.y + ele.height))
            img = cv2.rectangle(img, start_point, end_point, blue, -1)
        path = f'{file_name}_{direction}_{str(i)}.png'
        cv2.imwrite(path, img)

    '''
    Store the obtained news content into csv file and remove duplicates.
    @param block_list
    '''
    @staticmethod
    def textOutput(block_list):
        print('-----------------------------------Store News Content to CSV ---------------------------------')
        news = []
        content = ''

        for block in block_list:
            for box in block.boxes:
                if box.nodeType == 3 and box.parentNode.nodeName == "p":
                    if len(box.nodeValue.split()) < 10:
                        continue
                    content += box.nodeValue + ' '
        news_items = {'Content': content}
        news.append(news_items)

        current = pd.DataFrame(news)
        print(current.tail(10))
        print("Shape    : ", current.shape)

        try:
            before = pd.read_csv('News.csv')
            print(before.tail(10))
            print("Shape    : ", before.shape)
            data = pd.concat([before, current])
        except FileNotFoundError:
            data = current
        data.drop_duplicates(inplace=True)
        data.to_csv('News.csv', index=False)

        print("Rows     : ", data.shape[0])
        print("Columns  : ", data.shape[1])
        print("Shape    : ", data.shape)
        print("Features : ", data.columns.tolist())

    @staticmethod
    def weightOutput(sep_list, file_name, condition, i):
        print('------------------------------Store Separator Weight to Text File ----------------------------')
        path = f'{file_name}_{condition}_{str(i)}.txt'

        with open(path, 'w') as f:
            for ele in sep_list:
                f.write(str(ele.weight))
                if ele == sep_list[-1]:
                    f.write('.')
                else:
                    f.write(', ')