import pandas as pd
from utils import standardize_columns
from qb_cleaning import get_cleaned_data_qb
from sklearn.cluster import KMeans
import numpy as np




pd.set_option('display.width', 100)

#------------------------------------GRADING------------------------------------------------------#

def calculate_final_grade(df, att_min=0):
    WEIGHTS = {
        'EPA/Play': 0.275, 'ANY/A': 0.25, 'IAY/PA': 0.125, 'OnTgt%': 0.075,
        'Succ%': 0.075, 'SoS': 0.05, 'TD%': 0.05, 'Rush EPA': 0.05,
        'QBR': 0.025, 'Prss%': 0.05, 'Att': 0.025,
        'Int%': -0.05, 'Bad%': -0.075, 'Sk%': -0.025
    }
    
    df = df[df['Att'] >= (att_min - 1e-9)].copy()
    drivers = list(WEIGHTS.keys())
    df[drivers] = df[drivers].fillna(0)
    df['Att'] = df['Att'].fillna(0)

    calib_mask = df['Att'] >= 150
    calib_pool = df[calib_mask] if calib_mask.sum() >= 10 else df.nlargest(32, 'Att')
    
    stats = calib_pool[drivers].agg(['mean', 'std']).T
    stats['std'] = stats['std'].replace(0, 1) 
    
    z_scores = (df[drivers] - stats['mean']) / stats['std']
    
    df['Composite_Z'] = z_scores.dot(pd.Series(WEIGHTS))

    ramp = (df['Att'] / 250).clip(upper=1.0)
    df['Composite_Z'] *= ramp
    
    calib_z = df.loc[calib_mask, 'Composite_Z']
    min_z, max_z = (calib_z.min(), calib_z.max()) if not calib_z.empty else (df['Composite_Z'].min(), df['Composite_Z'].max())
    
    df['Final_Grade'] = ((df['Composite_Z'] - min_z) / (max_z - min_z) * 100).clip(0, 100)
    df['Final_Grade'] = (df['Final_Grade'] * ramp).round(2)
    
    if 'GS' in df.columns:
        df.loc[df['GS'] == 0, ['Composite_Z', 'Final_Grade']] = [df['Composite_Z'].min() - 1, 0]

    return df.sort_values(by='Final_Grade', ascending=False).reset_index(drop=True)
#------------------------------------------------------CONTRACTS-------------------------------------------------------------------#
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

def get_market_data(df):
    xp = [0,   30,  40,    50,    60,    70,    85,    100]
    fp = [1.2, 3.5, 12.0,  30.0,  42.0,  52.0,  58.0,  65.0]
    
    df['Market Value'] = np.interp(df['Final_Grade'], xp, fp).round(2)
    df['APYM'] = df['APY'] / 1_000_000
    df['Value Diff'] = (df['Market Value'] - df['APYM']).round(2)
    return df

df = get_cleaned_data_qb()
df['Att'] = df['Att'].fillna(0)
df=calculate_final_grade(df, 0)
df=assign_contract_tiers(df)
df=get_market_data(df)
#--------------------------------------------LEADERBOARDS-------------------------------------------------------------------------#
cols = ['Player', 'Team', 'Value Diff', 'APY', 'Final_Grade', 'Contract_Tier', 'Market Value']


vet_qbs = df[df['Contract_Tier'].isin(['Franchise/Elite', 'Bridge/Mid'])].copy()
rookie_qbs = df[df['Contract_Tier'] == 'Rookie/Cheap'].copy()

print("\nOverall Leaderboard (Value Diff):")
vet_print = vet_qbs[cols].sort_values('Value Diff', ascending=False).head(30).reset_index(drop=True)
vet_print.index = range(1, len(vet_print) + 1) 
print(vet_print)

print("\nRookie/Cheap QB Leaderboard (Value Diff):")
rookie_print = rookie_qbs[cols].sort_values('Value Diff', ascending=False).head(30).reset_index(drop=True)
rookie_print.index = range(1, len(rookie_print) + 1)
print(rookie_print)

df.to_csv('qb_market_data.csv', index=False)
