from pathlib import Path
import pandas as pd
from utils import * # This imports all the functions from utils.py

def main():
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
        df_passing = pd.read_csv(raw / "passing_data.csv")
        df_rushing = pd.read_csv(raw / "rushing_data.csv")
        df_receiving = pd.read_csv(raw / "receiving_data.csv")
        df_passing_2 = pd.read_csv(raw / "qb_stats_sumer.csv")
    except FileNotFoundError as e:
        print("Data file not found:", e)
        return

    # CLEANING DATA (Your logic, exactly as provided)
    df_contracts = clean_contract(df_contracts)
    df_rushing = promote_first_row_to_header(df_rushing)
    df_receiving = promote_first_row_to_header(df_receiving)

    columns_to_clean_passing = ["G", "GS", "Cmp", "Att", "Cmp%", "Yds", "TD", "TD%", "Int", "Int%", "1D", "Succ%", "Lng", "Y/A", "AY/A", "Y/C", "Y/G", "Rate", "QBR", "Sk", "Sk%", "NY/A", "ANY/A", "4QC", "GWD", "Awards"]
    columns_to_clean_rushing = ["G", "GS", "Att", "Yds", "TD", "1D", "Succ%", "Lng", "Y/A", "Y/G", "A/G", "Fmb"]
    columns_to_clean_receiving = ["G", "GS", "Tgt", "Rec", "Yds", "1D", "YBC", "YBC/R", "YAC", "YAC/R", "ADOT", "BrkTkl", "Rec/Br", "Drop", "Drop%", "Int", "Rat"]

    df_contracts = convert_team_abbreviations(df_contracts, 'Team')
    df_passing = clean_numeric_columns(df_passing, columns_to_clean_passing)
    df_rushing = clean_numeric_columns(df_rushing, columns_to_clean_rushing)
    df_receiving = clean_numeric_columns(df_receiving, columns_to_clean_receiving)
    
    df_qb_only = df_passing[df_passing['Pos'] == 'QB'].copy()
    passing_2_cols_to_keep = ['Player Name', 'EPA/Play', 'Pass EPA', 'Rush EPA', 'ADoT', 'Time To Throw']
    df_passing_2 = df_passing_2[passing_2_cols_to_keep]
    df_passing_2 = df_passing_2.rename(columns={'Player Name': 'Player'})
    df_passing_2['Player'] = df_passing_2['Player'].apply(clean_nfl_string, sep = '.', keep_left=False)
    
    df_qb_only['QBrec'] = df_qb_only['QBrec'].astype(str)
    df_qb_only['QBrec'] = df_qb_only['QBrec'].apply(clean_nfl_string)
    df_rb_only = merge_dataframes(df_rushing, df_receiving, merge_col='Player')

    cols_to_remove_qb = ['Team', 'Pos', 'Rk', 'Age', 'G', 'GS', 'Cmp', 'Yds', 'TD', 'Int', '1D', 'SkYds', 'Y/A', 'AY/A', 'NY/A', 'Y/C', 'Cmp%', 'Lng', 'Sk', 'Yds.1','4QC', 'GWD', 'Awards']

    df_final_passing = merge_dataframes(df_contracts, df_qb_only, 'Player', cols_to_remove_qb)
    df_final_passing = merge_dataframes(df_final_passing, df_passing_2, 'Player')
    
    # NEW STEP: Save the result so grading.py can use it
    df_final_passing.to_csv("df_final_passing_cleaned.csv", index=False)
    print("Cleaned data saved to df_final_passing_cleaned.csv")

if __name__ == "__main__":
    main()