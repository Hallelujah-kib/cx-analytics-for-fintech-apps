import time
import pandas as pd
from google_play_scraper import reviews, Sort

# Constants
APP_IDS = {
    'CBE': 'com.combanketh.mobilebanking',
    'BOA': 'com.boa.boaMobileBanking',
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
                'review': r['content'],
                'rating': r['score'],
                'date': r['at'].date(),
                'bank': app_name,
                'source': 'Google Play'
            })
        if continuation_token is None:
            break
        time.sleep(1)
    return pd.DataFrame(all_reviews[:count])

def scrape_all_reviews():
    dfs = []
    for bank, app_id in APP_IDS.items():
        print(f"Scraping {bank}...")
        df = fetch_reviews(bank, app_id, count=500)
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)