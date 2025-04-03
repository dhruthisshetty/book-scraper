import json
import logging
from process.process import BookScraper

def lambda_handler(inputDA, context):
    try:
        # Extract scraper configuration
        scraper_config = inputDA.get('scraper_input', {})
        scraper_name = scraper_config.get('scraper_name', 'default_scraper')
        run_scraper_id = scraper_config.get('run_scraper_id', 'unknown')
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO, 
            format=f'%(asctime)s - %(levelname)s - Scraper: {scraper_name} - ID: {run_scraper_id} - %(message)s'
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
    try:
        # Load configuration from run_scraper.json
        with open('run_scraper.json', 'r') as config_file:
            scraper_config = json.load(config_file)
            
        # Call lambda handler with loaded configuration
        result = lambda_handler(scraper_config, "")
        print(json.dumps(result, indent=2))
    except FileNotFoundError:
        print("Error: run_scraper.json file not found.")
        exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON in run_scraper.json file.")
        exit(1)
    except Exception as e:
        print(f"Error executing scraper: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
