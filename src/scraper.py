import os
import time
import logging
import pandas as pd
from datetime import datetime
from google_play_scraper import reviews, Sort
from typing import Dict, List, Optional
import json

class PlayStoreScraper:
    """Enhanced Google Play Store review scraper with better error handling."""
    
    def __init__(self, config_path: str = None):
        self._setup_paths()
        self._setup_logging()
        self.config = self._load_config(config_path)
        
        
    def _setup_paths(self):
        """Initialize all required directories."""
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.base_dir, 'data', 'scraped_data')
        self.output_dir = os.path.join(self.base_dir, 'data', 'cleaned_data')
        os.makedirs(self.data_dir, exist_ok=True)
        

    def _setup_logging(self):
        """Configure dual logging (file + console)."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.output_dir, 'cleaning.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load config with enhanced validation."""
        default_config = {
            "APP_IDS": {
                "CBE": "com.combanketh.mobilebanking",
                "BOA": "com.boa.boaMobileBanking", 
                "Dashen": "com.dashen.dashensuperapp"
            },
            "DEFAULT_COUNT": 450,
            "MAX_RETRIES": 3,
            "RETRY_DELAY": 5,
            "REQUEST_TIMEOUT": 30,
            "LANG": "en",
            "COUNTRY": "us"
        }
        if config_path:
            try:
                with open(config_path) as f:
                    user_config = json.load(f)
                    return {**default_config, **user_config}
            except Exception as e:
                self.logger.warning(f"Config load failed: {e}. Using defaults.")
        return default_config

    def fetch_reviews(self, app_name: str, app_id: str, count: int = None) -> List[Dict]:
        """Fetch reviews with timeout and retry logic."""
        count = count or self.config["DEFAULT_COUNT"]
        all_reviews = []
        continuation_token = None
        
        while len(all_reviews) < count:
            try:
                result, continuation_token = reviews(
                    app_id,
                    lang=self.config["LANG"],
                    country=self.config["COUNTRY"],
                    sort=Sort.NEWEST,
                    count=min(200, count - len(all_reviews)),
                    continuation_token=continuation_token
                )
                all_reviews.extend([{
                    'review_text': r['content'],
                    'rating': r['score'],
                    'date': r['at'].strftime('%Y-%m-%d'),
                    'bank_name': app_name,
                    'source': 'Google Play',
                    'app_id': app_id
                } for r in result])
                
                if not continuation_token:
                    break
                    
                time.sleep(1.5)  # Gentle rate limiting
                
            except Exception as e:
                self.logger.error(f"Failed batch for {app_name}: {e}")
                time.sleep(5)
                if len(all_reviews) >= count * 0.8:  # Accept partial results
                    break
                    
        return all_reviews[:count]

    def scrape_all_reviews(self, count_per_app: int = None) -> pd.DataFrame:
        """Scrape all apps with progress tracking."""
        results = []
        count_per_app = count_per_app or self.config["DEFAULT_COUNT"]
        
        for bank, app_id in self.config["APP_IDS"].items():
            self.logger.info(f"🔄 Scraping {bank}...")
            try:
                reviews = self.fetch_reviews(bank, app_id, count_per_app)
                df = pd.DataFrame(reviews)
                
                # Save individual app data
                timestamp = datetime.now().strftime('%Y%m%d_%H%M')
                df.to_csv(
                    os.path.join(self.data_dir, f'{bank}_reviews_{timestamp}.csv'),
                    index=False
                )
                results.append(df)
                self.logger.info(f"✅ {bank}: {len(df)} reviews")
                
            except Exception as e:
                self.logger.error(f"❌ {bank} failed: {e}")
                
        return pd.concat(results, ignore_index=True) if results else pd.DataFrame()