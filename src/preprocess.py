import pandas as pd

def clean_reviews(df):
    df = df.drop_duplicates(subset=['review'])
    df = df.dropna(subset=['review', 'rating', 'date'])
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    return df

def save_clean_data(df, path):
    df.to_csv(path, index=False)

# === STEP 3: SENTIMENT ANALYSIS ===
# File: src/sentiment.py
from transformers import pipeline

def load_sentiment_model():
    return pipeline('sentiment-analysis', model="distilbert-base-uncased-finetuned-sst-2-english")

def classify_sentiment(df, model):
    sentiments = model(df['review'].tolist(), truncation=True)
    df['sentiment_label'] = [s['label'] for s in sentiments]
    df['sentiment_score'] = [s['score'] for s in sentiments]
    return df