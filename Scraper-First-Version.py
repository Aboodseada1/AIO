import os
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import time
import random
import requests
import json
import csv
from googlesearch import search

url = "http://localhost:11434/api/generate"

headers = {
    'Content-Type': 'application/json',
}

conversation_history = []

def generate_response(prompt):
    conversation_history.append(prompt)

    full_prompt = "\n".join(conversation_history)

    data = {
        "model": "mistral",
        "stream": False,
        "prompt": full_prompt,
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_text = response.text
        data = json.loads(response_text)
        actual_response = data["response"]
        conversation_history.append(actual_response)
        return actual_response
    else:
        print("Error:", response.status_code, response.text)
        return None

def search_queries(prompt, num_queries):
    queries = []
    # Use Ollama to generate search queries based on the prompt
    response = generate_response(f"Generate {num_queries} search queries for Google based on the following prompt: {prompt}")
    queries = response.split("\n")
    queries = [query.split(". ", 1)[1].replace('"', '') for query in queries if query.strip()]  # Extract the actual query and remove quotes

    st.subheader("Ollama Conversation")
    st.write(f"Prompt: {prompt}")
    st.write(f"Ollama Response:")
    st.write(response)

    return queries

def scrape_google_search(query, num_links=10):
    try:
        search_results = []
        for result in search(query, num_results=num_links):
            search_results.append(result)
            if len(search_results) >= num_links:
                break
        return search_results

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def scrape_url(url):
    try:
        # Initialize WebDriver with Firefox
        options = Options()
        options.binary_location = 'C:\\Program Files\\Mozilla Firefox\\firefox.exe'  # Update the path accordingly
        driver = webdriver.Firefox(options=options)

        # Load the URL
        driver.get(url)
        
        # Wait for the page to load completely (you may need to adjust the waiting time based on page load speed)
        time.sleep(5)

        # Extract page content
        page_content = driver.page_source

        # Parse HTML content with BeautifulSoup
        soup = BeautifulSoup(page_content, 'html.parser')

        # Get the text content
        text_content = soup.get_text(separator=' ')

        # Remove excess whitespace and newlines between sentences
        text_content = re.sub(r'\s+', ' ', text_content)

        # Extract emails, phone numbers, names, and company names using regular expressions
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text_content)
        phone_numbers = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text_content)
        names = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', text_content)
        company_names = re.findall(r'\b[A-Z][a-zA-Z]* (Inc\.|LLC|Ltd\.|Co\.|Corporation)\b', text_content)

        # Close the browser
        driver.quit()

        return emails, phone_numbers, names, company_names

    except Exception as e:
        # Print the error message
        print(f"An error occurred during scraping: {e}")
        # Close the browser if it's still open
        if 'driver' in locals():
            driver.quit()
        # Return empty lists for data
        return [], [], [], []


def main():
   with st.container():
    st.image("https://upload.wikimedia.org/wikipedia/commons/8/85/AbdelFattah_Elsisi_%28cropped%29.jpg", width=300)
    st.title('🦜🔗 Chat With Website')
    st.subheader('Input your search query, specify the number of search queries and links to scrape, and receive the desired information.')

    prompt = st.text_input("What do you want to search for today?")
    num_queries = st.number_input("How many search queries do you want to generate?", min_value=1, value=1, step=1)
    num_links = st.number_input("How many links do you want to take from each search query?", min_value=1, value=10, step=1)

    if st.button("Submit Query", type="primary"):
        try:
            st.write("Generating search queries...")
            search_queries_list = search_queries(prompt, num_queries)
            st.write(f"Generated {len(search_queries_list)} search queries.")

            emails = []
            phone_numbers = []
            names = []
            company_names = []

            progress_bar = st.progress(0)

            # Set up Selenium Firefox webdriver with options
            options = Options()
            options.binary_location = 'C:\\Program Files\\Mozilla Firefox\\firefox.exe'  # Update the path accordingly
            driver = webdriver.Firefox(options=options)
            
            st.write("Scraping Search Result URLs for each query:")

            search_result_urls = []

            for i, query in enumerate(search_queries_list):
                st.write(f"Searching for query {i+1}/{len(search_queries_list)}: {query}")
                
                # Scrape search result URLs for the current query
                result_urls = scrape_google_search(query, num_links)
                search_result_urls.extend(result_urls)
                
                # Save the search result URLs to a text file
                with open(f"search_results_query_{i+1}.txt", "w") as file:
                    file.write("\n".join(result_urls))
                
                progress_bar.progress((i + 1) / len(search_queries_list))
            
            st.write("Scraping Search Result URLs completed!")
            
            st.write("Scraping data from Search Result URLs:")
            
            if search_result_urls:  # Check if search_result_urls is not empty
                for i, url in enumerate(search_result_urls):
                    st.write(f"Scraping URL {i+1}/{len(search_result_urls)}: {url}")
                    scraped_data = scrape_url(url)
                    emails.extend(scraped_data[0])
                    phone_numbers.extend(scraped_data[1])
                    names.extend(scraped_data[2])
                    company_names.extend(scraped_data[3])

                st.write("Scraping data from Search Result URLs completed!")
                st.write(f"GOT Total ({len(search_queries_list)} search queries * {num_links} links per query = {len(search_result_urls)} leads)")

                # Close the browser
                driver.quit()

                # Save the scraped data to a CSV file
                csv_filename = "Scraped_Data.csv"
                with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Email", "Phone Number", "Name", "Company Name"])
                    max_rows = max(len(emails), len(phone_numbers), len(names), len(company_names))
                    for i in range(max_rows):
                        email = emails[i] if i < len(emails) else ""
                        phone = phone_numbers[i] if i < len(phone_numbers) else ""
                        name = names[i] if i < len(names) else ""
                        company = company_names[i] if i < len(company_names) else ""
                        writer.writerow([email, phone, name, company])

                st.success(f"Scraped data saved to {csv_filename}")
            else:
                st.warning("No search result URLs found. Please check your search queries.")

        except Exception as e:
            st.error(f"An error occurred: {e}")
            if 'driver' in locals():
                driver.quit()  # Close the browser in case of error

            # Log the contents of search_result_urls
            st.error(f"search_result_urls: {search_result_urls}")

if __name__ == '__main__':
    main()

