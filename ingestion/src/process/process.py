import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import os
import re

class BookScraper:
    def __init__(self, base_url='http://books.toscrape.com/'):
        
        self.base_url = base_url
        self.books_data = []
        
        # Setup logging
        logging.basicConfig(
            filename='book_scraper.log', 
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s: %(message)s'
        )

    def _clean_price(self, price_str):
        
        try:
            # Remove non-numeric characters except decimal point
            price = re.sub(r'[^\d.]', '', price_str)
            return float(price)
        except (ValueError, TypeError):
            logging.error(f"Could not convert price: {price_str}")
            return None

    def _extract_book_details(self, book):
        
        try:
            # Title
            title = book.find('h3').find('a')['title']
            
            # Price (with encoding fix)
            price_elem = book.find('div', class_='product_price').find('p', class_='price_color')
            price = self._clean_price(price_elem.text)
            
            # Rating
            rating_class = book.find('p', class_='star-rating')['class'][1]
            rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
            rating = rating_map.get(rating_class, 0)
            
            # Availability
            availability = book.find('div', class_='product_price').find('p', class_='instock availability').text.strip()
            
            # Product URL
            product_url = self.base_url + book.find('h3').find('a')['href'].replace('../', '')
            
            return {
                'Title': title,
                'Price': price,
                'Rating': rating,
                'Availability': availability,
                'URL': product_url
            }
        except Exception as e:
            logging.error(f"Error extracting book details: {e}")
            return None

    def scrape_books(self):
       
        page_url = self.base_url + 'index.html'
        page_number = 1
        
        while page_url:
            try:
                # Fetch page
                response = requests.get(page_url)
                response.raise_for_status()
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                books = soup.find_all('article', class_='product_pod')
                
                # Extract book details
                for book in books:
                    book_details = self._extract_book_details(book)
                    if book_details:
                        self.books_data.append(book_details)
                
                # Check for next page
                next_link = soup.find('li', class_='next')
                if next_link:
                    page_number += 1
                    next_page = next_link.find('a')['href']
                    page_url = self.base_url + 'catalogue/' + next_page
                else:
                    page_url = None
                
            except requests.RequestException as e:
                logging.error(f"HTTP error occurred: {e}")
                break

    def save_to_csv(self, filename='books_data.csv'):
      
        try:
            if not self.books_data:
                logging.warning("No books data to save.")
                return False
            
            df = pd.DataFrame(self.books_data)
            
            # Drop rows with None values
            df = df.dropna()
            
            df.to_csv(filename, index=False)
            logging.info(f"Data saved to {filename}")
            return True
        except Exception as e:
            logging.error(f"Error saving to CSV: {e}")
            return False
