import pandas as pd
import re

def clean_numeric_columns(df, cols):
    for col in cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(r"[\*\$,]", "", regex=True)
                .replace("nan", None)
                .astype(float)
            )
    return df

def clean_contract(df):
    if 'Pos.' in df.columns:
        df = df.rename(columns={'Pos.': 'Pos'})
    df.drop(columns=["Total Value", "Total\nGuaranteed", "Avg.\nGuarantee/Year", "% Guaranteed"], inplace=True, errors='ignore')
    drop = ['RT', 'RG', 'C', 'LG', 'LT']
    if 'Pos.' in df.columns:
        df = df[~df['Pos.'].isin(drop)]
    return df

def promote_first_row_to_header(df):
    try:
        unnamed = any(str(c).startswith("Unnamed") for c in df.columns)
    except Exception:
        unnamed = False
    if unnamed or df.columns.duplicated().any():
        first_row = df.iloc[0].fillna("").astype(str).str.strip().tolist()
        if any(first_row):
            df = df.iloc[1:].copy()
            df.columns = first_row
            df = df.reset_index(drop=True)
    return df

# def convert_team_abbreviations(df, col):
#     if col not in df.columns:
#         return df
#     df[col] = df[col].astype(str).str.lower().str.strip()
#     abbreviation_map = {
#         'bills': 'BUF', 'dolphins': 'MIA', 'patriots': 'NE', 'jets': 'NYJ',
#         'ravens': 'BAL', 'bengals': 'CIN', 'browns': 'CLE', 'steelers': 'PIT',
#         'texans': 'HOU', 'colts': 'IND', 'jaguars': 'JAX', 'titans': 'TEN',
#         'broncos': 'DEN', 'chiefs': 'KC', 'raiders': 'LV', 'chargers': 'LAC',
#         'cowboys': 'DAL', 'giants': 'NYG', 'eagles': 'PHI', 'commanders': 'WAS',
#         'bears': 'CHI', 'lions': 'DET', 'packers': 'GB', 'vikings': 'MIN',
#         'falcons': 'ATL', 'panthers': 'CAR', 'saints': 'NO', 'buccaneers': 'TB',
#         'cardinals': 'ARI', 'rams': 'LAR', '49ers': 'SF', 'seahawks': 'SEA'
#     }
#     df[col] = df[col].map(abbreviation_map)
#     return df
def convert_team_abbreviations(df, col):
    abbreviation_map = {
        'bills': 'BUF', 'dolphins': 'MIA', 'patriots': 'NE', 'jets': 'NYJ',
        'ravens': 'BAL', 'bengals': 'CIN', 'browns': 'CLE', 'steelers': 'PIT',
        'texans': 'HOU', 'colts': 'IND', 'jaguars': 'JAX', 'titans': 'TEN',
        'broncos': 'DEN', 'chiefs': 'KC', 'raiders': 'LV', 'chargers': 'LAC',
        'cowboys': 'DAL', 'giants': 'NYG', 'eagles': 'PHI', 'commanders': 'WAS',
        'bears': 'CHI', 'lions': 'DET', 'packers': 'GB', 'vikings': 'MIN',
        'falcons': 'ATL', 'panthers': 'CAR', 'saints': 'NO', 'buccaneers': 'TB',
        'cardinals': 'ARI', 'rams': 'LAR', '49ers': 'SF', 'seahawks': 'SEA'
    }

    def find_team(text):
        text = str(text).lower()
        for nickname, abbr in abbreviation_map.items():
            if nickname in text: 
                return abbr
        return text 

    df[col] = df[col].apply(find_team)
    return df

def merge_dataframes(df1, df2, merge_col, remove_cols=None):
    if remove_cols is None:
        remove_cols = []
    cols_to_drop = [c for c in remove_cols if c in df2.columns]
    df_stats_cleaned = df2.drop(columns=cols_to_drop)
    return pd.merge(df1, df_stats_cleaned, on=merge_col, how='left')

def clean_nfl_string(text, sep='-', keep_left=True):
    if not isinstance(text, str):
        return None
    parts = text.split(sep)
    if len(parts) < 2:
        return text
    result = parts[0] if keep_left else parts[1]
    return result.strip()

def standardize_columns(df, cols):
    for col in cols:
        
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
       
        mean = df[col].mean()
        std = df[col].std()
        
     
        if std > 0:
            df[f'{col}_z'] = (df[col] - mean) / std
        else:
            df[f'{col}_z'] = 0
    return df

def fix_flacco_manually(df):
    flacco_rows = df[df['Player'] == 'Joe Flacco']
    
    if not flacco_rows.empty:
        clean_flacco = flacco_rows.iloc[0].copy()
        clean_flacco['Team'] = 'CIN'
        cin_sos = flacco_rows[flacco_rows['Team'] == 'CIN']['SoS']
        if not cin_sos.empty:
            clean_flacco['SoS'] = cin_sos.iloc[0]
        else:
            clean_flacco['SoS'] = -0.1 
        df = df[df['Player'] != 'Joe Flacco'].copy()
        df = pd.concat([df, pd.DataFrame([clean_flacco])], ignore_index=True)
    
    return df