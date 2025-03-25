import pandas as pd
import numpy as np

def get_csv(season: int, tourney: str):
    df = pd.read_csv(f"tournament_draft_csvs/drafts_s{season}_{tourney}.csv")
    return df

def preprocess_ban_data(df: pd.DataFrame):
    ban_columns = ["blue_bans", "red_bans"]
    patch_column = "patch"

    if not all(col in df.columns for col in [*ban_columns, patch_column, "winner"]):
        raise ValueError("Missing required columns in the DataFrame")

    processed_bans = []
    grouped_df = df.groupby(df.index // 6)
    for _, group in grouped_df:
        blue_bans = group["blue_bans"].tolist()[:-1]
        red_bans = group["red_bans"].tolist()[:-1]
        patch = group[patch_column].iloc[0]
        winner = group["winner"].iloc[5]
        processed_bans.append({
            "blue_bans": blue_bans,
            "red_bans": red_bans,
            "patch": patch,
            "winner": winner
        })
    return pd.DataFrame(processed_bans)

def clean_ban_data(df: pd.DataFrame):
    df["winner"] = df["winner"].map({"blue_side": 1.0, "red_side": 0.0})
    if df["winner"].isna().any():
        raise ValueError("Invalid value found in winner column. Expected 'blue_side' or 'red_side'")

def main():
    df = get_csv(14, "LCK Summer Playoffs 2024")
    df = preprocess_ban_data(df)
    clean_ban_data(df)
    print(df)

if __name__ == "__main__":
    main()
