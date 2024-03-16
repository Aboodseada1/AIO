import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
import time

def is_same_domain(url1, url2):
    domain1 = urlparse(url1).netloc
    domain2 = urlparse(url2).netloc
    return domain1 == domain2

def scrape_url(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        
        # Create a BeautifulSoup object to parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract the title of the page
        title = soup.title.string if soup.title else ''
        
        # Extract the main content of the page
        main_content = soup.get_text(strip=True)
        
        # Save the scraped data to the text file with the name of the page
        file_name = re.sub(r'[^a-zA-Z0-9\-]', '', title) + ".txt"
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(f"URL: {url}\n")
            file.write(f"Title: {title}\n")
            file.write(f"Main Content:\n{main_content}\n")
            file.write("\n")
        
        # Find all the clickable URLs in the page
        links = soup.find_all('a')
        
        # Initialize a set to store scraped URLs
        scraped_urls = set()
        
        # Iterate over each link and scrape its URL
        for link in links:
            href = link.get('href')
            if href:
                # Resolve relative URLs to absolute URLs
                absolute_url = urljoin(url, href)
                
                # Check if the URL belongs to the same domain and has not been scraped before
                if is_same_domain(url, absolute_url) and absolute_url not in scraped_urls:
                    print(f"Scraping related URL: {absolute_url}")
                    scrape_related_url(absolute_url)
                    scraped_urls.add(absolute_url)
                    if len(scraped_urls) >= 20:
                        break
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while scraping URL: {url}")
        print(f"Error message: {str(e)}")

def scrape_related_url(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        
        # Create a BeautifulSoup object to parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract the title of the page
        title = soup.title.string if soup.title else ''
        
        # Extract the main content of the page
        main_content = soup.get_text(strip=True)
        
        # Save the scraped data to the text file with the name of the page
        file_name = re.sub(r'[^a-zA-Z0-9\-]', '', title) + ".txt"
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(f"URL: {url}\n")
            file.write(f"Title: {title}\n")
            file.write(f"Main Content:\n{main_content}\n")
            file.write("\n")
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while scraping URL: {url}")
        print(f"Error message: {str(e)}")

# Example usage
starting_url = 'https://github.com/ollama/ollama/blob/main/docs/api.md'
print("Scraping complete.")
