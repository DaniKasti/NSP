import csv
from collections import defaultdict

def get_users_with_exact_reviews(user_entries, exact_reviews):
    users_with_exact_reviews = [username for username, count in user_entries.items() if count == exact_reviews]
    return users_with_exact_reviews

# Initialize a dictionary to store user entries
user_entries = defaultdict(list)

# Initialize a set to store unique movie names
unique_movies = set()

# Read data from the CSV file
with open('movie_reviews3.csv', 'r', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Skip header if present
    for row in reader:
        # Ensure that the row has at least four elements
        if len(row) >= 4:
            key = (row[0], row[1])  # Using username and movie_name as the key
            user_entries[key] = [row[0], row[1], row[2], row[3]]
            unique_movies.add(row[1])

# Initialize counters
unique_users = set()
users_by_movies = defaultdict(int)

# Count unique users and users by the number of movies
for key in user_entries:
    username = key[0]
    unique_users.add(username)
    users_by_movies[username] += 1

# Count the number of users with 1, 2, 3, etc. movies
users_count_by_movies = defaultdict(int)
for count in users_by_movies.values():
    users_count_by_movies[count] += 1

# Print the results with sorted order
print(f"Number of unique users: {len(unique_users)}")
print("Number of users by the number of movies:")
for count, user_count in sorted(users_count_by_movies.items()):
    print(f"{count} movie(s): {user_count} user(s)")

# Calculate the mean number of movies
mean_movies_per_user = sum(users_by_movies.values()) / len(unique_users)
# Print the mean number of movies per user
print(f"\nMean number of movies per user: {mean_movies_per_user:.2f}")

# Print the number of movies and list their names vertically
print(f"\nNumber of movies: {len(unique_movies)}")
print("List of movies:")
for movie_name in sorted(unique_movies):
    print(movie_name)

# Example: Get users with exactly 8 movie reviews
exact_reviews = 45
users_with_exact_reviews = get_users_with_exact_reviews(users_by_movies, exact_reviews)
print(f"\nUsers with exactly {exact_reviews} movie reviews: {users_with_exact_reviews}")





