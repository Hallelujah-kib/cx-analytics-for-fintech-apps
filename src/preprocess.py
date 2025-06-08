import pandas as pd

def clean_reviews(df):
    df = df.drop_duplicates(subset=['review'])
    df = df.dropna(subset=['review', 'rating', 'date'])
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    return df

def save_clean_data(df, path):
    df.to_csv(path, index=False)