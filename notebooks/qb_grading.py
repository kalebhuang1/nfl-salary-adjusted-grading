import pandas as pd
from utils import standardize_columns
pd.set_option('display.max_columns', None)

# 2. Prevent the table from 'wrapping' to a new line
pd.set_option('display.width', 100)
# Load the file created by cleaning.py
df = pd.read_csv("df_final_passing_cleaned.csv")

# Identify the stats you want to use for your metric
# Example list based on what you have:
my_stats = ['ANY/A', 'QBR', 'EPA/Play', 'Succ%']

# Apply your function
df = standardize_columns(df, my_stats)

# Preview your work
print(df.head())
print(df[['Player'] + [f'{col}_z' for col in my_stats]].head())
