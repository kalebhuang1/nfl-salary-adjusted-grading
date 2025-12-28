from pathlib import Path
import pandas as pd
from utils import * 

def get_cleaned_data_wr():
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
        df_receiving = pd.read_csv(raw / "receiving_data.csv")
        df_opp_str_afc = pd.read_csv(raw / "opp_str_afc.csv")
        df_opp_str_nfc = pd.read_csv(raw / "opp_str_nfc.csv")
    except FileNotFoundError as e:
        print("Data file not found:", e)
        return
    df_contracts = clean_contract(df_contracts)
    df_receiving = promote_first_row_to_header(df_receiving)

    columns_to_clean_receiving = ["G", "GS", "Tgt", "Rec", "Yds", "1D", "YBC", "YBC/R", "YAC", "YAC/R", "ADOT", "BrkTkl", "Rec/Br", "Drop", "Drop%", "Int", "Rat"]
    df_receiving = clean_numeric_columns(df_receiving, columns_to_clean_receiving)

    df_opp_str = pd.concat([df_opp_str_afc, df_opp_str_nfc], ignore_index=True)
    df_opp_str['Tm'] = df_opp_str['Tm'].apply(clean_nfl_string, sep = '*', keep_left=True)
    df_opp_str['Tm'] = df_opp_str['Tm'].apply(clean_nfl_string, sep = '+', keep_left=True)
    df_opp_str = convert_team_abbreviations(df_opp_str, 'Tm')
    df_opp_str = df_opp_str.rename(columns={'Tm': 'Team'})
    df_opp_str = df_opp_str[['Team', 'SoS']]

    df_contracts = convert_team_abbreviations(df_contracts, 'Team')
    df_contracts['APY'] = df_contracts['APY'].astype(str).str.replace(r'[$, ]', '', regex=True)
    df_contracts['APY'] = pd.to_numeric(df_contracts['APY'], errors='coerce')
    df_contracts['APY'] = df_contracts['APY'].fillna(0)

    df_wr_only = df_receiving[df_receiving['Pos'] == 'WR'].copy()

if __name__ == "__main__":
    df = get_cleaned_data_wr()
    print(df.head())