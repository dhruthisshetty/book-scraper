import os
import pandas as pd
import pytest
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from process.process import BookScraper

class TestBookScraper:
    @pytest.fixture
    def scraper(self):
        return BookScraper()
    
    def test_csv_file_download(self, scraper):
        scraper.scrape_books()
        scraper.save_to_csv()
        assert os.path.exists('books_data.csv')
    
    def test_csv_extraction(self, scraper):
        scraper.scrape_books()
        scraper.save_to_csv()
        
        # Read CSV
        df = pd.read_csv('books_data.csv')
        assert not df.empty
    
    def test_file_type(self):
        assert os.path.exists('books_data.csv')
        with open('books_data.csv', 'r') as f:
            first_line = f.readline().strip()
            assert ',' in first_line  # CSV should have comma-separated values
    
    def test_data_structure(self):
        df = pd.read_csv('books_data.csv')
        expected_columns = ['Title', 'Price', 'Rating', 'Availability', 'URL']
        
        # Check column names
        assert list(df.columns) == expected_columns
        
        # Check data types
        assert df['Price'].dtype in ['float64', 'float32']
        assert df['Rating'].dtype in ['int64', 'int32']
    
    def test_handle_missing_data(self, scraper):
        scraper.scrape_books()
        scraper.save_to_csv()
        
        df = pd.read_csv('books_data.csv')
        
        # Check no rows are completely empty
        assert df.dropna().shape[0] > 0
