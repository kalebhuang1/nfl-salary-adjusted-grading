import pandas as pd
from utils import standardize_columns
from qb_cleaning import get_cleaned_data_qb
from sklearn.cluster import KMeans




pd.set_option('display.width', 100)

#------------------------------------GRADING------------------------------------------------------#
df = get_cleaned_data_qb()
df['Att'] = df['Att'].fillna(0)

def calculate_ramp_penalty(att, limit=250):
    if att >= limit:
        return 1.0
    return att / limit

def calculate_final_grade(df, att_min=0):
    df = df[df['Att'] >= (att_min - 1e-9)].copy()
    
    drivers = ['ANY/A', 'EPA/Play', 'QBR', 'Succ%', 'Int%', 'Sk%', 'Att', 'Rush EPA', 'TD%', 'IAY/PA','Bad%', 'Prss%', 'OnTgt%', 'SoS']
    df[drivers] = df[drivers].fillna(0)
    
    z_cols = [f"{col}_z" for col in drivers]
    df_active = df[df['Att'] > 0].copy()
    df_inactive = df[df['Att'] <= 0].copy()

    if not df_active.empty:
        calibration_pool = df_active[df_active['Att'] >= 150] 
        
        if len(calibration_pool) < 10:
            calibration_pool = df_active.nlargest(32, 'Att')


        for col in drivers:
            mu = calibration_pool[col].mean()
            sigma = calibration_pool[col].std()
            
            sigma = sigma if sigma > 0 else 1.0 
            
            df_active[f"{col}_z"] = (df_active[col] - mu) / sigma

    for col in z_cols:
        df_inactive[col] = -3.0
        
    df = pd.concat([df_active, df_inactive], axis=0).reset_index(drop=True)

    df['Composite_Z'] = (
        (df['EPA/Play_z'] * 0.275) +
        (df['ANY/A_z'] * 0.25) +
        (df['OnTgt%_z'] * 0.075) +
        (df['IAY/PA_z'] * 0.10) +
        (df['SoS_z'] * 0.05) + 
        (df['TD%_z'] * 0.05) +  
        (df['Att_z'] * 0.025) +
        (df['Rush EPA_z'] * 0.05) +
        (df['Succ%_z'] * 0.075) +
        (df['QBR_z'] * 0.05) +
        (df['Prss%_z'] * 0.05) -    
        (df['Int%_z'] * 0.05) -
        (df['Bad%_z'] * 0.075) -
        (df['Sk%_z'] * 0.025)
    )

    df['Composite_Z'] = df['Composite_Z'] * df['Att'].apply(calculate_ramp_penalty)
    
    if 'GS' in df.columns:
        df.loc[df['GS'] == 0, 'Composite_Z'] = df['Composite_Z'].min() - 1


    calibration_z = df[df['Att'] >= 150]['Composite_Z']
    if not calibration_z.empty:
        min_z = calibration_z.min()
        max_z = calibration_z.max()
    else:
        min_z = df['Composite_Z'].min()
        max_z = df['Composite_Z'].max()
    
    df['Final_Grade'] = ((df['Composite_Z'] - min_z) / (max_z - min_z)) * 100
    df['Final_Grade'] = df['Final_Grade'] * df['Att'].apply(lambda x: calculate_ramp_penalty(x, limit=250))
    df['Final_Grade'] = df['Final_Grade'].clip(0, 100).round(2)
    
    if 'GS' in df.columns:
        df.loc[df['GS'] == 0, 'Final_Grade'] = 0

    df = df.sort_values(by='Final_Grade', ascending=False).reset_index(drop=True)
    df.index = df.index + 1

    return df

#------------------------------------CONTRACTS------------------------------------------------------#
def assign_contract_tiers(df):
    X = df[['APY']].values
    kmeans = KMeans(n_clusters=3, random_state=42)
    df['Salary_Cluster'] = kmeans.fit_predict(X)
    cluster_averages = df.groupby('Salary_Cluster')['APY'].mean().sort_values()
    tier_map = {
        cluster_averages.index[0]: "Rookie/Cheap",
        cluster_averages.index[1]: "Bridge/Mid",
        cluster_averages.index[2]: "Franchise/Elite"
    }
    df['Contract_Tier'] = df['Salary_Cluster'].map(tier_map)
    return df

threshold = 35.0
backup_min, backup_max = 1.2, 10.0 
bridge_min, bridge_max = 10.0, 25.0  
starter_min, starter_max = 35.0, 65.0 

def calculate_market_value(grade):
    if grade < threshold:
        return ((grade - 0) / (threshold - 0)) * (backup_max - backup_min) + backup_min
    elif grade <  50:
        return ((grade - threshold) / (50 - threshold)) * (bridge_max - bridge_min) + bridge_min
    else:
        return ((grade - threshold) / (100 - threshold)) * (starter_max - starter_min) + starter_min

def market_data(df, group_col):
    df = df[df['Contract_Tier'].isin(group_col)].copy()
    df['Market Value'] = df['Final_Grade'].apply(calculate_market_value).round(2)
    df['APYM'] = df['APY'] / 1_000_000
    df['Value Diff'] = (df['Market Value'] - df['APYM']).round(2)
    return df
df=calculate_final_grade(df, 0)
df=assign_contract_tiers(df)
#------------------------------------MARKET VALUE ELITE/VETS -----------------------------------------#

vet_qbs_adj= market_data(df, ['Franchise/Elite', 'Bridge/Mid'])
ovr_vet_qb_adj_leaderboard = vet_qbs_adj[['Player', 'Team', 'Value Diff', 'APY', 'Final_Grade', 'Contract_Tier', 'Market Value']].sort_values(by='Value Diff', ascending=False)
ovr_vet_qb_adj_leaderboard = ovr_vet_qb_adj_leaderboard.reset_index(drop=True)
ovr_vet_qb_adj_leaderboard.index = ovr_vet_qb_adj_leaderboard.index+1
print("\nOverall Leaderboard (Value Diff):")
print(ovr_vet_qb_adj_leaderboard.head(30))

#------------------------------------MARKET VALUE ROOKIES/CHEAP -----------------------------------------#
rookie_qbs = market_data(df, ['Rookie/Cheap'])
rookie_qb_leaderboard = rookie_qbs[['Player', 'Team', 'Value Diff', 'APY', 'Final_Grade', 'Contract_Tier', 'Market Value']].sort_values(by='Value Diff', ascending=False)
rookie_qb_leaderboard = rookie_qb_leaderboard.reset_index(drop=True)
rookie_qb_leaderboard.index = rookie_qb_leaderboard.index+1
print("\nRookie/Cheap QB Leaderboard (Value Diff):")
print(rookie_qb_leaderboard.head(30))


df_market_master = pd.concat([vet_qbs_adj, rookie_qbs], ignore_index=True)
df_market_master.to_csv('qb_market_data.csv', index=False)
