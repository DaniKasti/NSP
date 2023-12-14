#anonymization.py : anonymizes dataset usernames and creates two csv files. 
#One with dataset of anonymized name and one with username, anonymized name pairings 

import csv

def get_unique_username(username, user_mapping):
    for k, v in user_mapping.items():
        if v == username:
            return k
    return None

def count_lines_in_csv(file_path):
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        return sum(1 for line in csvfile)

# Read data from the existing CSV file
existing_user_entries = {}
with open('movie_reviews3.csv', 'r', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    #header = next(reader)
    for row in reader:
        if len(row) >= 4:
            key = (row[0], row[1])
            existing_user_entries[key] = [row[0], row[1], row[2], row[3]]

# Read data from the existing user mapping CSV file (if it exists)
existing_user_mapping = {}
try:
    with open('user_mapping.csv', 'r', newline='', encoding='utf-8') as mapping_csvfile:
        mapping_reader = csv.reader(mapping_csvfile)
        
        if any(mapping_reader):
            next(mapping_reader)  # Skip header
            
            for row in mapping_reader:
                existing_user_mapping[row[0]] = row[1]
except FileNotFoundError:
    pass

# If user_mapping is not empty, update the counter to continue from the last user
if existing_user_mapping:
    valid_user_ids = [user_id[1][4:] for user_id in existing_user_mapping.items() if user_id[1][4:].startswith('user') and user_id[1][4:][4:].isdigit()]
    user_counter = max(int(user_id) for user_id in valid_user_ids) + 1 if valid_user_ids else 1
else:
    user_counter = 1

# Create a new mapping between original usernames and new user identifiers
user_mapping = {}
for username in set(row[0] for row in existing_user_entries.values()):
    if username not in existing_user_mapping.values() and username not in user_mapping.values() :
        new_user_identifier = f"user{user_counter}"
        user_mapping[new_user_identifier] = username
        user_counter += 1

# Create a new CSV file with updated usernames, avoiding duplicates
new_user_entries = {}
for key, entry in existing_user_entries.items():
    new_username = get_unique_username(entry[0], user_mapping)
    if new_username:
        entry[0] = new_username
        new_user_entries[key] = entry

# Update the existing user mapping with the new entries
existing_user_mapping.update({k: v for v, k in user_mapping.items()})

# Write the updated data to the existing user mapping CSV file
with open('user_mapping.csv', 'w', newline='', encoding='utf-8') as mapping_csvfile:
    mapping_writer = csv.writer(mapping_csvfile)
    mapping_writer.writerow(['User Identifier', 'Original Username'])
    for user_identifier, original_username in existing_user_mapping.items():
        mapping_writer.writerow([user_identifier, original_username])

# Create a new CSV file with updated usernames, avoiding duplicates
with open('new_movie_reviews.csv', 'w', newline='', encoding='utf-8') as new_csvfile:
    writer = csv.writer(new_csvfile)
    #writer.writerow(header)
    for key, entry in new_user_entries.items():
        writer.writerow(entry)

def count_lines_in_csv(file_path):
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        return sum(1 for line in csvfile)

# Check the count of unique users in each file
unique_users_movie_reviews3 = set(row[0] for row in existing_user_entries.values())

unique_users_user_mapping = set(existing_user_mapping.values())
user_mapping_lines = count_lines_in_csv('user_mapping.csv')
unique_users_new_movie_reviews = set(row[0] for row in new_user_entries.values())

print("Count of Unique Users:")
print(f"In movie_reviews3.csv: {len(unique_users_movie_reviews3)}")
print(f"In user_mapping.csv: {len(unique_users_user_mapping)}")
print(f"In new_movie_reviews.csv: {len(unique_users_new_movie_reviews)}")
print(f"Number of Lines in user_mapping.csv (shud be 1 extra for header): {user_mapping_lines}")


movie_reviews3_lines = count_lines_in_csv('movie_reviews3.csv')
new_movie_reviews_lines = count_lines_in_csv('new_movie_reviews.csv')

# Check if the total number of reviews in movie_reviews3.csv matches new_movie_reviews.csv
total_reviews_movie_reviews3 = len(existing_user_entries)
total_reviews_new_movie_reviews = len(new_user_entries)

print("\nReview Counts:")
print(f"Total reviews in movie_reviews3.csv: {total_reviews_movie_reviews3}")
print(f"Total reviews in new_movie_reviews.csv: {total_reviews_new_movie_reviews}")
print(f"Number of Lines in movie_reviews3.csv: {movie_reviews3_lines}")
print(f"Number of Lines in new_movie_reviews.csv: {new_movie_reviews_lines}")
