from src import scraper, preprocess, sentiment, themes

def main():
    # Step 1 - Scrape
    df = scraper.scrape_all_reviews()

    # Step 2 - Clean
    df_clean = preprocess.clean_reviews(df)
    preprocess.save_clean_data(df_clean, 'data/clean_reviews.csv')

    # Step 3 - Sentiment
    model = sentiment.load_sentiment_model()
    df_sent = sentiment.classify_sentiment(df_clean.copy(), model)

    # Step 4 - Themes
    tfidf, vectorizer = themes.extract_keywords_tfidf(df_sent['review'])
    themes_by_bank = themes.extract_themes(tfidf, vectorizer)
    print("Sample Themes:", themes_by_bank)

    # Save final output
    df_sent.to_csv('outputs/final_sentiment_reviews.csv', index=False)

if __name__ == '__main__':
    main()
