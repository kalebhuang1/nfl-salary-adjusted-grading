from pathlib import Path
import pandas as pd


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


def promote_first_row_to_header(df):
    # If columns are unnamed or the first row looks like header labels, promote it
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
    df[col] = df[col].str.lower().str.strip()
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

        # promote first data row to header only for rushing and receiving
        df_rushing = promote_first_row_to_header(df_rushing)
        df_receiving = promote_first_row_to_header(df_receiving)
    except FileNotFoundError as e: 
        print("Data file not found:", e)
        return

    #df_rushing.drop(df_rushing.index[0], inplace=True)
    #df_receiving.drop(df_receiving.index[0], inplace=True)

    columns_to_clean_passing = [
        "G","GS","Cmp","Att","Cmp%","Yds","TD","TD%","Int","Int%",
        "1D","Succ%","Lng","Y/A","AY/A","Y/C","Y/G","Rate","QBR","Sk",
        "Yds","Sk%","NY/A","ANY/A","4QC","GWD","Awards",
    ]
    columns_to_clean_rushing = ["G","GS","Att","Yds","TD","1D","Succ%","Lng","Y/A","Y/G","A/G","Fmb"]
    columns_to_clean_receiving = [
        "G","GS","Tgt","Rec","Yds","1D","YBC","YBC/R","YAC","YAC/R","ADOT",
        "BrkTkl","Rec/Br","Drop","Drop%","Int","Rat",
    ]
    df_contracts = convert_team_abbreviations(df_contracts, 'Team')
    df_passing = clean_numeric_columns(df_passing, columns_to_clean_passing)
    df_rushing = clean_numeric_columns(df_rushing, columns_to_clean_rushing)
    df_receiving = clean_numeric_columns(df_receiving, columns_to_clean_receiving)

    df_contracts.drop(columns={"Total Value", "Total\nGuaranteed", "Avg.\nGuarantee/Year", "% Guaranteed"}, inplace=True)

    print(df_contracts.head())
    print(df_passing.head())
    print(df_rushing.head())
    print(df_receiving.head())


if __name__ == "__main__":
    main()
from pathlib import Path
import pandas as pd


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


def main():
    # locate repo root by searching parents for a 'data' directory
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

    df_rushing.drop(df_rushing.index[0], inplace=True)
    df_receiving.drop(df_receiving.index[0], inplace=True)

    columns_to_clean_passing = [
        "G","GS","Cmp","Att","Cmp%","Yds","TD","TD%","Int","Int%",
        "1D","Succ%","Lng","Y/A","AY/A","Y/C","Y/G","Rate","QBR","Sk",
        "Yds","Sk%","NY/A","ANY/A","4QC","GWD","Awards",
    ]
    columns_to_clean_rushing = ["G","GS","Att","Yds","TD","1D","Succ%","Lng","Y/A","Y/G","A/G","Fmb"]
    columns_to_clean_receiving = [
        "G","GS","Tgt","Rec","Yds","1D","YBC","YBC/R","YAC","YAC/R","ADOT",
        "BrkTkl","Rec/Br","Drop","Drop%","Int","Rat",
    ]

    df_passing = clean_numeric_columns(df_passing, columns_to_clean_passing)
    df_rushing = clean_numeric_columns(df_rushing, columns_to_clean_rushing)
    df_receiving = clean_numeric_columns(df_receiving, columns_to_clean_receiving)

    df_contracts.drop(columns={"Total Value", "Total\nGuaranteed", "Avg.\nGuarantee/Year", "% Guaranteed"}, inplace=True)

    print(df_contracts.head())
    print(df_passing.head())
    from pathlib import Path
    import pandas as pd


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


    def main():
        # find repo root by locating a parent that contains the "data" directory
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

        df_rushing.drop(df_rushing.index[0], inplace=True)
        df_receiving.drop(df_receiving.index[0], inplace=True)

        columns_to_clean_passing = [
            "G","GS","Cmp","Att","Cmp%","Yds","TD","TD%","Int","Int%",
            "1D","Succ%","Lng","Y/A","AY/A","Y/C","Y/G","Rate","QBR","Sk",
            "Yds","Sk%","NY/A","ANY/A","4QC","GWD","Awards",
        ]
        columns_to_clean_rushing = ["G","GS","Att","Yds","TD","1D","Succ%","Lng","Y/A","Y/G","A/G","Fmb"]
        columns_to_clean_receiving = [
            "G","GS","Tgt","Rec","Yds","1D","YBC","YBC/R","YAC","YAC/R","ADOT",
            "BrkTkl","Rec/Br","Drop","Drop%","Int","Rat",
        ]

        df_passing = clean_numeric_columns(df_passing, columns_to_clean_passing)
        df_rushing = clean_numeric_columns(df_rushing, columns_to_clean_rushing)
        df_receiving = clean_numeric_columns(df_receiving, columns_to_clean_receiving)

        df_contracts.drop(columns={"Total Value", "Total\nGuaranteed", "Avg.\nGuarantee/Year", "% Guaranteed"}, inplace=True)

        print(df_contracts.head())
        print(df_passing.head())
        print(df_rushing.head())
        print(df_receiving.head())


    if __name__ == "__main__":
        main()