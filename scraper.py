import enum
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

GOLGG_BASE_URL = "https://gol.gg/"
GOLGG_TOURNAMENT_ENDPOINT = "tournament/list/"
GOL_GG_BANS_ENDPOINT = "champion/bans-stats/"
GOL_GG_PICKBAN_BY_PATCH_ENDPOINT = "stats/patches-by-patches/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
}

class Split(enum.Enum):
    WINTER = "split-Winter/"
    SUMMER = "split-Summer/"
    SPRING = "split-Spring/"
    ALL = "split-ALL/"

def GOL_GG_SEASON_SPLIT_URL_GEN(season: int, split: Split):
    return f"season-S{season}/{split.value}"

def scrape_pick_ban_by_patch(url: str):
    """
    Scrapes pick/ban data from gol.gg for a given season and split.

    Args:
        url (str): The URL to scrape pick/ban data from.

    Returns:
        pd.DataFrame: A DataFrame containing the pick/ban data.
    """
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', class_='table_list playerslist tablesaw')
    if table is None:
        raise Exception("Table not found")
    
    data = []

    for row in table.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) >= 2:
            champion = cells[0].text.strip()
            pick_ban_percentage = cells[1].text.strip()
            data.append([champion, pick_ban_percentage])

    return pd.DataFrame(data, columns=['Champion', 'Pick/Ban Percentage'])

def main():
    c_url = GOLGG_BASE_URL + GOL_GG_PICKBAN_BY_PATCH_ENDPOINT + GOL_GG_SEASON_SPLIT_URL_GEN(15, Split.WINTER)
    df = scrape_pick_ban_by_patch(c_url)
    print(df)
    df.to_csv("pick_ban_by_patch.csv", index=False)

if __name__ == "__main__":
    main()
