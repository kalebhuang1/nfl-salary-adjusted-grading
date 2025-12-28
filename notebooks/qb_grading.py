import pandas as pd
from utils import standardize_columns
from qb_cleaning import get_cleaned_data_qb
from sklearn.cluster import KMeans




pd.set_option('display.width', 100)

#------------------------------------GRADING------------------------------------------------------#
df = get_cleaned_data_qb()
df = df[df['Att'] >= 200].copy()
drivers = ['ANY/A', 'EPA/Play', 'QBR', 'Succ%', 'Int%', 'Sk%', 'Att', 'Rush EPA', 'TD%', 'IAY/PA','Bad%', 'Prss%', 'OnTgt%', 'SoS']
df = standardize_columns(df, drivers)
df['Composite_Z'] = (
  
    (df['EPA/Play_z'] * 0.25) +
    (df['ANY/A_z'] * 0.225) +
    (df['OnTgt%_z'] * 0.075) +
    (df['IAY/PA_z'] * 0.10) +
    (df['SoS_z'] * 0.05) + 
    (df['TD%_z'] * 0.05) +  
    (df['Att_z'] * 0.075) +
    (df['Rush EPA_z'] * 0.05) +
    (df['Succ%_z'] * 0.075) +
    (df['QBR_z'] * 0.05) +
    (df['Prss%_z'] * 0.05) -    
    (df['Int%_z'] * 0.05) -
    (df['Bad%_z'] * 0.075) -
    (df['Sk%_z'] * 0.025)
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


cluster_averages = df.groupby('Salary_Cluster')['APY'].mean().sort_values()
tier_map = {
    cluster_averages.index[0]: "Rookie/Cheap",
    cluster_averages.index[1]: "Bridge/Mid",
    cluster_averages.index[2]: "Franchise/Elite"
}
df['Contract_Tier'] = df['Salary_Cluster'].map(tier_map)

threshold = 35.0
backup_min, backup_max = 1.2, 10.0 
bridge_min, bridge_max = 10.0, 25.0  
starter_min, starter_max = 35.0, 65.0 
#------------------------------------MARKET VALUE ELITE/VETS -----------------------------------------#
def calculate_market_value(grade):
    if grade < threshold:
        return ((grade - 0) / (threshold - 0)) * (backup_max - backup_min) + backup_min
    elif grade <  50:
        return ((grade - threshold) / (50 - threshold)) * (bridge_max - bridge_min) + bridge_min
    else:
        return ((grade - threshold) / (100 - threshold)) * (starter_max - starter_min) + starter_min

vet_qbs_adj= df[df['Contract_Tier'].isin(['Franchise/Elite', 'Bridge/Mid'])].copy()
vet_qbs_adj['Market Value'] = vet_qbs_adj['Final_Grade'].apply(calculate_market_value).round(2)
vet_qbs_adj['APYM'] = vet_qbs_adj['APY'] / 1_000_000
vet_qbs_adj['Value Diff'] = (vet_qbs_adj['Market Value'] - vet_qbs_adj['APYM']).round(2)


ovr_vet_qb_adj_leaderboard = vet_qbs_adj[['Player', 'Value Diff', 'APY', 'Final_Grade', 'Contract_Tier', 'Market Value']].sort_values(by='Value Diff', ascending=False)
ovr_vet_qb_adj_leaderboard = ovr_vet_qb_adj_leaderboard.reset_index(drop=True)
ovr_vet_qb_adj_leaderboard.index = ovr_vet_qb_adj_leaderboard.index+1
print("\nOverall Leaderboard (Value Diff):")
print(ovr_vet_qb_adj_leaderboard.head(20))

#------------------------------------MARKET VALUE ROOKIES/CHEAP -----------------------------------------#
rookie_qbs = df[df['Contract_Tier'] == 'Rookie/Cheap'].copy()
rookie_qbs['Market Value'] = rookie_qbs['Final_Grade'].apply(calculate_market_value).round(2)
rookie_qbs['APYM'] = rookie_qbs['APY'] / 1_000_000
rookie_qbs['Value Diff'] = (rookie_qbs['Market Value'] - rookie_qbs['APYM']).round(2)
rookie_qb_leaderboard = rookie_qbs[['Player', 'Value Diff', 'APY', 'Final_Grade', 'Contract_Tier', 'Market Value']].sort_values(by='Value Diff', ascending=False)
rookie_qb_leaderboard = rookie_qb_leaderboard.reset_index(drop=True)
rookie_qb_leaderboard.index = rookie_qb_leaderboard.index+1
print("\nRookie/Cheap QB Leaderboard (Value Diff):")
print(rookie_qb_leaderboard.head(20))
