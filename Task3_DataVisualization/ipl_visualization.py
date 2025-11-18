import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# ---------------- CONFIG ----------------
FILE_PATH = r"C:\Users\Asus\Desktop\IPL.csv"   # <<< YOUR FILE PATH
OUTPUT_DIR = "output_visuals"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------- LOAD DATA ----------------
print("Loading CSV (low_memory=False to reduce dtype warnings)...")
df = pd.read_csv(FILE_PATH, low_memory=False)
print("Loaded. Shape:", df.shape)
print("Columns:", df.columns.tolist())

# ---------------- helper to pick column name if multiple variants exist ----------------
def pick_column(df, candidates):
    """
    Given a list of candidate column names (case-insensitive),
    return the first one that exists in df.columns, or None.
    """
    cols_lc = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand and cand.lower() in cols_lc:
            return cols_lc[cand.lower()]
    return None

# Map likely columns
winner_col = pick_column(df, ["winner", "match_won_by", "match_winner", "win_team", "team_won"])
season_col = pick_column(df, ["season", "year", "Year"])
toss_decision_col = pick_column(df, ["toss_decision", "tossdecision", "toss_decision "])
venue_col = pick_column(df, ["venue", "stadium", "ground"])
# For batsman/batter and runs
batsman_col = pick_column(df, ["batsman", "batter", "player"])
batsman_runs_col = pick_column(df, ["batsman_runs", "batter_runs", "runs_batter", "runs_batsman", "batsmanrun", "batsman_run"])
# Some files may have 'batsman_runs' at deliveries-level; check also 'runs_total' or 'runs' fallback
total_runs_col = pick_column(df, ["runs_total", "total_runs", "runs", "runs_total "])
toss_winner_col = pick_column(df, ["toss_winner", "tosswinner"])

print("Detected columns mapping:")
print(" winner_col:", winner_col)
print(" season_col:", season_col)
print(" toss_decision_col:", toss_decision_col)
print(" venue_col:", venue_col)
print(" batsman_col:", batsman_col)
print(" batsman_runs_col:", batsman_runs_col)
print(" total_runs_col:", total_runs_col)
print(" toss_winner_col:", toss_winner_col)

sns.set_style("whitegrid")

# ---------------- 1) Wins by Team ----------------
if winner_col is not None:
    try:
        win_count = df[winner_col].value_counts().dropna()
        if len(win_count) > 0:
            plt.figure(figsize=(12,6))
            sns.barplot(x=win_count.values, y=win_count.index)
            plt.title("Total Wins by IPL Teams", fontsize=15)
            plt.xlabel("Number of Wins")
            plt.ylabel("Team Name")
            plt.tight_layout()
            outp = os.path.join(OUTPUT_DIR, "wins_by_team.png")
            plt.savefig(outp, bbox_inches='tight')
            plt.close()
            print("Saved:", outp)
    except Exception as e:
        print("Failed to plot wins_by_team:", e)
else:
    print("Winner column not found; skipping Wins by Team plot.")

# ---------------- 2) Matches per Season ----------------
if season_col is not None:
    # Coerce season to numeric where possible, otherwise treat as string but sort safely
    s = df[season_col].copy()
    # attempt numeric conversion
    s_num = pd.to_numeric(s, errors='coerce')
    if s_num.notnull().sum() > 0:
        # use numeric where available
        df['_season_numeric'] = s_num
        season_counts = df.dropna(subset=['_season_numeric']).groupby('_season_numeric').size().reset_index(name='matches')
        season_counts = season_counts.sort_values('_season_numeric')
        x_vals = season_counts['_season_numeric'].astype(int).astype(str).tolist()
        y_vals = season_counts['matches'].tolist()
    else:
        # fallback: treat all as strings and sort lexicographically
        season_counts = df[season_col].astype(str).value_counts().sort_index()
        x_vals = season_counts.index.tolist()
        y_vals = season_counts.values.tolist()

    if len(y_vals) > 0:
        plt.figure(figsize=(10,5))
        sns.lineplot(x=x_vals, y=y_vals, marker="o")
        plt.title("Matches Played per Season", fontsize=15)
        plt.xlabel("Season")
        plt.ylabel("Number of Matches")
        plt.xticks(rotation=45)
        plt.tight_layout()
        outp = os.path.join(OUTPUT_DIR, "matches_per_season.png")
        plt.savefig(outp, bbox_inches='tight')
        plt.close()
        print("Saved:", outp)
else:
    print("Season column not found; skipping Matches per Season plot.")

# ---------------- 3) Toss Decision Distribution ----------------
if toss_decision_col is not None:
    try:
        counts = df[toss_decision_col].value_counts().dropna()
        if counts.sum() > 0:
            plt.figure(figsize=(7,7))
            counts.plot(kind="pie", autopct="%1.1f%%", startangle=90)
            plt.title("Toss Decision: Bat or Field?")
            plt.ylabel("")
            outp = os.path.join(OUTPUT_DIR, "toss_decision_pie.png")
            plt.savefig(outp, bbox_inches='tight')
            plt.close()
            print("Saved:", outp)
    except Exception as e:
        print("Failed to plot toss_decision_pie:", e)
else:
    print("Toss decision column not found; skipping toss decision plot.")

# ---------------- 4) Venue Match Count ----------------
if venue_col is not None:
    try:
        venue_counts = df[venue_col].value_counts().head(15)
        if len(venue_counts) > 0:
            plt.figure(figsize=(10,7))
            sns.barplot(y=venue_counts.index, x=venue_counts.values)
            plt.title("Top 15 Venues by Match Count")
            plt.xlabel("Matches Held")
            plt.ylabel("Venue")
            plt.tight_layout()
            outp = os.path.join(OUTPUT_DIR, "venue_match_count.png")
            plt.savefig(outp, bbox_inches='tight')
            plt.close()
            print("Saved:", outp)
    except Exception as e:
        print("Failed to plot venue_match_count:", e)
else:
    print("Venue column not found; skipping venue plot.")

# ---------------- 5) Top Batsmen (if dataset has batting-level info) ----------------
# Your file shows 'batter' and 'batter_runs' or 'batsman' and 'batsman_runs' variants.
# We'll try a few possibilities.
if batsman_col is not None and batsman_runs_col is not None:
    try:
        br = df.groupby(batsman_col)[batsman_runs_col].sum().sort_values(ascending=False).head(10)
        if br.sum() > 0:
            plt.figure(figsize=(10,6))
            sns.barplot(x=br.values, y=br.index)
            plt.title("Top 10 Batsmen by Total Runs")
            plt.xlabel("Total Runs")
            plt.ylabel("Batsman")
            plt.tight_layout()
            outp = os.path.join(OUTPUT_DIR, "top_batsmen.png")
            plt.savefig(outp, bbox_inches='tight')
            plt.close()
            print("Saved:", outp)
    except Exception as e:
        print("Failed to plot top_batsmen:", e)
else:
    # attempt with alternative names that appeared in your columns
    alt_batter = pick_column(df, ["batter", "batsman", "player_out", "player_of_match"])
    alt_runs = pick_column(df, ["batter_runs", "runs_batter", "runs_total", "runs", "runs_batsman"])
    if alt_batter and alt_runs and alt_batter in df.columns and alt_runs in df.columns:
        try:
            br = df.groupby(alt_batter)[alt_runs].sum().sort_values(ascending=False).head(10)
            if br.sum() > 0:
                plt.figure(figsize=(10,6))
                sns.barplot(x=br.values, y=br.index)
                plt.title("Top 10 Batsmen by Total Runs")
                plt.xlabel("Total Runs")
                plt.ylabel("Batsman")
                plt.tight_layout()
                outp = os.path.join(OUTPUT_DIR, "top_batsmen_alt.png")
                plt.savefig(outp, bbox_inches='tight')
                plt.close()
                print("Saved:", outp)
        except Exception as e:
            print("Failed to plot alt top_batsmen:", e)
    else:
        print("Batsman or batsman_runs columns not found; skipping top batsmen plot.")

print("\nAll done — check the folder:", os.path.abspath(OUTPUT_DIR))
