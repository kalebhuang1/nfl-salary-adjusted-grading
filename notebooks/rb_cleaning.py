from pathlib import Path
import pandas as pd
from utils import * 


pd.set_option('display.max_columns', None)
pd.set_option('display.width', 100)
def get_cleaned_data_rb():
    p = Path(__file__).resolve()
    base = None
    for parent in p.parents:
        if (parent / "data").exists():
            base = parent
            break
    if base is None:
        base = p.parents[3]
    raw = base / "data" / "raw"

    try:
        df_contracts = pd.read_csv(raw / "contract_data.csv")
        df_rushing = pd.read_csv(raw / "sumer_rb_data.csv")
    except FileNotFoundError as e:
        print("Data file not found:", e)
        return

    df_contracts = clean_contract(df_contracts)
    df_contracts = df_contracts[df_contracts['Pos'] == 'RB'].copy()
    df_contracts['APY'] = df_contracts['APY'].astype(str).str.replace(r'[$, ]', '', regex=True)
    df_contracts['APY'] = pd.to_numeric(df_contracts['APY'], errors='coerce')
    df_contracts = normalize_player_names(df_contracts,'Player')
    df_contracts['Team'] = df_contracts['Team'].str.lower()
    df_contracts = convert_team_abbreviations(df_contracts, 'Team')
    df_contracts['Player Merge'] = df_contracts['Player'].str.lower()
    print(df_contracts.head())

    df_rushing = df_rushing.rename(columns = {'Player Name': 'Player'})
    df_rushing['Player'] = df_rushing['Player'].str.replace(r'^\d+\.\s*', '', regex=True).str.strip()
    df_rushing = normalize_player_names(df_rushing, 'Player')
    df_rushing['Player Merge'] = df_rushing['Player'].str.lower()
    cols_to_remove = ['Season','Team', 'Position', 'Total EPA', 'First Down %']
    df_rushing = df_rushing.drop(columns=cols_to_remove, errors='ignore')
    print(df_rushing.head())

    
    df_final_rushing = pd.merge(df_rushing, df_contracts[['Team', 'Pos', 'APY', 'Player Merge']], on='Player Merge', how='left')
    df_final_rushing = df_final_rushing.replace('%', '', regex=True)
    df_final_rushing = df_final_rushing.apply(pd.to_numeric, errors='ignore')
    print("Final Rushing Data:")
    print(df_final_rushing.head(20))

if __name__ == "__main__":
    df = get_cleaned_data_rb()  