import pandas as pd
import os
from IPython.display import HTML

# create a dictionary of data with hyperlinks
data = {
    'Name': ['John', 'Emily', 'David'],
    'Link': ['/path/to/folder1',
             '/path/to/folder2',
             '/path/to/folder3']
}

# create a dataframe from the dictionary
df = pd.DataFrame(data)

# replace the hyperlink with clickable text and add a callback function
def open_folder(path):
    os.startfile(path)

df['Link'] = df['Link'].apply(lambda x: '<a href="#" onclick="open_folder(\'{}\')">{}</a>'.format(x, os.path.basename(x)))

# display the dataframe as an HTML table with clickable text
html_table = '<table>{}</table>'.format(df.to_html(
    escape=False,
    index=False
))

HTML(html_table)
