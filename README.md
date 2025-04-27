# Book Data Scraper

## Project Overview
This is a web scraping project designed to extract book details from the "Books to Scrape" website (http://books.toscrape.com/). The scraper collects comprehensive information about books, including title, price, rating, availability, and product URL.

## Features
- Scrape book details from multiple pages
- Extract key book information
- Save data to CSV
- Comprehensive error handling
- Detailed logging
- Extensive test coverage

## Project Structure
```
ingestion/
│
├── src/
│   ├── process/
│   │   └── process.py
│   ├── tests/
│   │   └── test_book_scraper.py
│   └── main.py
│
└── requirements.txt
```

## Prerequisites
- Python 3.8+
- pip

## Installation
1. Clone the repository:
```bash
git clone https://github.com/dhruthisshetty/book-scraper.git
cd ingestion
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
Run the scraper:
```bash
python src/main.py
```

## Running Tests
```bash
pytest src/tests/test.py
```

## Technologies Used
- Python
- Requests
- BeautifulSoup
- Pandas
- Power BI (for data visualization and analytics)

