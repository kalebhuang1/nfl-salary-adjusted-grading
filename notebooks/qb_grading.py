import pandas as pd
from utils import standardize_columns
pd.set_option('display.max_columns', None)

# 2. Prevent the table from 'wrapping' to a new line
pd.set_option('display.width', 100)
# Load the file created by cleaning.py
df = pd.read_csv("df_final_passing_cleaned.csv")
df = df[df['Att'] >= 200].copy()
drivers = ['ANY/A', 'EPA/Play', 'QBR', 'Succ%', 'Int%', 'Sk%', 'Att', 'Rush EPA']
df = standardize_columns(df, drivers)
df['Composite_Z'] = (
    (df['EPA/Play_z'] * 0.25) +
    (df['ANY/A_z'] * 0.25) +
    (df['Att_z'] * 0.075) +      # High volume players get a massive boost here
    (df['QBR_z'] * 0.10) +
    (df['Rush EPA_z']* 0.10) +
    (df['Succ%_z'] * 0.10) -
    (df['Int%_z'] * 0.075) -
    (df['Sk%_z'] * 0.05)
)
# print(df.head())

min_z = df['Composite_Z'].min()
max_z = df['Composite_Z'].max()
df['Final_Grade'] = ((df['Composite_Z'] - min_z) / (max_z - min_z)) * 100
df['Final_Grade'] = df['Final_Grade'].round(1)
df = df.sort_values(by='Final_Grade', ascending=False).reset_index(drop=True)

df.index = df.index + 1

leaderboard = df[['Player', 'Final_Grade', 'Att', 'EPA/Play', 'ANY/A']].sort_values(by='Final_Grade', ascending=False)
print(leaderboard.head(20))
