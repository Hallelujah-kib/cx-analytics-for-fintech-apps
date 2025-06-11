import os
import pandas as pd
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from deep_translator import GoogleTranslator
from langdetect import detect
import torch
from tqdm import tqdm
import emoji


class SentimentAnalyzer:
    def __init__(self, model_name="distilbert-base-uncased-finetuned-sst-2-english"):
        # Load DistilBERT sentiment model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.pipeline = pipeline(
            "sentiment-analysis",
            model=self.model,
            tokenizer=self.tokenizer,
            return_all_scores=False,  # for batch inference
            device=0 if torch.cuda.is_available() else -1
        )

        # Translation
        self.translator = GoogleTranslator(source="auto", target="en")
        self.translation_cache = {}

    def is_english(self, text):
        try:
            return detect(text) == "en"
        except:
            return False

    def demojize_text(self, text):
        return emoji.demojize(str(text), delimiters=(" ", " "))

    def safe_translate(self, text):
        text = self.demojize_text(text)
        if text in self.translation_cache:
            return self.translation_cache[text]
        try:
            translated = self.translator.translate(text)
            self.translation_cache[text] = translated
            return translated
        except:
            return text

    def classify_batch(self, texts):
        results = []
        for text in texts:
            try:
                result = self.pipeline(str(text)[:512])[0]
                results.append((result["label"].lower(), float(result["score"])))
            except:
                results.append(("unknown", 0.0))
        return results

    def analyze_file(self, input_csv, output_csv):
        df = pd.read_csv(input_csv)
        tqdm.pandas(desc="🔁 Translating Reviews")

        # Translate only non-English and demojize all
        df["translated_review"] = df["review_text"].progress_apply(
            lambda x: x if self.is_english(x) else self.safe_translate(x)
        )

        tqdm.pandas(desc="🔍 Analyzing Sentiment")
        sentiments = self.classify_batch(df["translated_review"].tolist())
        df[["sentiment_label", "sentiment_score"]] = pd.DataFrame(sentiments, index=df.index)

        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        df.to_csv(output_csv, index=False)
        print(f"✅ Final sentiment-labeled file saved: {output_csv}")
        return df
