import cx_Oracle
import pandas as pd

# Oracle DB connection details
username = "system"
password = "123456"
dsn = "localhost/XE"

# Connect to Oracle
conn = cx_Oracle.connect(user=username, password=password, dsn=dsn)
cursor = conn.cursor()

# Load the final sentiment reviews CSV
df = pd.read_csv("data/processed/final_sentiment_reviews.csv")

# Step 1: Insert unique banks
bank_names = df["bank_name"].unique()
bank_id_map = {}

for name in bank_names:
    cursor.execute("MERGE INTO banks b USING (SELECT :name AS bank_name FROM dual) d ON (b.bank_name = d.bank_name) " +
                   "WHEN NOT MATCHED THEN INSERT (bank_name) VALUES (:name)", [name])
conn.commit()

# Step 2: Get bank_id mapping
cursor.execute("SELECT bank_id, bank_name FROM banks")
for bank_id, bank_name in cursor.fetchall():
    bank_id_map[bank_name] = bank_id

# Step 3: Insert reviews
insert_sql = '''INSERT INTO reviews (
    bank_id, review_text, translated_review, rating, review_date, sentiment_label, sentiment_score
) VALUES (:1, :2, :3, :4, TO_DATE(:5, 'YYYY-MM-DD'), :6, :7)'''

for _, row in df.iterrows():
    cursor.execute(insert_sql, (
        bank_id_map.get(row["bank_name"]),
        row["review_text"],
        row["translated_review"],
        int(row["rating"]),
        row["date"],
        row["sentiment_label"],
        float(row["sentiment_score"])
    ))

conn.commit()
cursor.close()
conn.close()
print("✅ Data inserted successfully into Oracle DB.")
