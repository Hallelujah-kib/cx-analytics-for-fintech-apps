import pandas as pd
import logging
from typing import Optional
import os
from datetime import datetime

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReviewPreprocessor:
    """
    A class for cleaning and preprocessing app review data.
    """
    
    def __init__(self, min_review_length: int = 10, min_rating: int = 1, max_rating: int = 5):
        """
        Initialize the preprocessor with validation parameters.
        
        Args:
            min_review_length: Minimum characters for a valid review
            min_rating: Minimum valid rating value
            max_rating: Maximum valid rating value
        """
        self.min_review_length = min_review_length
        self.min_rating = min_rating
        self.max_rating = max_rating
    
    def clean_reviews(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Perform comprehensive cleaning of review data.
        
        Args:
            df: Raw review DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        try:
            # Initial validation
            if not isinstance(df, pd.DataFrame):
                raise ValueError("Input must be a pandas DataFrame")
                
            required_columns = {'review_text', 'rating', 'date', 'bank_name', 'source'}
            if not required_columns.issubset(df.columns):
                missing = required_columns - set(df.columns)
                raise ValueError(f"Missing required columns: {missing}")
            
            logger.info(f"Starting cleaning with {len(df)} initial reviews")
            
            # 1. Remove duplicates
            initial_count = len(df)
            df = df.drop_duplicates(subset=['review_text'])
            logger.info(f"Removed {initial_count - len(df)} duplicate reviews")
            
            # 2. Handle missing values
            df = df.dropna(subset=['review_text', 'rating', 'date'])
            logger.info(f"After dropping NA values: {len(df)} reviews remain")
            
            # 3. Clean and validate dates
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df[df['date'].notna()]
            df['date'] = df['date'].dt.strftime('%Y-%m-%d')
            
            # 4. Validate ratings
            df = df[(df['rating'] >= self.min_rating) & (df['rating'] <= self.max_rating)]
            
            # 5. Clean review text
            df['review_text'] = df['review_text'].str.strip()
            df = df[df['review_text'].str.len() >= self.min_review_length]
            
            # 6. Add metadata
            df['processed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            logger.info(f"Cleaning complete. Final count: {len(df)} reviews")
            return df
            
        except Exception as e:
            logger.error(f"Error during cleaning: {str(e)}")
            raise

    def save_clean_data(self, df: pd.DataFrame, path: str, overwrite: bool = False) -> None:
        """
        Save cleaned data to CSV with additional checks.
        
        Args:
            df: Cleaned DataFrame
            path: Output file path
            overwrite: Whether to overwrite existing file
        """
        try:
            if not isinstance(df, pd.DataFrame):
                raise ValueError("Input must be a pandas DataFrame")
                
            if os.path.exists(path) and not overwrite:
                raise FileExistsError(f"File {path} already exists. Set overwrite=True to replace.")
                
            os.makedirs(os.path.dirname(path), exist_ok=True)
            df.to_csv(path, index=False, encoding='utf-8')
            logger.info(f"Successfully saved cleaned data to {path}")
            
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")
            raise