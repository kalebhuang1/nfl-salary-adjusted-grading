from curses import raw
import pandas as pd
import re
from pathlib import Path

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

def normalize_player_names(df, name_col='Player'):
   
    df = df.copy()
    df[name_col] = df[name_col].str.strip().str.title()
    suffixes = r'\b(Jr|Sr|II|III|IV|V|iii|iv|Iv|Iii|Ii)\.?\b'
    df[name_col] = df[name_col].str.replace(suffixes, '', regex=True, flags=re.IGNORECASE)

    df[name_col] = df[name_col].str.replace(r'[.\']', '', regex=True)
    
    df[name_col] = df[name_col].str.replace(r'\s+', ' ', regex=True).str.strip()
    
    return df

def fix_nan(df, zero_cols, average_cols, percentile_cols, pct_val):
    df = df.copy()

    all_to_fix = [
        (zero_cols, "zero"), 
        (average_cols, "mean"), 
        (percentile_cols, "percentile")
    ]
    for col_list, method in all_to_fix:
        for col in col_list: 
            if col in df.columns:
                if method == "zero":
                    df[col] = df[col].fillna(0)
                elif method == "mean":
                    df[col] = df[col].fillna(df[col].mean())
                elif method == "percentile":
                    df[col] = df[col].fillna(df[col].quantile(pct_val))
    
    return df

def wins_export():
    raw = Path("data/raw")
    df_opp_str_afc = pd.read_csv(raw / "opp_str_afc.csv")
    df_opp_str_nfc = pd.read_csv(raw / "opp_str_nfc.csv")
    df_team_wins = pd.concat([df_opp_str_afc, df_opp_str_nfc], ignore_index=True)
    df_team_wins['Tm'] = df_team_wins['Tm'].apply(clean_nfl_string, sep = '*', keep_left=True)
    df_team_wins['Tm'] = df_team_wins['Tm'].apply(clean_nfl_string, sep = '+', keep_left=True)
    df_team_wins = convert_team_abbreviations(df_team_wins, 'Tm')
    df_team_wins = df_team_wins.rename(columns={'Tm': 'Team'})
    df_team_wins = df_team_wins[['Team', 'W']]
    return df_team_wins   
