import requests
import time

def scrape_url(url):
    start_time = time.time()  # Record the start time

    response = requests.get(url)

    elapsed_time = time.time() - start_time  # Calculate the elapsed time

    # Check if the request was successful and the elapsed time is within the limit
    if response.status_code == 200 and elapsed_time <= 6:
        return response.text
    elif elapsed_time > 6:
        print(f"Skipping {url} due to exceeding the time limit (elapsed time: {elapsed_time:.2f} seconds)")
    else:
        print(f"Failed to retrieve data from {url}: {response.status_code}")
    return None

# Example usage
url_to_scrape = 'https://github.com/ollama/ollama/blob/main/docs/api.md'
scraped_data = scrape_url(url_to_scrape)
if scraped_data is not None:
    print(scraped_data)
