import enum
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
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

def scrape_pick_ban_by_patch(url: str) -> pd.DataFrame:
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
        return pd.DataFrame()

    soup = BeautifulSoup(response.content, 'html.parser')
    
    headers = soup.find_all('th')
    patch_headers = [header.text.strip() for header in headers]
    
    # Find all table cells
    cells = soup.find_all('td', {'style': 'vertical-align:top'})
    
    all_champions_data = []
    
    # Process each cell (corresponds to a patch)
    for i, cell in enumerate(cells):
        patch = patch_headers[i] if i < len(patch_headers) else f"Unknown_Patch_{i}"
        
        # Find all champion divs in this cell
        champion_divs = cell.find_all('div', {'class': re.compile(r'[A-Za-z]')})
        
        # Filter out divs that don't contain champion data
        champion_divs = [div for div in champion_divs if div.get('onmouseover') and 'setBg' in div.get('onmouseover')]
        
        for div in champion_divs:
            # Extract champion name
            champion_name = div.get('class')[0]
            
            # Extract percentage value
            percentage_text = div.text.strip()
            percentage_match = re.search(r'(\d+)%', percentage_text)
            percentage = int(percentage_match.group(1)) if percentage_match else None
            
            # Get the champion ID from the URL
            link = div.find('a')
            if link:
                champion_id_match = re.search(r'/champion-stats/(\d+)/', link.get('href'))
                champion_id = champion_id_match.group(1) if champion_id_match else None
            else:
                champion_id = None
            
            all_champions_data.append({
                'name': champion_name,
                'percentage': percentage,
                'id': champion_id,
                'patch': patch
            })
    
    # Convert to DataFrame
    df = pd.DataFrame(all_champions_data)
    return df

def main():
    c_url = GOLGG_BASE_URL + GOL_GG_PICKBAN_BY_PATCH_ENDPOINT + GOL_GG_SEASON_SPLIT_URL_GEN(14, Split.SUMMER)
    df = scrape_pick_ban_by_patch(c_url)
    print(df)
    df.to_csv(f"pick_ban_by_patch_s14Summer.csv", index=False)
    
if __name__ == "__main__":
    main()
