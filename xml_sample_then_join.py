import sys
import xml.etree.ElementTree as ET
import random
import pandas as pd

def main():
    if len(sys.argv) != 6:
        print("Usage: python xml_sample_and_join.py <posts_xml_file> <comments_xml_file> <users_xml_file> <votes_xml_file> <sample_size>")
        sys.exit(1)

    posts_xml_file = sys.argv[1]
    comments_xml_file = sys.argv[2]
    users_xml_file = sys.argv[3]
    votes_xml_file = sys.argv[4]
    try:
        sample_size = int(sys.argv[5])
        if sample_size <= 0:
            raise ValueError
    except ValueError:
        print("Please provide a positive integer for the sample size.")
        sys.exit(1)

    try:
        # Step 1: Sample Records from Posts
        print("Sampling posts...")
        sampled_posts, post_ids, user_ids_from_posts = sample_posts(posts_xml_file, sample_size)

        # Step 2: Extract Matching Comments
        print("Extracting matching comments...")
        matching_comments, user_ids_from_comments = extract_matching_comments(comments_xml_file, post_ids)

        # Step 3: Extract Matching Votes
        print("Extracting matching votes...")
        matching_votes = extract_matching_votes(votes_xml_file, post_ids)

        # Combine user IDs from posts and comments
        user_ids = user_ids_from_posts.union(user_ids_from_comments)

        # Step 4: Extract Matching Users
        print("Extracting matching users...")
        matching_users = extract_matching_users(users_xml_file, user_ids)

        # Step 5: Combine Data into DataFrames
        print("Combining data...")
        posts_df = pd.DataFrame(sampled_posts)
        comments_df = pd.DataFrame(matching_comments)
        votes_df = pd.DataFrame(matching_votes)
        users_df = pd.DataFrame(matching_users)

        # Merge DataFrames
        # Merge Posts with Users (OwnerUserId)
        posts_users_df = posts_df.merge(users_df, left_on='OwnerUserId', right_on='Id', how='left', suffixes=('_Post', '_User'))

        # Merge Posts with Comments
        posts_comments_df = posts_users_df.merge(comments_df, left_on='Id_Post', right_on='PostId', how='left')

        # Merge with Votes
        full_df = posts_comments_df.merge(votes_df, left_on='Id_Post', right_on='PostId', how='left', suffixes=('', '_Vote'))

        # Write the combined data to an Excel file
        output_file = 'combined_sample_data.xlsx'
        print(f"Writing combined data to {output_file}...")
        full_df.to_excel(output_file, index=False, engine='openpyxl')

        print("Process completed successfully.")

    except FileNotFoundError as e:
        print(f"File not found: {e.filename}")
        sys.exit(1)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

def sample_posts(posts_xml_file, sample_size):
    """Sample posts from the Posts XML file."""
    sample_records = []
    total_records = 0
    post_ids = set()
    user_ids = set()

    # Incremental parsing of the XML file
    context = ET.iterparse(posts_xml_file, events=('end',))
    context = iter(context)

    for event, elem in context:
        if elem.tag == 'row' and elem.attrib.get('PostTypeId') == '1':  # Only sample questions
            total_records += 1

            # Print progress every 100 records
            if total_records % 100000 == 0:
                print(f"{total_records} posts processed...")

            # Parse the element into a dictionary
            record_data = elem.attrib.copy()

            if len(sample_records) < sample_size:
                sample_records.append(record_data)
            else:
                # Reservoir sampling algorithm
                s = random.randint(0, total_records - 1)
                if s < sample_size:
                    sample_records[s] = record_data

            # Collect PostIds and OwnerUserIds
            post_ids.add(record_data.get('Id'))
            owner_user_id = record_data.get('OwnerUserId')
            if owner_user_id:
                user_ids.add(owner_user_id)

            # Clear the element to free memory
            elem.clear()

    print(f"Total posts processed: {total_records}")
    print(f"Sampled {len(sample_records)} posts.")
    return sample_records, post_ids, user_ids

def extract_matching_comments(comments_xml_file, post_ids):
    """Extract comments that match the sampled post IDs."""
    matching_records = []
    total_records = 0
    user_ids = set()

    context = ET.iterparse(comments_xml_file, events=('end',))
    context = iter(context)

    for event, elem in context:
        if elem.tag == 'row':
            total_records += 1
            post_id = elem.attrib.get('PostId')
            if post_id in post_ids:
                record_data = elem.attrib.copy()
                matching_records.append(record_data)
                user_id = record_data.get('UserId')
                if user_id:
                    user_ids.add(user_id)
            elem.clear()

    print(f"Total comments processed: {total_records}")
    print(f"Matching comments found: {len(matching_records)}")
    return matching_records, user_ids

def extract_matching_votes(votes_xml_file, post_ids):
    """Extract votes that match the sampled post IDs."""
    matching_records = []
    total_records = 0

    context = ET.iterparse(votes_xml_file, events=('end',))
    context = iter(context)

    for event, elem in context:
        if elem.tag == 'row':
            total_records += 1
            post_id = elem.attrib.get('PostId')
            if post_id in post_ids:
                record_data = elem.attrib.copy()
                matching_records.append(record_data)
            elem.clear()

    print(f"Total votes processed: {total_records}")
    print(f"Matching votes found: {len(matching_records)}")
    return matching_records

def extract_matching_users(users_xml_file, user_ids):
    """Extract users that match the collected user IDs."""
    matching_records = []
    total_records = 0

    context = ET.iterparse(users_xml_file, events=('end',))
    context = iter(context)

    for event, elem in context:
        if elem.tag == 'row':
            total_records += 1
            user_id = elem.attrib.get('Id')
            if user_id in user_ids:
                record_data = elem.attrib.copy()
                matching_records.append(record_data)
            elem.clear()

    print(f"Total users processed: {total_records}")
    print(f"Matching users found: {len(matching_records)}")
    return matching_records

if __name__ == "__main__":
    main()

