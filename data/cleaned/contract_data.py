from pathlib import Path
import pandas as pd

# FUNCTIONS
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


def convert_team_abbreviations(df, col):
    if col not in df.columns:
        return df
    df[col] = df[col].astype(str).str.lower().str.strip()
    abbreviation_map = {
        'bills': 'BUF',
        'dolphins': 'MIA',
        'patriots': 'NE',
        'jets': 'NYJ',
        'ravens': 'BAL',
        'bengals': 'CIN',
        'browns': 'CLE',
        'steelers': 'PIT',
        'texans': 'HOU',
        'colts': 'IND',
        'jaguars': 'JAX',
        'titans': 'TEN',
        'broncos': 'DEN',
        'chiefs': 'KC',
        'raiders': 'LV',
        'chargers': 'LAC',
        'cowboys': 'DAL',
        'giants': 'NYG',
        'eagles': 'PHI',
        'commanders': 'WAS',
        'bears': 'CHI',
        'lions': 'DET',
        'packers': 'GB',
        'vikings': 'MIN',
        'falcons': 'ATL',
        'panthers': 'CAR',
        'saints': 'NO',
        'buccaneers': 'TB',
        'cardinals': 'ARI',
        'rams': 'LAR',
        '49ers': 'SF',
        'seahawks': 'SEA'
    }
    df[col] = df[col].map(abbreviation_map)
    return df


def merge_dataframes(df1, df2, merge_col, remove_cols=None):
    if remove_cols is None:
        remove_cols = []
    cols_to_drop = [c for c in remove_cols if c in df2.columns]
    df_stats_cleaned = df2.drop(columns=cols_to_drop)
    return pd.merge(df1, df_stats_cleaned, on=merge_col, how='left')


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
    except FileNotFoundError as e:
        print("Data file not found:", e)
        return

    # CLEANING DATA
    df_contracts = clean_contract(df_contracts)
    df_rushing = promote_first_row_to_header(df_rushing)
    df_receiving = promote_first_row_to_header(df_receiving)

    columns_to_clean_passing = [
        "G", "GS", "Cmp", "Att", "Cmp%", "Yds", "TD", "TD%", "Int", "Int%",
        "1D", "Succ%", "Lng", "Y/A", "AY/A", "Y/C", "Y/G", "Rate", "QBR", "Sk",
        "Sk%", "NY/A", "ANY/A", "4QC", "GWD", "Awards",
    ]
    columns_to_clean_rushing = ["G", "GS", "Att", "Yds", "TD", "1D", "Succ%", "Lng", "Y/A", "Y/G", "A/G", "Fmb"]
    columns_to_clean_receiving = [
        "G", "GS", "Tgt", "Rec", "Yds", "1D", "YBC", "YBC/R", "YAC", "YAC/R", "ADOT",
        "BrkTkl", "Rec/Br", "Drop", "Drop%", "Int", "Rat",
    ]

    df_contracts = convert_team_abbreviations(df_contracts, 'Team')
    df_passing = clean_numeric_columns(df_passing, columns_to_clean_passing)
    df_rushing = clean_numeric_columns(df_rushing, columns_to_clean_rushing)
    df_receiving = clean_numeric_columns(df_receiving, columns_to_clean_receiving)
    df_wr_te_only = df_receiving[df_receiving['Pos'].isin(['WR', 'TE'])]
    df_rb_combined = merge_dataframes(df_rushing, df_receiving, merge_col='Player')

    df_final_passing = merge_dataframes(
        df_contracts,
        df_passing,
        'Player',
        ['GS', 'QBrec', 'Sk', 'Yds.1', 'Sk%', 'NY/A', 'ANY/A', '4QC', 'GWD', 'Awards']
    )
    df_final_rushing = merge_dataframes(df_contracts[df_contracts['Pos'] == 'RB'], df_rb_combined, 'Player')
    df_final_receiving = merge_dataframes(df_contracts[df_contracts['Pos'].isin(['WR', 'TE'])], df_receiving, 'Player')
    
    pd.set_option('display.max_columns', None)
    # print('--- Contract Data ---')
    # print(df_contracts.head())
    # print('--- Passing Data ---')
    # print(df_passing.head())
    # print('--- Rushing Data ---')
    # print(df_rushing.head())
    # print('--- Receiving Data ---')
    # print(df_receiving.head())
    # print('--- Final Passing Data ---')
    # print(df_final_passing.head())
    print('--- Final Rushing Data ---')
    print(df_final_rushing.head())
    # print('--- Final Receiving Data ---')
    # print(df_final_receiving.head())
    print('--- Combined RB Data ---')
    print(df_rb_combined.head())


if __name__ == "__main__":
    main()