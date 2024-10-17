# How to use xml_to_excel.py
The python program is run through the bash command line using the the following: 
'python xml_to_excel_limited.py <input_xml_file> <output_excel_file> <number_of_records> <record_tag>'

The program turns the specified amount of rows into an excel file.

It should be noted that the input_xml_file should end with the extension .xml and the output_excel_file should end with .xlsx. The record tag should always be the string 'row'.

# Findings
- Individual entries are separated by a 'row' tag which is defined in the python file to parse the data.
- The code blocks are defined in the body elements by the <code></code> tags.

# Troubles with data
- The initial data was hard to read in due to an innate 'row' tag that was not defined in the documentation. The row tag separates each entry in the xml file. As such the tag had to be read and determined manually.
- The records in each dataset are not aligned with records of each other dataset. This is because they are independent collections of records sorted by their creation dates or IDs. For example, the first 10 entries in the Votes datset do not correspond to the first 10 posts in the Posts dataset because votes can occur at any time and thus are recorded separately.
- To align the datasets we have to select a random sample of posts to get a representative sample from the dataset.
- Comments are being joined now, have yet to check if they are joining correctly.
