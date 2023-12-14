import math
import itertools
from datetime import datetime
from collections import defaultdict

def load_csv(file_path):
    data = []
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            data.append(row)
    return data

def load_user_mapping(file_path):
    user_mapping = {}
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        for row in reader:
            user_mapping[row[1]] = row[0]  # Reverse the order
    return user_mapping


def load_user_mapping2(file_path):
    i=0
    user_mappingT = {}
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        for row in reader:
          user_mappingT[i] = row 
    return user_mappingT

def calculate_similarity(auxiliary_entry, user_entry, movie_review_counts):
    aux_rating = 0 if auxiliary_entry[2] == 'No rating' else int(auxiliary_entry[2])
    user_rating = 0 if user_entry[2] == 'No rating' else int(user_entry[2])

    # if aux_rating == 0 and user_rating == 0:
    #     rating_similarity = 0
    # else:
    rating_similarity = 1/(1+abs(aux_rating - user_rating)/10)
       # new = abs(aux_rating - user_rating)
        #rating_similarity = 1/(.01+abs(aux_rating - user_rating)/10)
        # if new !=0:
        #     new = math.log(abs(aux_rating - user_rating) !=0)
        # rating_similarity = 1/(.01+new)

    aux_date = datetime.strptime(auxiliary_entry[3], '%d %B %Y')
    user_date = datetime.strptime(user_entry[3], '%d %B %Y')
    
    # Use reciprocal directly to achieve normalization
    date_difference_years = abs((aux_date - user_date).days)/365
    # if(date_difference_years)!=0:
    #     date_similarity =math.log(date_difference_years)
    date_similarity = 1 / (1 + date_difference_years)
    
    movie_review_count = movie_review_counts[user_entry[1]]
    
    # Lower review count indicates a more distinctive user
    review_count_similarity = 1 / math.log(1 + movie_review_count)
    
    # Weighted sum of normalized similarities
    #total_similarity = 4*rating_similarity + 2*date_similarity + 5*review_count_similarity   
    #total_similarity = 0.45*rating_similarity + 0.15*date_similarity + 0.4*review_count_similarity
    #total_similarity = 0.35*rating_similarity + 0.35*date_similarity + 0.3*review_count_similarity
    total_similarity = (rating_similarity + date_similarity)*review_count_similarity
    return total_similarity

def deanonymize_single_user(auxiliary_user, anonymized_data, movie_review_counts, user_mapping, target_name):
    user_total_similarity_scores = defaultdict(float)

    for aux_entry in auxiliary_user:
        for user_entry in anonymized_data:
            if user_entry[1] == aux_entry[1]:  # Matching movie
                similarity = calculate_similarity(aux_entry, user_entry, movie_review_counts)
                user_id = user_entry[0]

                user_total_similarity_scores[user_id] += similarity
    # Find the top five users with the highest total similarity scores
    top_users = sorted(user_total_similarity_scores.items(), key=lambda x: x[1], reverse=True)[:5]
    deanonymized_data = defaultdict(list)

    # print("\nTop Five Users:")
    # for user_id, total_similarity_score in top_users:
    #     # Display deanonymized results
    #     deanonymized_user = f"UserID: {user_id}"
    #     original_username = user_mapping.get(user_id, "Unknown user")
    #     print(f"\nDeanonymized User ID: {deanonymized_user}")
    #     print(f"Original Username: {original_username}")
    #     print(f"Total Similarity Score: {total_similarity_score}")
        
    #     deanonymized_data['DeanonymizedUserID'].append(deanonymized_user)
    #     deanonymized_data['OriginalUsername'].append(original_username)
    #     deanonymized_data['TotalSimilarityScore'].append(total_similarity_score)

    

    reversed_dict = {value: key for key, value in user_mapping.items()}
    # Find the person being deanonymized in the auxiliary data
    target_user_id = reversed_dict.get(target_name, "Unknown user")
    target_rank = None
    target_score = user_total_similarity_scores.get(str(target_user_id), "Unknown score")

    sorted_users = sorted(user_total_similarity_scores.items(), key=lambda x: x[1], reverse=True)

    for rank, (user_id, total_similarity_score) in enumerate(sorted_users, start=1):
        if user_id == target_user_id:
            target_rank = rank
        # if rank<16:
        #   print("----------------------------------------------")
        #   print(user_id, total_similarity_score)

    # Print the rank and score of the person being deanonymized in the auxiliary data
    #if target_rank is not None:
    print(f"\nPerson Being Deanonymized in Aux Data:")
    print(f"User ID: {target_user_id}")
    print(f"Rank: {target_rank}")
    print(f"Score: {target_score}")
    
    if len(top_users) >= 2:
        score_difference = abs(top_users[0][1] - top_users[1][1])
    if score_difference >= 0.05:
        print("------Threshold: true")
    else:
        print("-----Threshold: false")

    return deanonymized_data

# Simulated auxiliary data
auxiliary_data_path = 'auxillary_data_pm1_d30_25%.csv'
auxiliary_data = load_csv(auxiliary_data_path)

# Simulated anonymized data
anonymized_data_path = 'new_movie_reviews.csv'
anonymized_data = load_csv(anonymized_data_path)

# Simulated movie review counts
movie_review_count_path = 'movie_names_count.csv'
movie_review_count_data = load_csv(movie_review_count_path)
movie_review_counts = {row[0]: int(row[1]) for row in movie_review_count_data}

# Load user mapping data
user_mapping_path = 'user_mapping.csv'
user_mapping = load_user_mapping(user_mapping_path)
user_mappingT = load_user_mapping2(user_mapping_path)
# Deanonymize the data for each user separately
for user_id, group in itertools.groupby(auxiliary_data, key=lambda x: x[0]):
    group_data = list(group)
    deanonymized_data = deanonymize_single_user(group_data, anonymized_data, movie_review_counts, user_mapping, group_data[0][0])
