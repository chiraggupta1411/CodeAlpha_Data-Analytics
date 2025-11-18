"""
Task 4 — Sentiment Analysis (CodeAlpha Internship)
Performs text cleaning + sentiment scoring + classification + visualization.
"""

import pandas as pd
import matplotlib.pyplot as plt
from textblob import TextBlob
import seaborn as sns
import os

# ---------------- CONFIG ----------------
FILE_PATH = r"C:\Users\Asus\Desktop\reviews.csv"   # Your dataset of reviews
OUTPUT_DIR = "sentiment_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Loading dataset...")
df = pd.read_csv(FILE_PATH)
print("Dataset loaded. Shape:", df.shape)

# ---------------- Clean Column Detection ----------------
review_col = None
for c in df.columns:
    if "review" in c.lower() or "comment" in c.lower() or "text" in c.lower():
        review_col = c
        break

if review_col is None:
    raise ValueError("No column found containing text reviews. Please rename your text column to 'review'.")

print("Using text column:", review_col)

# ---------------- STEP 1 — Text Cleaning ----------------
def clean_text(text):
    if pd.isnull(text):
        return ""
    text = str(text)
    text = text.replace("\n", " ")
    text = text.replace("\t", " ")
    return text.strip()

df["cleaned_text"] = df[review_col].apply(clean_text)

# ---------------- STEP 2 — Polarity & Subjectivity ----------------
def get_polarity(text):
    return TextBlob(text).sentiment.polarity

def get_subjectivity(text):
    return TextBlob(text).sentiment.subjectivity

df["polarity"] = df["cleaned_text"].apply(get_polarity)
df["subjectivity"] = df["cleaned_text"].apply(get_subjectivity)

# ---------------- STEP 3 — Sentiment Label ----------------
def classify_sentiment(score):
    if score > 0.05:
        return "Positive"
    elif score < -0.05:
        return "Negative"
    else:
        return "Neutral"

df["sentiment"] = df["polarity"].apply(classify_sentiment)

# Save processed file
df.to_csv(os.path.join(OUTPUT_DIR, "sentiment_results.csv"), index=False)
print("Saved: sentiment_results.csv")

# ---------------- STEP 4 — Visualization ----------------
# 1. Sentiment distribution
plt.figure(figsize=(7,5))
sns.countplot(data=df, x="sentiment", palette="coolwarm")
plt.title("Sentiment Distribution")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "sentiment_distribution.png"))
plt.close()
print("Saved: sentiment_distribution.png")

# 2. Polarity histogram
plt.figure(figsize=(8,5))
sns.histplot(df["polarity"], bins=40)
plt.title("Polarity Score Distribution")
plt.xlabel("Polarity")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "polarity_histogram.png"))
plt.close()
print("Saved: polarity_histogram.png")

# 3. Subjectivity histogram
plt.figure(figsize=(8,5))
sns.histplot(df["subjectivity"], bins=40)
plt.title("Subjectivity Score Distribution")
plt.xlabel("Subjectivity")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "subjectivity_histogram.png"))
plt.close()
print("Saved: subjectivity_histogram.png")

print("\n🎉 Sentiment Analysis Completed Successfully!")
print("Check the folder:", OUTPUT_DIR)
