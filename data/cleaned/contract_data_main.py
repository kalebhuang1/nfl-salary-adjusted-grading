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
