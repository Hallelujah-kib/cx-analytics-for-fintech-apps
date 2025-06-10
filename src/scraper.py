import os
import time
import logging
import pandas as pd
from datetime import datetime
from google_play_scraper import reviews, Sort
from typing import Dict, List, Optional
import json

class PlayStoreScraper:
    """A class to scrape reviews from Google Play Store for specified apps."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize the scraper with configuration.
        
        Args:
            config_path: Path to JSON config file. If None, uses default config.
        """
        # Set up directories
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.base_dir, 'data')
        self.logs_dir = os.path.join(self.base_dir, 'logs')
        
        # Create directories if they don't exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, 'scraped_data'), exist_ok=True)
        
        # Set up logging
        self._setup_logging()
        
        # Load configuration
        self.config = self._load_config(config_path)
        
    def _setup_logging(self):
        """Configure logging to both file and console."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.logs_dir, 'scraper.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file or use defaults."""
        default_config = {
            "APP_IDS": {
                "CBE": "com.combanketh.mobilebanking",
                "BOA": "com.boa.boaMobileBanking",
                "Dashen": "com.dashen.dashensuperapp"
            },
            "DEFAULT_COUNT": 500,
            "MAX_RETRIES": 3,
            "RETRY_DELAY": 5,
            "LANG": "en",
            "COUNTRY": "us"
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load config file: {e}. Using default config.")
                return default_config
        return default_config
        
    def fetch_reviews(self, app_name: str, app_id: str, count: int = None) -> List[Dict]:
        """
        Fetch reviews for a single app.
        
        Args:
            app_name: Name of the app (for logging)
            app_id: Package ID of the app in Play Store
            count: Number of reviews to fetch
            
        Returns:
            List of review dictionaries
        """
        count = count or self.config["DEFAULT_COUNT"]
        all_reviews = []
        continuation_token = None
        retries = 0
        
        while len(all_reviews) < count and retries < self.config["MAX_RETRIES"]:
            try:
                self.logger.debug(f"Fetching batch {len(all_reviews)}-{len(all_reviews)+min(500, count - len(all_reviews))} for {app_name}")
                result, continuation_token = reviews(
                    app_id,
                    lang=self.config["LANG"],
                    country=self.config["COUNTRY"],
                    sort=Sort.NEWEST,
                    count=min(500, count - len(all_reviews)),
                    continuation_token=continuation_token
                )
                
                for r in result:
                    all_reviews.append({
                        'review_text': r['content'],
                        'rating': r['score'],
                        'date': r['at'].strftime('%Y-%m-%d'),
                        'bank_name': app_name,
                        'source': 'Google Play'
                    })
                    
                if continuation_token is None:
                    break
                    
                time.sleep(1)  # Rate limiting
                retries = 0  # Reset retry counter after success

            except Exception as e:
                retries += 1
                self.logger.error(f"Attempt {retries} failed for {app_name}: {str(e)}")
                if retries < self.config["MAX_RETRIES"]:
                    time.sleep(self.config["RETRY_DELAY"])
                else:
                    self.logger.error(f"Max retries reached for {app_name}")
                    break
                    
        self.logger.info(f"Collected {len(all_reviews)} reviews for {app_name}")
        return all_reviews[:count]
        
    def scrape_all_reviews(self, count_per_app: int = None, save_csv: bool = True) -> pd.DataFrame:
        """
        Scrape reviews for all configured apps.
        
        Args:
            count_per_app: Number of reviews to fetch per app
            save_csv: Whether to save results to CSV
            
        Returns:
            DataFrame containing all reviews
        """
        count_per_app = count_per_app or self.config["DEFAULT_COUNT"]
        all_data = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for bank, app_id in self.config["APP_IDS"].items():
            try:
                self.logger.info(f"Starting scrape for {bank}")
                reviews_data = self.fetch_reviews(bank, app_id, count=count_per_app)
                all_data.extend(reviews_data)

                if save_csv:
                    filename = os.path.join(
                        self.data_dir, 
                        'scraped_data', 
                        f"{bank}_reviews_{timestamp}.csv"
                    )
                    df = pd.DataFrame(reviews_data)
                    df.to_csv(filename, index=False)
                    self.logger.info(f"Saved {len(reviews_data)} reviews to {filename}")
                    
            except Exception as e:
                self.logger.error(f"Error processing {bank}: {str(e)}")
                continue
                
        return pd.DataFrame(all_data)