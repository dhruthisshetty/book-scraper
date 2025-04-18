import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import os
import re
from urllib.parse import urljoin

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
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        
        # Get latest GBP to USD exchange rate
        self.exchange_rate = self._get_exchange_rate()
        logging.info(f"Current GBP to USD exchange rate: {self.exchange_rate}")
    
    def _get_exchange_rate(self):
        """Fetch the current GBP to USD exchange rate from an API"""
        try:
            # Using Exchange Rate API (you might need to register for an API key)
            response = requests.get('https://api.exchangerate-api.com/v4/latest/GBP')
            data = response.json()
            
            # Get USD rate from the response
            usd_rate = data['rates']['USD']
            return usd_rate
        except Exception as e:
            logging.error(f"Failed to get exchange rate: {e}")
            # Default fallback rate if API call fails
            return 1.30  # Approximate GBP to USD rate
    
    def _clean_price(self, price_str):
        try:
            # Remove non-numeric characters except decimal point
            price_gbp = re.sub(r'[^\d.]', '', price_str)
            price_gbp = float(price_gbp)
            
            # Convert to USD
            price_usd = price_gbp * self.exchange_rate
            
            return price_gbp, round(price_usd, 2)
        except (ValueError, TypeError):
            logging.error(f"Could not convert price: {price_str}")
            return None, None

    def _extract_book_details(self, book):
        try:
            # Title
            title = book.find('h3').find('a')['title']

            # Price (with encoding fix and conversion)
            price_elem = book.find('div', class_='product_price').find('p', class_='price_color')
            price_gbp, price_usd = self._clean_price(price_elem.text) if price_elem else (0.0, 0.0)

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
                'Price_GBP': price_gbp,
                'Price_USD': price_usd,
                'Rating': rating,
                'Availability': availability,
                'URL': product_url
            }
        except Exception as e:
            logging.error(f"Error extracting book details: {e}")
            return None

    def scrape_books(self):
        total_books = 0
        try:
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            category_container = soup.find('div', class_='side_categories')
            category_links = category_container.find_all('a')
            
            for category_link in category_links:
                category_url = urljoin(self.base_url, category_link['href'])
                if category_url == self.base_url:
                    continue
                self._scrape_category(category_url)
            
            self._scrape_category(urljoin(self.base_url, 'catalogue/'))

        except Exception as e:
            logging.error(f"Error during category scraping: {e}")

    def _scrape_category(self, category_url):
        """Scrape all books within a category including pagination"""
        logging.info(f"Scraping category: {category_url}")
        current_url = category_url
        
        while current_url:
            try:
                response = requests.get(current_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract all books on current page
                books = soup.find_all('article', class_='product_pod')
                books_count = 0
                
                for book in books:
                    book_details = self._extract_book_details(book)
                    if book_details:
                        # Check for duplicates before adding
                        if not any(existing['URL'] == book_details['URL'] for existing in self.books_data):
                            self.books_data.append(book_details)
                            books_count += 1
                
                # Check for next page
                next_link = soup.find('li', class_='next')
                if next_link:
                    next_page = next_link.find('a')['href']
                    # Handle relative URLs correctly
                    if '/' in current_url:
                        base_dir = current_url.rsplit('/', 1)[0] + '/'
                    else:
                        base_dir = current_url
                    current_url = urljoin(base_dir, next_page)
                else:
                    current_url = None
                    
            except requests.RequestException as e:
                logging.error(f"HTTP error occurred when scraping {current_url}: {e}")
                current_url = None
    
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

# Example usage
if __name__ == "__main__":
    scraper = BookScraper()
    scraper.scrape_books()
    scraper.save_to_csv()
