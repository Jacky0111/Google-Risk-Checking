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
    @param path_list
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
            # Create directory for the screenshot if it doesn't exist
            parent_dir = Path(screenshot_path).parent
            os.makedirs(parent_dir, exist_ok=True)
            # Save screenshot with .png extension
            browser.save_screenshot(f'{screenshot_path}.png')

    '''
    Draw the blocks.
    @param block_list
    @param file_name
    @param i
    '''

    @staticmethod
    def blockOutput(block_list, file_name, i=1):
        # Print statement indicating the start of block drawing
        print('------------------------------------------Draw Block------------------------------------------')

        # Load image using OpenCV
        img = cv2.imread(f'{file_name}.png')
        # Define the color red in BGR format
        red = (0, 0, 255)
        # Define the font to use for text
        font = cv2.FONT_HERSHEY_SIMPLEX

        for block in block_list:
            # Check if the block is a visual block (i.e. has a bounding box)
            if block.isVisualBlock:
                # Define the coordinates of the bounding box
                coordinate = (int(block.x), int(block.y), int(block.x + block.width), int(block.y + block.height))

                # Draw the top horizontal line of the bounding box
                start_point = (coordinate[0], coordinate[1])
                end_point = (coordinate[2], coordinate[1])
                img = cv2.line(img, start_point, end_point, red, thickness=1)

                # Draw the right vertical line of the bounding box
                start_point = (coordinate[2], coordinate[1])
                end_point = (coordinate[2], coordinate[3])
                img = cv2.line(img, start_point, end_point, red, thickness=1)

                # Draw the bottom horizontal line of the bounding box
                start_point = (coordinate[2], coordinate[3])
                end_point = (coordinate[0], coordinate[3])
                img = cv2.line(img, start_point, end_point, red, thickness=1)

                # Draw the left vertical line of the bounding box
                start_point = (coordinate[0], coordinate[3])
                end_point = (coordinate[0], coordinate[1])
                img = cv2.line(img, start_point, end_point, red, thickness=1)

                # Draw the identity of the block as text
                img = cv2.putText(img, str(block.identity), (coordinate[0], coordinate[3]), font, 0.5, red, 1)

        # Define the path to save the output image and write the image using OpenCV
        path = f'{file_name}_Block_{str(i)}.png'
        cv2.imwrite(path, img)

    '''
    Store the obtained news content into csv file and remove duplicates.
    @param block_list
    '''
    @staticmethod
    def textOutput(block_list):
        print('-----------------------------------Store News Content to CSV ---------------------------------')
        content = ''

        for block in block_list:
            for box in block.boxes:
                # Check if the box node type is text (i.e. 3) and the parent node is a <p> tag
                if box.node_type == 3 and box.parent_node.node_name == "p":
                    # Check if the length of the text in the box is less than 10
                    if len(box.node_value.split()) < 10:
                        continue
                    # If the length is greater than or equal to 10, add the text to the content string
                    content += box.node_value + ' '

        return content


