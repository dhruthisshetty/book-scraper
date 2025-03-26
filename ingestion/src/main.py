import json
import logging
from process.process import BookScraper

def lambdaHandler(inputDA, context):
    
    try:
        # Extract scraper configuration
        scraper_config = inputDA.get('scraper_input', {})
        scraper_name = scraper_config.get('scraper_name', 'default_scraper')
        run_scraper_id = scraper_config.get('run_scraper_id', 'unknown')
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s - Scraper: {} - ID: {} - %(message)s'.format(
                scraper_name, run_scraper_id
            )
        )
        
        # Initialize scraper
        scraper = BookScraper()
        
        # Scrape books
        logging.info("Starting book scraping process")
        scraper.scrape_books()
        
        # Save to CSV
        csv_filename = f'{scraper_name}_{run_scraper_id}_books.csv'
        save_result = scraper.save_to_csv(filename=csv_filename)
        
        # Prepare response
        response = {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Book scraping completed successfully",
                "scraper_name": scraper_name,
                "run_scraper_id": run_scraper_id,
                "total_books_scraped": len(scraper.books_data),
                "output_file": csv_filename,
                "status": "success"
            })
        }
        
        logging.info(f"Scraping completed. Total books: {len(scraper.books_data)}")
        
        return response
    
    except Exception as e:
        # Log and return error response
        logging.error(f"Scraping failed: {str(e)}")
        
        error_response = {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Book scraping failed",
                "scraper_name": scraper_config.get('scraper_name', 'unknown'),
                "run_scraper_id": scraper_config.get('run_scraper_id', 'unknown'),
                "error": str(e),
                "status": "failed"
            })
        }
        
        return error_response

def main():
    
    # Example input dictionary for local testing
    inputDA = {
        "scraper_input": {
            "scraper_name": "csv_100",
            "run_scraper_id": "100"
        }
    }
    
    # Call lambda handler for testing
    result = lambdaHandler(inputDA, "")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
