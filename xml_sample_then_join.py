import sys
import xml.etree.ElementTree as ET
import random
import pandas as pd
from collections import defaultdict

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
        comments_dict, user_ids_from_comments = extract_matching_comments(comments_xml_file, post_ids)

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
        full_df = combine_data(sampled_posts, comments_dict, matching_votes, matching_users)

        # Specify the columns to keep
        columns_to_keep = [
            'Id', 'PostTypeId', 'CreationDate', 'Score', 'ViewCount', 'Body',
            'OwnerUserId', 'LastEditorUserId', 'LastEditDate', 'LastActivityDate',
            'Title', 'Tags', 'AnswerCount', 'CommentCount', 'AcceptedAnswerId',
            'ClosedDate', 'CommentCount_Comment', 'VoteCount', 'Reputation',
            'LastAccessDate', 'Views', 'UpVotes', 'DownVotes', 'AccountId', 'Comments'
        ]

        # Keep only the specified columns
        full_df = full_df[columns_to_keep]

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

    # Incremental parsing of the XML file
    context = ET.iterparse(posts_xml_file, events=('end',))
    context = iter(context)

    for event, elem in context:
        if elem.tag == 'row' and elem.attrib.get('PostTypeId') == '1':  # Only sample questions
            total_records += 1

            # Progress indicator
            if total_records % 100000 == 0:
                print(f"{total_records} posts processed...", flush=True)

            # Parse the element into a dictionary
            record_data = elem.attrib.copy()

            # Convert Id and OwnerUserId to integers
            post_id = record_data.get('Id')
            if post_id is not None:
                post_id = int(post_id)
                record_data['Id'] = post_id

            owner_user_id = record_data.get('OwnerUserId')
            if owner_user_id:
                owner_user_id = int(owner_user_id)
                record_data['OwnerUserId'] = owner_user_id
            else:
                record_data['OwnerUserId'] = pd.NA  # Handle missing OwnerUserId

            if len(sample_records) < sample_size:
                sample_records.append(record_data)
            else:
                # Reservoir sampling algorithm
                s = random.randint(0, total_records - 1)
                if s < sample_size:
                    sample_records[s] = record_data

            # Clear the element to free memory
            elem.clear()

    print(f"Total posts processed: {total_records}")
    print(f"Sampled {len(sample_records)} posts.")

    # Now extract post_ids and user_ids from sample_records
    post_ids = set()
    user_ids = set()
    for record in sample_records:
        post_ids.add(record['Id'])
        owner_user_id = record.get('OwnerUserId')
        if pd.notna(owner_user_id):
            user_ids.add(owner_user_id)

    return sample_records, post_ids, user_ids

def extract_matching_comments(comments_xml_file, post_ids):
    """Extract comments that match the sampled post IDs."""
    comments_dict = defaultdict(list)
    total_records = 0
    user_ids = set()

    context = ET.iterparse(comments_xml_file, events=('end',))
    context = iter(context)

    for event, elem in context:
        if elem.tag == 'row':
            total_records += 1

            # Progress indicator
            if total_records % 1000000 == 0:
                print(f"{total_records} comments processed...", flush=True)

            post_id = elem.attrib.get('PostId')
            if post_id is not None:
                post_id = int(post_id)
                if post_id in post_ids:
                    record_data = elem.attrib.copy()
                    record_data['PostId'] = post_id

                    user_id = record_data.get('UserId')
                    if user_id:
                        user_id = int(user_id)
                        record_data['UserId'] = user_id
                        user_ids.add(user_id)
                    else:
                        record_data['UserId'] = pd.NA  # Handle missing UserId

                    # Add the comment to the list for the corresponding post
                    comments_dict[post_id].append(record_data)

            # Clear the element to free memory
            elem.clear()

    total_comments = sum(len(v) for v in comments_dict.values())
    print(f"Total comments processed: {total_records}")
    print(f"Matching comments found: {total_comments}")
    return comments_dict, user_ids

def extract_matching_votes(votes_xml_file, post_ids):
    """Extract votes that match the sampled post IDs."""
    matching_records = []
    total_records = 0

    context = ET.iterparse(votes_xml_file, events=('end',))
    context = iter(context)

    for event, elem in context:
        if elem.tag == 'row':
            total_records += 1

            # Progress indicator
            if total_records % 1000000 == 0:
                print(f"{total_records} votes processed...", flush=True)

            post_id = elem.attrib.get('PostId')
            if post_id is not None:
                post_id = int(post_id)
                if post_id in post_ids:
                    record_data = elem.attrib.copy()
                    record_data['PostId'] = post_id

                    matching_records.append(record_data)

            # Clear the element to free memory
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

            # Progress indicator
            if total_records % 100000 == 0:
                print(f"{total_records} users processed...", flush=True)

            user_id = elem.attrib.get('Id')
            if user_id is not None:
                user_id = int(user_id)
                if user_id in user_ids:
                    record_data = elem.attrib.copy()
                    record_data['Id'] = user_id

                    matching_records.append(record_data)

            # Clear the element to free memory
            elem.clear()

    print(f"Total users processed: {total_records}")
    print(f"Matching users found: {len(matching_records)}")
    return matching_records

def combine_data(sampled_posts, comments_dict, matching_votes, matching_users):
    """Combine posts with comments, votes, and user data."""
    # Posts DataFrame
    posts_df = pd.DataFrame(sampled_posts)
    posts_df['Id'] = posts_df['Id'].astype(int)
    posts_df['OwnerUserId'] = posts_df['OwnerUserId'].astype('Int64')

    print(f"posts_df shape: {posts_df.shape}")

    # Attach comments to posts
    print("Attaching comments to posts...")
    posts_df['Comments'] = posts_df['Id'].map(comments_dict)
    posts_df['Comments'] = posts_df['Comments'].fillna('').apply(lambda x: x if x != '' else [])

    print(f"After attaching comments, posts_df shape: {posts_df.shape}")

    # Add CommentCount from comments
    posts_df['CommentCount_Comment'] = posts_df['Comments'].apply(len)

    # Aggregate votes
    if matching_votes:
        votes_df = pd.DataFrame(matching_votes)
        votes_df['PostId'] = votes_df['PostId'].astype(int)
        votes_df['VoteTypeId'] = votes_df['VoteTypeId'].astype(int)

        # Example aggregation: count number of votes per post
        votes_agg = votes_df.groupby('PostId', as_index=False).agg({
            'VoteTypeId': 'count',  # Total votes
        }).rename(columns={'VoteTypeId': 'VoteCount'})

        # Ensure 'PostId' in votes_agg is unique
        if votes_agg['PostId'].duplicated().any():
            print("Warning: Duplicate Post IDs found in votes_agg")
        else:
            print("No duplicates in votes_agg['PostId']")

        print(f"votes_agg shape: {votes_agg.shape}")
    else:
        votes_agg = pd.DataFrame(columns=['PostId', 'VoteCount'])
        print("No matching votes found.")

    # Merge posts with aggregated votes
    print("Merging posts with votes...")
    full_df = posts_df.merge(votes_agg, left_on='Id', right_on='PostId', how='left')
    print(f"After merging with votes, full_df shape: {full_df.shape}")

    # Drop redundant 'PostId' column from votes
    full_df.drop(columns=['PostId'], inplace=True)

    # Merge with users
    if matching_users:
        users_df = pd.DataFrame(matching_users)
        users_df['Id'] = users_df['Id'].astype(int)
        users_df.rename(columns={'Id': 'UserId'}, inplace=True)

        print(f"users_df shape: {users_df.shape}")

        print("Merging with users...")
        full_df = full_df.merge(users_df, left_on='OwnerUserId', right_on='UserId', how='left', suffixes=('', '_User'))
        print(f"After merging with users, full_df shape: {full_df.shape}")

        # Drop redundant 'UserId' column
        full_df.drop(columns=['UserId'], inplace=True)
    else:
        print("No matching users found.")

    # Fill NaN values if needed
    full_df['VoteCount'] = full_df['VoteCount'].fillna(0).astype(int)

    # Ensure the final DataFrame has one row per post
    if full_df['Id'].duplicated().any():
        print("Warning: Duplicate Post IDs found in full_df after merging")
        duplicate_ids = full_df[full_df['Id'].duplicated()]['Id'].unique()
        print(f"Duplicate Post IDs: {duplicate_ids}")
    else:
        print("No duplicates in full_df['Id'] after merging")

    print(f"Final full_df shape: {full_df.shape}")

    return full_df

if __name__ == "__main__":
    main()

