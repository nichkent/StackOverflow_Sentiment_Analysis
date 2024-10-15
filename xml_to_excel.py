import sys
import pandas as pd
import xml.etree.ElementTree as ET

def main():
    if len(sys.argv) != 5:
        print("Usage: python xml_to_excel_limited.py <input_xml_file> <output_excel_file> <number_of_records> <record_tag>")
        sys.exit(1)

    input_xml_file = sys.argv[1]
    output_excel_file = sys.argv[2]
    record_tag = sys.argv[4]

    try:
        num_records = int(sys.argv[3])
        if num_records <= 0:
            raise ValueError
    except ValueError:
        print("Please provide a positive integer for the number of records to process.")
        sys.exit(1)

    try:
        # Parse the XML file incrementally
        context = ET.iterparse(input_xml_file, events=('start', 'end'))
        context = iter(context)
        event, root = next(context)

        records = []
        record_count = 0

        def get_local_tag(tag):
            return tag.split('}', 1)[1] if '}' in tag else tag

        for event, elem in context:
            if event == 'end':
                tag = get_local_tag(elem.tag)
                if tag == record_tag:
                    record_data = elem.attrib.copy()
                    for child in elem:
                        child_tag = get_local_tag(child.tag)
                        record_data[child_tag] = child.text.strip() if child.text else ''
                    records.append(record_data)
                    record_count += 1

                    # Clear elements to free memory
                    elem.clear()
                    root.clear()

                    if record_count >= num_records:
                        break

        if not records:
            print(f"No records with tag '{record_tag}' found to process.")
            sys.exit(1)

        # Convert to DataFrame
        df = pd.DataFrame(records)
        df.fillna('', inplace=True)

        # Write DataFrame to Excel file
        df.to_excel(output_excel_file, index=False, engine='openpyxl')

        print(f"Successfully processed {record_count} records.")
        print(f"Data successfully written to {output_excel_file}")

    except FileNotFoundError:
        print(f"File not found: {input_xml_file}")
        sys.exit(1)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

