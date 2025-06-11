import os
import pandas as pd
import logging
from datetime import datetime
from typing import Optional

class ReviewPreprocessor:
    """Advanced review cleaner with cross-file duplicate handling."""
    
    def __init__(self, input_dir: str = None, output_dir: str = None):
        self._setup_paths(input_dir, output_dir)
        self._setup_logging()
        
    def _setup_paths(self, input_dir, output_dir):
        """Configure paths with defaults."""
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.input_dir = input_dir or os.path.join(self.base_dir, 'data', 'scraped_data')
        self.output_dir = output_dir or os.path.join(self.base_dir, 'data', 'cleaned_data')
        self.log_dir = output_dir or os.path.join(self.base_dir, 'logs')
        os.makedirs(self.output_dir, exist_ok=True)

    def _setup_logging(self):
        """Initialize logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileFHandler(os.path.join(self.log_dir, 'cleaning.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _load_and_merge(self) -> Optional[pd.DataFrame]:
        """Load all scraped CSVs into single DataFrame."""
        dfs = []
        for file in os.listdir(self.input_dir):
            if file.endswith('.csv'):
                try:
                    df = pd.read_csv(os.path.join(self.input_dir, file))
                    df['source_file'] = file
                    dfs.append(df)
                    self.logger.info(f"Loaded {file}: {len(df)} reviews")
                except Exception as e:
                    self.logger.error(f"Failed to load {file}: {e}")
        return pd.concat(dfs, ignore_index=True) if dfs else None

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Perform comprehensive cleaning."""
        # Initial checks
        if df.empty:
            return df
            
        # Deduplication
        initial_count = len(df)
        df = df.drop_duplicates(subset=['review_text'])
        self.logger.info(f"Removed {initial_count - len(df)} duplicates")
        
        # Data validation
        df = df.dropna(subset=['review_text', 'rating'])
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df[df['date'].notna()]
        df = df[df['rating'].between(1, 5)]
        
        # Text cleaning
        df['review_text'] = df['review_text'].str.strip()
        return df.reset_index(drop=True)

    def process(self) -> Optional[pd.DataFrame]:
        """Full processing pipeline."""
        merged = self._load_and_merge()
        if merged is None:
            self.logger.warning("No files found to process")
            return None
            
        cleaned = self.clean(merged)
        if cleaned.empty:
            self.logger.warning("No valid reviews after cleaning")
            return None
            
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        output_path = os.path.join(self.output_dir, f'cleaned_reviews_{timestamp}.csv')
        cleaned.to_csv(output_path, index=False)
        self.logger.info(f"Saved {len(cleaned)} reviews to {output_path}")
        
        return cleaned