try:
    import requests
except ImportError:
    print('Please install the requests library using pip install requests')
    exit()
try:
    from bs4 import BeautifulSoup
except ImportError:
    print('Please install the BeautifulSoup library using pip install beautifulsoup4')
    exit()
try:
    import regex
except ImportError:
    print('Please install the regex library using pip install regex')
    exit()

try:
    import csv
except ImportError:
    print('Please install the csv library using pip install csv')
    exit()

# Send a GET request to the URL
url = 'https://en.wikipedia.org/wiki/List_of_municipalities_in_Colorado'
response = requests.get(url)

# Parse the HTML content of the response
soup = BeautifulSoup(response.content, 'html.parser')

# Debugging : Open a file named 'debugging.html' in write mode
# with open('debugging.html', 'w', encoding='utf-8') as file:
#     # Use the prettify() method to format the HTML nicely
#     pretty_html = soup.prettify()
    
#     # Write the formatted HTML to the file
#     file.write(pretty_html)

# Find the table with the title "The 273 active municipalities of the State of Colorado"
# using a CSS selector
caption_text = 'The 273 active municipalities of the State of Colorado'
caption_selector = f'caption:contains("{caption_text}")'
table_title = soup.select(caption_selector)
table = None
if table_title:
    table = table_title[0].find_parent('table')
    if not table:
        print('Table not found')
        exit()
else:
    print('Table title not found')
    exit()

# Set up header indices and column names
headers = ['Municipality', 'Population 2020', 'Population change 2010-2020 (%)', 'Population density 2020']
header_indices = [3, 5] # note: indices start at 0
municipality_index = 0 # special case, requires regex handling
density_index = 7 # special case, requires regex handling

municipality_pattern = r'\b\p{L}[\p{L}\s\'.-]*?(?=\[[^\]]*\]|\d|†*$)'
# \b: This is a word boundary anchor. It matches the position where a word starts or ends. It ensures that the match starts 
# at the beginning of a word.

# \p{L}: This is a Unicode property escape sequence. It matches any character with the "Letter" property, which includes 
# letters from various scripts, including Latin letters with diacritics (e.g., "ñ").

# [\p{L}\s'.-]*?: This part of the pattern matches zero or more characters that are either letters, whitespace characters, 
# apostrophes, dots, or hyphens. The * quantifier means "zero or more," and the ? makes the * quantifier 
# non-greedy, which means it will capture as few characters as possible while still allowing the rest of the pattern to match.

# (?=[\[\]\d†]*$): This is a positive lookahead assertion. It checks what follows the matched characters and ensures that it 
# contains only characters within the set [\[\]\d†]*. This set includes square brackets, digits, and the dagger 
# symbol (†). The * quantifier allows for zero or more of these characters, and $ signifies the end of the line. This ensures 
# that the match ends when it encounters any of these characters or reaches the end of the line.

# Use a regular expression to find the number before 'km'
# E.g. '1162/sq mi449/km2'
density_pattern = r'(\d+)\s*/\s*km2'

# Find the tbody element
tbody = table.find('tbody')
if not tbody:
    print('Table body not found')
    exit()

# Find all <tr> elements with a child <th> element with scope="row"
th_elements = tbody.select('tr > th[scope="row"]')
rows = []
for th in th_elements:
    # Find the parent <tr> element
    tr = th.find_parent('tr')
    if tr:
        # Add the row to the list of rows
        rows.append(tr)

# Iterate through the rows
data = []
for row in rows:
    # Initialize an empty dictionary for each row
    data_row = {}
    # Find all the cells in the row (th & td elements)
    cells = row.find_all(['th', 'td'])
    # Extract the text from each cell
    header_cnt = 0
    for i, cell in enumerate(cells):
        if i == municipality_index:
            # Extract the text from the cell
            cell_text = cells[i].text.strip()
            # Use regex to extract the municipality name from the cell text
            match = regex.search(municipality_pattern, cell_text)
            if match:
                cell_text = match.group(0)
            else:
                cell_text = ''
            # Add the text to the dictionary
            data_row[headers[header_cnt]] = cell_text
            header_cnt += 1
        if i in header_indices:
            # Extract the text from the cell
            cell_text = cells[i].text.strip()
            # Add the text to the dictionary
            data_row[headers[header_cnt]] = cell_text
            header_cnt += 1
        if i == density_index:
            # Extract the text from the cell
            cell_text = cells[i].text.strip()
            # Use regex to extract the number from the cell text
            match = regex.search(density_pattern, cell_text)
            if match:
                cell_text = match.group(1)
            else:
                cell_text = ''
            # Add the text to the dictionary
            data_row[headers[header_cnt]] = cell_text

    # Add the dictionary to the data list
    data.append(data_row)

# Save the data to a CSV file
filename = 'municipalities.csv'
with open(filename, 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()
    writer.writerows(data)
