import requests
from bs4 import BeautifulSoup
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
count=10
# The base URL of the IMDb movie review page
#Make sure you dont change filter in url whatsoever
#base_url = "https://www.imdb.com/title/tt0122529/reviews/?ref_=tt_ql_2"

def extract_review_count(soup):
    review_count_element = soup.find('div', class_='header').find('span')
    if review_count_element:
        review_count_text = review_count_element.get_text(strip=True)
        try:
            # Extract the numeric part and remove commas
            review_count = int(''.join(filter(str.isdigit, review_count_text)))
            return review_count
        except ValueError:
            print(f"Failed to convert '{review_count_text}' to an integer.")
            return None
    else:
        print("Failed to find the review count element.")
        return None


def write_movie_review_count_to_csv(movie_name, review_count):
    with open('movie_names_count.csv', 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([movie_name, review_count])


# Send a GET request to the URL
def scrape_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    else:
        print(f"Failed to retrieve the webpage {url}. Status code:", response.status_code)
        return None
    
 # Load base URLs from a CSV file
base_urls = []
with open('base_urls.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        base_urls.append(row[0])

# Iterate through each base URL
for base_url in base_urls:
    print(f"Scraping reviews for {base_url}")   

    # Create a dictionary to track entries by username and movie
    user_entries = {}

    # Extract the movie name
    soup = scrape_page(base_url)
    time.sleep(4)
    movie_name_element = soup.find('a', itemprop='url')
    movie_name = movie_name_element.get_text(strip=True) if movie_name_element else "No movie name"
    review_count = extract_review_count(soup)

    if review_count:
      write_movie_review_count_to_csv(movie_name, review_count)

    num_lines_before = 0
    with open('movie_reviews3.csv', 'r', newline='') as csvfile:
        num_lines_before = sum(1 for line in csvfile)


    # Load existing data from the CSV file into the dictionary
    with open('movie_reviews3.csv', 'r', newline='') as csvfile:
        csv_reader = csv.reader(csvfile)

        if csvfile.tell() != 0:
            for row in csv_reader:
                username, existing_movie, existing_rating, existing_date = row
                user_entries[(username, existing_movie)] = [username, existing_movie, existing_rating, existing_date]

    # Create or open a CSV file to store the data
    with open('movie_reviews3.csv', 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)

        # Do not write the header if the file is empty
        if csvfile.tell() == 0:
            csv_writer.writerow(["Username", "Movie Name", "Rating", "Date of Review"])

        # Initialize the web driver
        driver = webdriver.Chrome()

        try:
            # Navigate to the base URL
            driver.get(base_url)
            time.sleep(5)  # Let the page load

            while True:
                if review_count>25:
                    # Using WebDriverWait for better reliability
                    load_more_button = WebDriverWait(driver, 12).until(
                        EC.element_to_be_clickable((By.ID, 'load-more-trigger'))
                    )

                    # Scroll the "Load More" button into view to make it clickable
                    driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                    time.sleep(3)

                    # Click the "Load More" button to load more reviews
                    load_more_button.click()

                time.sleep(5)  # Let the page load after clicking "Load More"

                # Extract and process the reviews
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                review_containers = soup.find_all('div', class_='lister-item-content')

                for review in review_containers:
                    # Extract the username, rating, and date
                    username_element = review.find('span', class_='display-name-link').find('a')
                    username = username_element.get_text() if username_element else "No username"

                    rating_span = review.find('span', class_='point-scale')
                    rating = rating_span.find_previous('span').get_text() if rating_span else "No rating"

                    date_element = review.find('span', class_='review-date')
                    date = date_element.get_text() if date_element else "No date"

                    # Create a unique key combining username and movie
                    key = (username, movie_name)

                    # Check if this username and movie combination has been encountered before
                    if key in user_entries:
                        # If the same combination is already in the dictionary, keep the original rating
                        rating = user_entries[key][2]
                    else:
                        # If it's a new combination, create a new entry in the dictionary
                        user_entries[key] = [username, movie_name, rating, date]

                        # Write the data from the dictionary to the CSV file
                        csv_writer.writerow([username, movie_name, rating, date])

                # Check if the "Load More" button is still visible
                if not load_more_button.is_displayed():
                    break

                time.sleep(2)  # Add a delay to avoid overloading the website

        finally:
            # Close the web driver
            driver.quit()



    # Get the number of lines after writing to the CSV file
    num_lines_after = 0
    with open('movie_reviews3.csv', 'r', newline='') as csvfile:
        num_lines_after = sum(1 for line in csvfile)


    difference_mr3 = num_lines_after - num_lines_before

    # Calculate review_count/difference_mr3 and review_count-difference_mr3
    if difference_mr3 != 0:
        percent_gathered_ratio = difference_mr3 / review_count
        percent_gathered_difference = review_count - difference_mr3
    else:
        percent_gathered_ratio = 0
        percent_gathered_difference = 0

    # Save the results to PercentGathered.csv
    with open('PercentGathered.csv', 'a', newline='') as percent_csv:
        percent_csv_writer = csv.writer(percent_csv)

        # Check if the file is empty and write the header if needed
        if percent_csv.tell() == 0:
            percent_csv_writer.writerow(["Movie name","PercentGatheredRatio", "PercentGatheredDifference", "Advertised review count", "difference_mr3"])

        # Append the calculated values to the CSV file
        percent_csv_writer.writerow([movie_name, percent_gathered_ratio, percent_gathered_difference, review_count, difference_mr3])



    # Print the results
    print("---------------------------------------------------------------------------------------------")
    print(f"Scraping completed for movie:{movie_name} ")
    print(f"Number of lines before: {num_lines_before}")
    print(f"Number of lines after: {num_lines_after}")
    print(f"Difference:lines before & after in m_r3.csv: {difference_mr3}")
    print(f"review_count advertised on webpage: {review_count}")
    print(f"review_count-(Difference:lines before & after in m_r3.csv): {review_count-difference_mr3}")
    print(f"Percent gathered: {percent_gathered_ratio}")
    print("---------------------------------------------------------------------------------------------")