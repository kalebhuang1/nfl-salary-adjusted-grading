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
        df_rushing = pd.read_csv(raw / "rushing_data.csv")
        df_receiving = pd.read_csv(raw / "receiving_data.csv")
    except FileNotFoundError as e:
        print("Data file not found:", e)
        return

    df_contracts = clean_contract(df_contracts)
    df_contracts = df_contracts[df_contracts['Pos'] == 'RB'].copy()
    df_contracts['APY'] = df_contracts['APY'].astype(str).str.replace(r'[$, ]', '', regex=True)
    df_contracts['APY'] = pd.to_numeric(df_contracts['APY'], errors='coerce')
    df_contracts= normalize_player_names(df_contracts,'Player')
    print(df_contracts.head())

    df_rushing = promote_first_row_to_header(df_rushing)
    df_rushing = normalize_player_names(df_rushing,'Player')
    df_rushing = df_rushing[df_rushing['Pos'] == 'RB'].copy()
    basic_rush_cols = ['Player', 'Team', 'G', 'Att', 'Yds', 'TD', 'Succ%', 'Y/A', 'Y/G', 'Fmb']
    df_rushing = df_rushing[basic_rush_cols]
    df_rushing = clean_numeric_columns(df_rushing, basic_rush_cols[2:])
    print(df_rushing.head())
    df_receiving = promote_first_row_to_header(df_receiving)

if __name__ == "__main__":
    df = get_cleaned_data_rb()  