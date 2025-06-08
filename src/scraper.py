import os
import time
import logging
import argparse
import pandas as pd
from datetime import datetime
from google_play_scraper import reviews, Sort
import schedule

# Logging setup
os.makedirs('logs', exist_ok=True)
os.makedirs('data', exist_ok=True)

logging.basicConfig(
    filename='logs/scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Constants
APP_IDS = {
    'CBE': 'com.combankethio.CBEbankingapp',
    'BOA': 'com.abyssiniasoftware.boa',
    'Dashen': 'com.dashen.dashensuperapp'
}

def fetch_reviews(app_name, app_id, count=500):
    all_reviews = []
    continuation_token = None
    while len(all_reviews) < count:
        result, continuation_token = reviews(
            app_id,
            lang='en',
            country='us',
            sort=Sort.NEWEST,
            count=100,
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
        time.sleep(1)
    logging.info(f"✅ Collected {len(all_reviews)} reviews for {app_name}")
    return all_reviews[:count]

def scrape_all_reviews(count_per_app=500, use_csv=True):
    all_data = []
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    for bank, app_id in APP_IDS.items():
        reviews_data = fetch_reviews(bank, app_id, count=count_per_app)
        all_data.extend(reviews_data)

        if use_csv:
            filename = f"data/{bank}_reviews_{timestamp}.csv"
            df = pd.DataFrame(reviews_data)
            df.to_csv(filename, index=False)
            logging.info(f"📄 Saved {len(reviews_data)} reviews to {filename}")

    return pd.DataFrame(all_data)

# Optional scheduling support
def run_scheduled_scraper():
    

    logging.info("📅 Scheduling scraper to run every hour...")
    schedule.every(1).hours.do(lambda: scrape_all_reviews(count_per_app=500, use_csv=True))

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Google Play Review Scraper")
    parser.add_argument('--schedule', action='store_true', help='Run in scheduled mode (daily at 01:00)')
    parser.add_argument('--no-csv', action='store_true', help='Skip saving to CSV')
    parser.add_argument('--count', type=int, default=500, help='Number of reviews per app')

    args = parser.parse_args()

    if args.schedule:
        run_scheduled_scraper()
    else:
        df = scrape_all_reviews(count_per_app=args.count, use_csv=not args.no_csv)
        print(df.head())
