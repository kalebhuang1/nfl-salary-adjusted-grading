from pathlib import Path
import pandas as pd
from utils import * 

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 100)
def get_cleaned_data_qb():
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
        df_passing_adv = pd.read_csv(raw / "adv_passing.csv")
        df_opp_str_afc = pd.read_csv(raw / "opp_str_afc.csv")
        df_opp_str_nfc = pd.read_csv(raw / "opp_str_nfc.csv")
    except FileNotFoundError as e:
        print("Data file not found:", e)
        return
#------------------------------------CLEANING------------------------------------------------------#
    df_contracts = clean_contract(df_contracts)
    df_rushing = promote_first_row_to_header(df_rushing)
    df_receiving = promote_first_row_to_header(df_receiving)
    df_passing_adv = promote_first_row_to_header(df_passing_adv)

    df_opp_str = pd.concat([df_opp_str_afc, df_opp_str_nfc], ignore_index=True)
    df_opp_str['Tm'] = df_opp_str['Tm'].apply(clean_nfl_string, sep = '*', keep_left=True)
    df_opp_str['Tm'] = df_opp_str['Tm'].apply(clean_nfl_string, sep = '+', keep_left=True)
    df_opp_str = convert_team_abbreviations(df_opp_str, 'Tm')
    df_opp_str = df_opp_str.rename(columns={'Tm': 'Team'})
    df_opp_str = df_opp_str[['Team', 'SoS']]
    

    columns_to_clean_passing = ["G", "GS", "Cmp", "Att", "Cmp%", "Yds", "TD", "TD%", "Int", "Int%", "1D", "Succ%", "Lng", "Y/A", "AY/A", "Y/C", "Y/G", "Rate", "QBR", "Sk", "Sk%", "NY/A", "ANY/A", "4QC", "GWD"]
    # columns_to_clean_rushing = ["G", "GS", "Att", "Yds", "TD", "1D", "Succ%", "Lng", "Y/A", "Y/G", "A/G", "Fmb"]
    # columns_to_clean_receiving = ["G", "GS", "Tgt", "Rec", "Yds", "1D", "YBC", "YBC/R", "YAC", "YAC/R", "ADOT", "BrkTkl", "Rec/Br", "Drop", "Drop%", "Int", "Rat"]

    df_contracts = convert_team_abbreviations(df_contracts, 'Team')
    df_contracts['Player'] = df_contracts['Player'].replace('Matt Stafford', 'Matthew Stafford')
    df_contracts['APY'] = df_contracts['APY'].astype(str).str.replace(r'[$, ]', '', regex=True)
    df_contracts['APY'] = pd.to_numeric(df_contracts['APY'], errors='coerce')
    df_contracts['APY'] = df_contracts['APY'].fillna(0)
    df_contracts['Player'] = df_contracts['Player'].replace('Michael Penix Jr.', 'Michael Penix')
    df_contracts = normalize_player_names(df_contracts, 'Player')   
    df_contracts_qb = df_contracts[df_contracts['Pos'] == 'QB'].copy()

    df_passing.drop(columns = ['Awards'], inplace=True, errors='ignore')
    df_passing = clean_numeric_columns(df_passing, columns_to_clean_passing)
    df_passing = normalize_player_names(df_passing, 'Player')
    # df_rushing = clean_numeric_columns(df_rushing, columns_to_clean_rushing)
    # df_receiving = clean_numeric_columns(df_receiving, columns_to_clean_receiving)
    
    df_qb_only = df_passing[df_passing['Pos'] == 'QB'].copy()
    passing_2_cols_to_keep = ['Player Name', 'EPA/Play', 'Pass EPA', 'Rush EPA', 'ADoT', 'Time To Throw']
    df_passing_2 = df_passing_2[passing_2_cols_to_keep]
    df_passing_2 = df_passing_2.rename(columns={'Player Name': 'Player'})
    df_passing_2['Player'] = df_passing_2['Player'].str.replace(r'^\d+\.\s*', '', regex=True).str.strip()
    df_passing_2 = normalize_player_names(df_passing_2, 'Player')
    df_passing_2['Player'] = df_passing_2['Player'].replace('Cameron Ward', 'Cam Ward')

    passing_adv_cols_to_keep = ['Player', 'IAY/PA', 'Bad%', 'Prss%', 'OnTgt%']
    df_passing_adv = df_passing_adv[passing_adv_cols_to_keep]
    df_passing_adv = normalize_player_names(df_passing_adv, 'Player')
    df_qb_only['QBrec'] = df_qb_only['QBrec'].astype(str)
    df_qb_only['QBrec'] = df_qb_only['QBrec'].apply(clean_nfl_string)
    df_rb_only = merge_dataframes(df_rushing, df_receiving, merge_col='Player')
    
    cols_to_remove_qb = ['Team', 'Pos', 'Rk', 'Age', 'G', 'Cmp', 'Yds', 'TD', 'Int', '1D', 'SkYds', 'Y/A', 'AY/A', 'NY/A', 'Y/C', 'Cmp%', 'Lng', 'Sk', 'Yds.1','4QC', 'GWD', 'Awards']
    df_qb_only = df_qb_only.drop(columns=cols_to_remove_qb, errors='ignore')
#-------------------------------------MERGING------------------------------------------------------#
    df_final_passing = merge_dataframes(df_contracts_qb, df_qb_only, 'Player')
    
    print(df_final_passing)
    df_final_passing = merge_dataframes(df_final_passing, df_passing_2, 'Player')
    df_final_passing = merge_dataframes(df_final_passing, df_passing_adv, 'Player')
    df_final_passing = merge_dataframes(df_final_passing, df_opp_str, 'Team')
    
    if 'Team' in df_final_passing.columns:
        df_final_passing = df_final_passing[df_final_passing['Team'] != '2TM'].copy()
    df_final_passing = df_final_passing.drop_duplicates(subset=['Player', 'Team'], keep='first')
    df_final_passing.loc[(df_final_passing['Player'] == 'Joe Flacco') & (df_final_passing['QBR'].isna()), 'QBR'] = 40.9

    for col in ['Prss%', 'Bad%', 'OnTgt%', 'IAY/PA']:
        df_final_passing[col] = df_final_passing[col].astype(str).str.replace('%', '', regex=False)
        df_final_passing[col] = pd.to_numeric(df_final_passing[col], errors='coerce')
    

    zero_cols = ['TD%', 'Int%', 'Rush EPA', 'Pass EPA', 'EPA/Play', 'Succ%', 'GS']
    percentile_cols = ['QBR', 'Rate', 'OnTgt%', 'IAY/PA', 'ANY/A']
    average_cols = ['Time To Throw', 'ADoT', 'Prss%', 'Bad%']

       
   

    df_final_passing = fix_nan(df_final_passing, zero_cols, average_cols, percentile_cols, 0.1)

    return df_final_passing


if __name__ == "__main__":
    df = get_cleaned_data_qb()
    # print(df.head(10))