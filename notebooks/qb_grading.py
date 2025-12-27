import pandas as pd
from utils import standardize_columns
from qb_cleaning import get_cleaned_data
from sklearn.cluster import KMeans



# 2. Prevent the table from 'wrapping' to a new line
pd.set_option('display.width', 100)
# Load the file created by cleaning.py
df = get_cleaned_data()
df = df[df['Att'] >= 200].copy()
drivers = ['ANY/A', 'EPA/Play', 'QBR', 'Succ%', 'Int%', 'Sk%', 'Att', 'Rush EPA', 'TD%', 'IAY/PA','Bad%', 'Prss%', 'OnTgt%', 'SoS']
df = standardize_columns(df, drivers)
df['Composite_Z'] = (
    # --- Efficiency (50%) ---
    (df['EPA/Play_z'] * 0.25) +
    (df['ANY/A_z'] * 0.225) +

    # --- Accuracy & Difficulty (25%) ---
    (df['OnTgt%_z'] * 0.075) +
    (df['IAY/PA_z'] * 0.10) +
    (df['SoS_z'] * 0.05) +     # <--- New SOS Weight
    
    # --- Context & Volume (25%) ---
    (df['Att_z'] * 0.075) +
    (df['Rush EPA_z'] * 0.075) +
    (df['Succ%_z'] * 0.075) +
    (df['QBR_z'] * 0.05) +
    (df['Prss%_z'] * 0.05) -    # Pressure faced is a 'difficulty' bonus
    
    # --- Penalties ---
    (df['Int%_z'] * 0.05) -
    (df['Bad%_z'] * 0.075) -
    (df['Sk%_z'] * 0.05)
)

min_z = df['Composite_Z'].min()
max_z = df['Composite_Z'].max()
df['Final_Grade'] = ((df['Composite_Z'] - min_z) / (max_z - min_z)) * 100
df['Final_Grade'] = df['Final_Grade'].round(2)
df = df.sort_values(by='Final_Grade', ascending=False).reset_index(drop=True)

df.index = df.index + 1

score_leaderboard_qbs = df[['Player', 'Team', 'Final_Grade', 'Att', 'EPA/Play', 'ANY/A', 'SoS']].sort_values(by='Final_Grade', ascending=False)
print(score_leaderboard_qbs.head(20))

#------------------------------------CONTRACTS------------------------------------------------------#
X = df[['APY']].values
kmeans = KMeans(n_clusters=3, random_state=42)
df['Salary_Cluster'] = kmeans.fit_predict(X)
cluster_means = df.groupby('Salary_Cluster')['APY'].mean()
elite_cluster_id = cluster_means.idxmax()
calculated_threshold = df[df['Salary_Cluster'] == elite_cluster_id]['APY'].min()
print(df[['Player', 'Salary_Cluster']].head(20))


cluster_averages = df.groupby('Salary_Cluster')['APY'].mean().sort_values()
tier_map = {
    cluster_averages.index[0]: "Rookie/Cheap",
    cluster_averages.index[1]: "Bridge/Mid",
    cluster_averages.index[2]: "Franchise/Elite"
}
df['Contract_Tier'] = df['Salary_Cluster'].map(tier_map)

max_salary = 60_000_000
min_salary = 1_200_000
dollar_per_z_M = ((max_salary - min_salary) / 4.0)/1_000_000
league_avg_anchor = df[df['Contract_Tier'].isin(['Franchise/Elite', 'Bridge/Mid'])].copy()
league_avg_anchor_M = league_avg_anchor['APY'].mean() / 1_000_000
df['APYM'] = df['APY'] / 1_000_000
franchise_qbs = df[df['Contract_Tier'] == "Franchise/Elite"].copy()
market_rate_franchise = franchise_qbs['APYM'].mean() / franchise_qbs['Composite_Z'].mean()
df['Market Value'] = league_avg_anchor_M + (df['Composite_Z'] * dollar_per_z_M)
df['Value Diff'] = df['Market Value'] - df['APYM']
df['Value Diff'] = df['Value Diff'].round(3)
franchise_qbs = df[df['Contract_Tier'] == "Franchise/Elite"].copy()

overall_franchise_leaderboard_qbs = franchise_qbs[['Player', 'Value Diff', 'APY', 'Final_Grade', 'Contract_Tier', 'Market Value']].sort_values(by='Value Diff', ascending=False)
overall_franchise_leaderboard_qbs = overall_franchise_leaderboard_qbs.reset_index(drop=True)
overall_franchise_leaderboard_qbs.index = overall_franchise_leaderboard_qbs.index+1
print("\nOverall Leaderboard (Value Diff):")
print(overall_franchise_leaderboard_qbs.head(20))