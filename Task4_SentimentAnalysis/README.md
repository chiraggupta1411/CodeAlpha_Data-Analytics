# 📝 Sentiment Analysis — CodeAlpha Task 4

This project performs sentiment analysis on a dataset of text reviews using Python and TextBlob.  
The objective is to classify reviews as **Positive**, **Negative**, or **Neutral** and visualize sentiment patterns.

## Features
- Text cleaning & preprocessing
- Polarity scoring (−1 to +1)
- Subjectivity scoring (0 to 1)
- Sentiment classification
- Visualizations:
  - Sentiment distribution
  - Polarity histogram
  - Subjectivity histogram

## Requirements
pip install pandas textblob matplotlib seaborn
python -m textblob.download_corpora

## How To Run
1. Place your reviews file as `reviews.csv`
2. Update FILE_PATH in the script
3. Run:
   python sentiment_analysis.py
4. Outputs will be in `sentiment_output/`

## Outcome
Clear identification of sentiment trends within the text dataset, useful for customer feedback analysis, review mining, and social sentiment monitoring.
