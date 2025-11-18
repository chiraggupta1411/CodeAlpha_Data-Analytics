📊 IPL Data Visualization (Task 3)

This repository contains Data Visualization work on the IPL Dataset (2008–2025).
Multiple visualizations were created to highlight season trends, team performance, venue distribution, and batting patterns in the IPL.

📁 Files

ipl_visualization.ipynb / ipl_visualization.py : Notebook / script to generate all visualizations.

output_visuals/ : generated PNG plots (wins by team, matches per season, toss decisions, venues, top batsmen).

▶️ How to run

Download the dataset (IPL.csv) from Kaggle or your local source.

Update the file path in the script:

FILE_PATH = r"C:\Users\Asus\Desktop\IPL.csv"


Install required libraries:

pip install pandas matplotlib seaborn


Run the script or notebook:

python ipl_visualization.py


or

jupyter notebook ipl_visualization.ipynb

📈 Summary of Visualizations

The project includes the following insights:

Wins by Team: Identifies the most successful IPL franchises.

Matches per Season: Shows IPL’s growth and seasonal variations over the years.

Toss Decision Distribution: Reveals batting vs. fielding preferences after winning the toss.

Venue Match Count: Highlights the most frequently used stadiums.

Top Batsmen: Displays leading run-scorers based on ball-by-ball data (if available).

All charts are saved in the output_visuals/ folder.
