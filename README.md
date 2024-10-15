# How to use xml_to_excel.py
The python program is run through the bash command line using the the following: 
'python xml_to_excel_limited.py <input_xml_file> <output_excel_file> <number_of_records> <record_tag>'

The program turns the specified amount of rows into an excel file.

It should be noted that the input_xml_file should end with the extension .xml and the output_excel_file should end with .xlsx. The record tag should always be row.

# Findings
- Individual entries are separated by a 'row' tag which is defined in the python file to parse the data.
- The code blocks are defined in the body elements.

# Troubles with data
- The initial data was hard to read due to an innate 'row' tag that was not defined in the documentation. As such the tag had to be read and determined manually.
