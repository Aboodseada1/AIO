import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

def get_user_input():
    url = st.sidebar.text_input("What do you want to scrape today? (Please paste the URL): ")
    return url.strip()

def get_same_domain_preference():
    response = st.sidebar.radio("Do you want the fetched URLs to be from the same domain?", ('Yes', 'No'))
    return response == 'Yes'

def scrape_url(url, same_domain=True):
    try:
        # Set Firefox browser binary location
        binary = FirefoxBinary('C:\\Program Files\\Mozilla Firefox\\firefox.exe')  # Update the path accordingly
        
        # Set up Selenium Firefox webdriver
        driver = webdriver.Firefox(firefox_binary=binary)
        
        # Load the URL
        driver.get(url)

        # Extract page title and content
        page_title = driver.title
        page_content = driver.page_source
        
        # Extract page URLs based on the domain if specified by the user
        if same_domain:
            base_domain = urlparse(url).netloc
            page_urls = set()
            for link in driver.find_elements(By.TAG_NAME, 'a'):
                href = link.get_attribute('href')
                if href:
                    parsed_href = urlparse(href)
                    if parsed_href.netloc == base_domain:
                        page_urls.add(href)
        else:
            page_urls = set()
            for link in driver.find_elements(By.TAG_NAME, 'a'):
                href = link.get_attribute('href')
                if href:
                    page_urls.add(href)
        
        # Parse HTML content with BeautifulSoup
        soup = BeautifulSoup(page_content, 'html.parser')
        
        # Get the text content
        text_content = soup.get_text(separator=' ')
        
        # Remove excess whitespace and newlines between sentences
        text_content = re.sub(r'\s+', ' ', text_content)
        
        # Display the scraped data
        st.subheader("Scraped Page Data:")
        
        # Display page title and content in the first column
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"Page Title: {page_title}")
            st.write("Page Content:")
            st.write(text_content)
        
        # Display page URLs in the second column
        with col2:
            if page_urls:
                st.write("Page URLs:")
                for page_url in page_urls:
                    st.write(page_url)
            else:
                st.write("No page URLs found.")
        
    except Exception as e:
        st.error(f"An error occurred during scraping: {e}")

def main():
    st.sidebar.title("Web Scraping Tool")

    url_to_scrape = get_user_input()
    same_domain_preference = get_same_domain_preference()
    if url_to_scrape:
        if st.sidebar.button("SCRAP!", key="scrap_btn", type="primary"):
            scrape_url(url_to_scrape, same_domain=same_domain_preference)

if __name__ == "__main__":
    main()
