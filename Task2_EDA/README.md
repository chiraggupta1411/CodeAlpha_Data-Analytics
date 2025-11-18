# IPL EDA (2008-2025)

This repository contains an Exploratory Data Analysis (EDA) on the IPL Dataset (2008-2025) from Kaggle.

## Files
- `ipl_eda.ipynb` / `ipl_eda.py` : Notebook / script to run the EDA.
- `data/` : place `matches.csv` and `deliveries.csv` here (not included).
- `output/` : generated plots and summary files after running the notebook.

## How to run
1. Download dataset from Kaggle: https://www.kaggle.com/datasets/chaitu20/ipl-dataset2008-2025. Place CSVs in `data/`.
2. `pip install -r requirements.txt` (pandas, numpy, matplotlib, seaborn, scipy)
3. `jupyter notebook ipl_eda.ipynb` or `python ipl_eda.py`

## Summary
Includes team rankings, top batsmen/bowlers, season-level trends, hypothesis tests (toss advantage, batting first vs second), and anomaly detection.
