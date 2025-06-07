# Fintech App Review Analysis

Customer Experience Analytics for Fintech Apps (Week 2 Challenge – 10 Academy)

## 🔍 Project Overview

This project simulates a real-world consulting task where we analyze user reviews of three Ethiopian banking apps:

* Commercial Bank of Ethiopia (CBE)
* Bank of Abyssinia (BOA)
* Dashen Bank

Our objective is to extract insights from Google Play Store reviews to identify customer satisfaction drivers and pain points. The pipeline includes:

* Web scraping
* Text preprocessing
* Sentiment & thematic analysis
* Oracle database integration
* Insight visualization and reporting

---

## 📁 Folder Structure

```
fintech-review-analysis/
├── data/                  # raw and cleaned data
├── notebooks/             # Jupyter notebooks
├── outputs/               # final CSVs, plots
├── src/                   # modular scripts
│   ├── scraper.py         # Google Play scraping
│   ├── preprocess.py      # deduplication, cleaning
│   ├── sentiment.py       # sentiment classification
│   ├── themes.py          # keyword extraction, topic modeling
│   ├── database.py        # Oracle/Postgres DB logic
│   ├── plots.py           # data visualization
│   └── utils.py           # reusable helper functions
├── sql/                   # schema.sql and insert scripts
├── requirements.txt
├── main.py                # main runner script
└── README.md
```

---

## ⚙️ How to Run the Project

### 1. Clone and Set Up Environment

```bash
git clone https://github.com/Hallelujah-kib/cx-analytics-for-fintech-apps.git
cd cx-analytics-for-fintech-apps
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Run Main Pipeline

```bash
python main.py
```

This will:

* Scrape reviews for all 3 banks
* Clean and normalize the data
* Perform sentiment classification and keyword extraction
* Output final sentiment-labeled reviews

### 3. Visualize Insights

Run the plotting module or use Jupyter Notebooks in the `/notebooks/` folder.

### 4. Load Data into Oracle/Postgres

Update credentials in `database.py` and run:

```bash
python src/database.py
```

---

## 🧪 Features and Methodologies

| Component         | Description                                                                   |
| ----------------- | ----------------------------------------------------------------------------- |
| **Scraping**      | `google-play-scraper` used with pagination & retry handling                   |
| **Preprocessing** | Duplicate removal, missing value drop, date normalization                     |
| **Sentiment**     | Hugging Face’s DistilBERT (`distilbert-base-uncased-finetuned-sst-2-english`) |
| **Themes**        | TF-IDF + NMF for thematic extraction                                          |
| **Database**      | Oracle XE integration via `oracledb` library                                  |
| **Plots**         | Sentiment trends, keyword clouds, rating distributions                        |

---

## 📊 Deliverables

* ✅ 1,200+ cleaned reviews
* ✅ Sentiment score and label for each review
* ✅ 3–5 themes per bank
* ✅ Oracle DB integration scripts
* ✅ Visualizations & business-oriented report

---

## 👨‍💻 Authors

This project was developed by \Hallelujah Kibru, 10 Academy Trainee.

---

## 📄 License

MIT License – see `LICENSE` file.
