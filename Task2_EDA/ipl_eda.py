"""
ipl_eda_csv.py
Runs Exploratory Data Analysis (EDA) on a single CSV IPL dataset.
Handles both match-level and deliveries-level CSVs (auto-detection).
Outputs CSV summaries, PNG plots and a summary.json into ./output/

Update FILE_PATH to point to your CSV file (use r"..." on Windows).
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import json
import warnings
warnings.filterwarnings("ignore")

# ------------- CONFIG -------------
# Update this path to your CSV file (use raw string r"..." on Windows)
FILE_PATH = r"C:\Users\Asus\Desktop\IPL.csv"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ------------- Helpers -------------
def save_fig(plt, fname):
    path = os.path.join(OUTPUT_DIR, fname)
    plt.tight_layout()
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    print(f"Saved plot: {path}")

def df_overview(df, name):
    print(f"\n--- {name} overview ---")
    print("shape:", df.shape)
    print("columns:", list(df.columns))
    missing = df.isnull().sum()
    print("missing values (top 10):")
    print(missing[missing>0].sort_values(ascending=False).head(10))
    desc = df.describe(include='all').T
    desc.to_csv(os.path.join(OUTPUT_DIR, f"{name}_describe.csv"))
    df.head(8).to_csv(os.path.join(OUTPUT_DIR, f"{name}_head.csv"), index=False)

def try_parse_dates(df, colnames):
    for col in colnames:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            except Exception:
                pass
    return df

# ------------- Load CSV -------------
if not os.path.exists(FILE_PATH):
    raise FileNotFoundError(f"CSV file not found: {FILE_PATH}\nPlease put the correct path in FILE_PATH.")

print("Loading CSV:", FILE_PATH)
df = pd.read_csv(FILE_PATH)
print("Loaded. Shape:", df.shape)

# ------------- Auto-detect type -------------
cols_lower = [c.lower() for c in df.columns]
is_deliveries = any(x in cols_lower for x in ('batsman','bowler','inning','ball','batsman_runs','total_runs','match_id'))
is_matches = any(x in cols_lower for x in ('season','team1','team2','winner','toss_winner','venue','date','id','match_id'))

# If both heuristics true, choose deliveries if delivery-specific columns present
if is_deliveries and not is_matches:
    mode = "deliveries"
elif is_matches and not is_deliveries:
    mode = "matches"
elif is_deliveries and is_matches:
    # ambiguous: decide based on stronger signal
    if 'batsman' in cols_lower or 'bowler' in cols_lower:
        mode = "deliveries"
    else:
        mode = "matches"
else:
    # fallback: treat as generic table
    mode = "generic"

print("Auto-detected dataset mode:", mode)

# Normalize column name access (map to lowercase->original)
col_map = {c.lower(): c for c in df.columns}

# ------------- MATCH-LEVEL EDA -------------
summary = {}
if mode in ("matches", "generic"):
    matches = df.copy()
    matches = try_parse_dates(matches, ['date'])
    df_overview(matches, "matches")

    # Basic info
    summary['n_rows'] = int(matches.shape[0])
    if 'season' in col_map:
        summary['n_seasons'] = int(matches[col_map['season']].nunique())
    # Teams detected
    teams = set()
    for k in ('team1','team2','winner','toss_winner'):
        if k in col_map:
            teams.update(matches[col_map[k]].dropna().unique().tolist())
    summary['teams'] = sorted(list(teams))

    # Top teams by wins
    if 'winner' in col_map:
        wins = matches[col_map['winner']].value_counts().reset_index()
        wins.columns = ['team','wins']
        wins.to_csv(os.path.join(OUTPUT_DIR,"top_teams_by_wins.csv"), index=False)
        # plot
        plt.figure(figsize=(10,6))
        sns.barplot(data=wins.head(10), x='wins', y='team')
        plt.title("Top 10 Teams by Wins")
        save_fig(plt, "top10_teams_wins.png")
        summary['top_teams'] = wins.head(5).to_dict(orient='records')

    # Matches per season
    if 'season' in col_map:
        season_counts = matches.groupby(col_map['season']).size().reset_index(name='matches')
        season_counts.to_csv(os.path.join(OUTPUT_DIR,"matches_per_season.csv"), index=False)
        plt.figure(figsize=(10,5))
        sns.lineplot(data=season_counts, x=col_map['season'], y='matches', marker='o')
        plt.title("Matches per Season")
        save_fig(plt, "matches_per_season.png")

    # Toss advantage (proportion)
    if 'toss_winner' in col_map and 'winner' in col_map:
        toss_win_and_won = (matches[col_map['toss_winner']] == matches[col_map['winner']]).astype(int)
        frac = float(toss_win_and_won.mean())
        successes = int(toss_win_and_won.sum())
        n = int(len(toss_win_and_won))
        try:
            pval = stats.binom_test(successes, n, 0.5, alternative='two-sided')
        except Exception:
            pval = None
        with open(os.path.join(OUTPUT_DIR,"toss_advantage.txt"), "w") as f:
            f.write(f"toss_win_fraction={frac}\nsuccesses={successes}\nn={n}\nbinom_test_p={pval}\n")
        print("Toss advantage fraction:", frac, "pval:", pval)
        summary['toss_advantage_fraction'] = frac
        summary['toss_advantage_p'] = pval

    # Save rows with missing values for inspection
    matches[matches.isnull().any(axis=1)].to_csv(os.path.join(OUTPUT_DIR,"matches_rows_with_missing.csv"), index=False)

# ------------- DELIVERIES-LEVEL EDA -------------
if mode == "deliveries":
    deliveries = df.copy()
    deliveries = try_parse_dates(deliveries, ['date'])
    df_overview(deliveries, "deliveries")

    # Detect match_id column name
    match_id_col = None
    for cand in ('match_id','id','matchid','matchId'):
        if cand in col_map:
            match_id_col = col_map[cand]
            break

    # Top batsmen
    if 'batsman' in col_map and 'batsman_runs' in col_map:
        br = deliveries.groupby(col_map['batsman'])[col_map['batsman_runs']].sum().sort_values(ascending=False).reset_index()
        br.columns = ['batsman','total_runs']
        br.to_csv(os.path.join(OUTPUT_DIR,"top_batsmen.csv"), index=False)
        plt.figure(figsize=(10,6))
        sns.barplot(data=br.head(10), x='total_runs', y='batsman')
        plt.title("Top 10 Batsmen by Runs")
        save_fig(plt, "top10_batsmen.png")
        summary['top_batsmen'] = br.head(5).to_dict(orient='records')

    # Top bowlers by wickets (exclude run outs)
    if 'bowler' in col_map and 'dismissal_kind' in col_map:
        w_df = deliveries[deliveries[col_map['dismissal_kind']].notnull() & (deliveries[col_map['dismissal_kind']] != 'run out')]
        bw = w_df.groupby(col_map['bowler']).size().sort_values(ascending=False).reset_index(name='wickets')
        bw.to_csv(os.path.join(OUTPUT_DIR,"top_bowlers.csv"), index=False)
        plt.figure(figsize=(10,6))
        sns.barplot(data=bw.head(10), x='wickets', y='bowler')
        plt.title("Top 10 Bowlers by Wickets")
        save_fig(plt, "top10_bowlers.png")
        summary['top_bowlers'] = bw.head(5).to_dict(orient='records')

    # Runs per match distribution
    if match_id_col is not None:
        if 'total_runs' in col_map:
            rpm = deliveries.groupby(match_id_col)[col_map['total_runs']].sum()
        else:
            # sum batsman_runs + extras if extras exist
            if 'extra_runs' in col_map and 'batsman_runs' in col_map:
                rpm = deliveries.groupby(match_id_col).apply(lambda g: g[col_map['batsman_runs']].sum() + g[col_map['extra_runs']].sum())
            elif 'batsman_runs' in col_map:
                rpm = deliveries.groupby(match_id_col)[col_map['batsman_runs']].sum()
            else:
                rpm = None

        if rpm is not None:
            rpm_df = rpm.reset_index().rename(columns={0:'total_runs'}) if isinstance(rpm, pd.Series) else rpm.reset_index(name='total_runs')
            rpm_df.to_csv(os.path.join(OUTPUT_DIR, "runs_per_match.csv"), index=False)
            plt.figure(figsize=(10,6))
            sns.histplot(rpm_df['total_runs'], bins=40)
            plt.xlabel("Total runs per match")
            plt.title("Distribution of Total Runs per Match")
            save_fig(plt, "runs_per_match_hist.png")
            # outliers
            rpm_df.sort_values('total_runs', ascending=False).head(20).to_csv(os.path.join(OUTPUT_DIR,"top_run_matches.csv"), index=False)
            summary['runs_per_match_summary'] = rpm_df['total_runs'].describe().to_dict()

            # Wickets per match if dismissal present
            if 'dismissal_kind' in col_map:
                wpm = deliveries.groupby(match_id_col)[col_map['dismissal_kind']].apply(lambda s: s.notnull().sum()).reset_index(name='total_wickets')
                rp = rpm_df.merge(wpm, left_on=match_id_col, right_on=match_id_col, how='left')
                plt.figure(figsize=(8,6))
                sns.scatterplot(data=rp, x='total_runs', y='total_wickets')
                plt.title("Runs vs Wickets per match")
                save_fig(plt, "runs_vs_wickets.png")

    # Innings level paired test (inning1 vs inning2)
    if 'inning' in col_map and match_id_col is not None and 'batsman_runs' in col_map:
        innings = deliveries.groupby([match_id_col, col_map['inning']])[col_map['batsman_runs']].sum().reset_index()
        pivot = innings.pivot(index=match_id_col, columns=col_map['inning'], values=col_map['batsman_runs']).dropna()
        if 1 in pivot.columns and 2 in pivot.columns:
            tstat, pval = stats.ttest_rel(pivot[1], pivot[2])
            with open(os.path.join(OUTPUT_DIR,"t_test_inning1_vs_inning2.txt"), "w") as f:
                f.write(f"paired t-test inning1 vs inning2: t={tstat}, p={pval}\n")
            print("Saved paired t-test for innings (1 vs 2).")
            summary['inning_paired_ttest'] = {'t': float(tstat), 'p': float(pval)}

    deliveries[deliveries.isnull().any(axis=1)].to_csv(os.path.join(OUTPUT_DIR,"deliveries_rows_with_missing.csv"), index=False)

# ------------- GENERIC NUMERIC CORRELATION -------------
# Use numeric correlation heatmap if many numeric columns exist
num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
if len(num_cols) >= 2:
    corr = df[num_cols].corr()
    corr.to_csv(os.path.join(OUTPUT_DIR,"numeric_correlation.csv"))
    plt.figure(figsize=(10,8))
    sns.heatmap(corr, annot=True, fmt=".2f")
    plt.title("Numeric correlation heatmap")
    save_fig(plt, "numeric_correlation_heatmap.png")

# ------------- MISSING & ANOMALIES -------------
df[df.isnull().any(axis=1)].to_csv(os.path.join(OUTPUT_DIR,"rows_with_missing.csv"), index=False)
# simple outlier detect for a numeric column if present
if 'total_runs' in col_map or 'batsman_runs' in col_map:
    col = col_map.get('total_runs', col_map.get('batsman_runs'))
    if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        upper = q3 + 1.5*iqr
        outliers = df[df[col] > upper]
        outliers.head(20).to_csv(os.path.join(OUTPUT_DIR, f"outliers_by_{col}.csv"), index=False)

# ------------- SAVE SUMMARY JSON -------------
with open(os.path.join(OUTPUT_DIR,"summary.json"), "w") as f:
    json.dump(summary, f, indent=2, default=str)

print("\nEDA finished. All outputs are in:", os.path.abspath(OUTPUT_DIR))
print("Key outputs: .csv summaries, .png plots, summary.json")
