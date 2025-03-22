import enum
from turtle import title
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

GOLGG_BASE_URL = "https://gol.gg/"
GOLGG_TOURNAMENT_ENDPOINT = "tournament/list/"
GOLGG_TOURNAMENT_SERIES_ENDPOINT = "tournament/tournament-matchlist/"
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

def GOL_GG_GAME_ENDPOINT_GEN(game_code: int) -> str:
    return f"game/stats/{game_code}/page-game/"

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

def get_all_games_from_tournament(html_content: str) -> list[str]:
    soup = BeautifulSoup(html_content, 'html.parser')
    
    match_links = []

    # Find all 'a' tags within the table containing match information
    table = soup.find('table')
    if table:
        for a_tag in table.find_all('a', href=True):
            href = a_tag['href']
            if href.startswith('../game/stats/'):
                full_url = f"https://gol.gg{href[2:]}"
                match_links.append(full_url)
    else:
        print("Match table not found on the page.")

    return match_links
    
def collect_matches_from_game(html_content: str) -> list[str]:
    soup = BeautifulSoup(html_content, 'html.parser')

    #TODO: Find length of series by looking at game menu - return links to each match
    match_links = []

    for link in soup.select(".game-menu-button a.nav-link"):
        href = link.get('href')
        if href and 'page-game' in href:
            match_links.append(f"{GOLGG_BASE_URL}{href[3:]}")
    return match_links

def scrape_teams_side_winner_from_game(html_content: str):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the winner/loser and the team that was blue/red
    blue_side_div = soup.find('div', class_='col-12 blue-line-header')
    if not blue_side_div:
        return None
    blue_side_team = blue_side_div.find('a').text.strip()

    red_side_div = soup.find('div', class_='col-12 red-line-header')
    if not red_side_div:
        return None
    red_side_team = red_side_div.find('a').text.strip()
    
    blue_side_lost = 'LOSS' in blue_side_div.text
    winner = red_side_team if blue_side_lost else blue_side_team

    return {
        "blue_side": blue_side_team,
        "red_side": red_side_team,
        "winner": winner,
        "loser": red_side_team if not blue_side_lost else blue_side_team
    }

def scrape_draft_from_game(html_content: str) -> pd.DataFrame:
    soup = BeautifulSoup(html_content, 'html.parser')

    section_divs = soup.find_all("div", class_="col-2")
    bans = []
    picks = []
    section_name = ["Bans", "Picks"]
    for div in section_divs:
        if div.text.strip() == section_name[0]:
            champions_div = div.find_next_sibling("div", class_="col-10")
            bans.extend(
                img["alt"] for img in champions_div.find_all("img", class_="champion_icon_medium")
            )
        elif div.text.strip() == section_name[1]:
            champions_div = div.find_next_sibling("div", class_="col-10")
            picks.extend(
                img["alt"] for img in champions_div.find_all("img", class_="champion_icon_medium")
            )

    # Clean data by organizing picks and bans by team
    blue_bans = bans[:len(bans)//2]
    red_bans = bans[len(bans)//2:]
    blue_picks = picks[:len(picks)//2]
    red_picks = picks[len(picks)//2:]
    
    return pd.DataFrame({"blue_bans": blue_bans, "red_bans": red_bans, "blue_picks": blue_picks, "red_picks": red_picks})

def collect_match_patch(html_content: str) -> str:
    soup = BeautifulSoup(html_content, 'html.parser')
    patch_div = soup.find('div', class_='col-3 text-right')
    if patch_div:
        return patch_div.text.strip()[1:]
    return None

def scrape_full_tournament(tourney_url_endpoint: str):
    upd_url = GOLGG_BASE_URL + GOLGG_TOURNAMENT_SERIES_ENDPOINT + tourney_url_endpoint
    try:
        response = requests.get(upd_url, headers=HEADERS)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []

    df = pd.DataFrame()
    
    ln = get_all_games_from_tournament(response.text)
    for link in ln:
        try:
            game_response = requests.get(link, headers=HEADERS)
            game_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            continue
        game_html = game_response.text
        series_games = collect_matches_from_game(game_html)
        new_data = scrape_draft_from_game(game_html)
        new_data["patch"] = collect_match_patch(game_html)
        df = pd.concat([df, new_data], ignore_index=True)

        for link_x in series_games:
            try:
                game_response = requests.get(link_x, headers=HEADERS)
                game_response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")
                continue
            game_html = game_response.text
            new_data = scrape_draft_from_game(game_html)
            new_data["patch"] = collect_match_patch(game_html)
            df = pd.concat([df, new_data], ignore_index=True)
    return df

def main():
    # c_url = GOLGG_BASE_URL + GOL_GG_PICKBAN_BY_PATCH_ENDPOINT + GOL_GG_SEASON_SPLIT_URL_GEN(12, Split.SPRING)
    # df = scrape_pick_ban_by_patch(c_url)
    # print(df)
    # df.to_csv(f"pick_ban_by_patch_s12Spring.csv", index=False)

    # tourney = "First Stand 2025/"
    # ff = get_all_games_from_tournament(tourney)

    game = GOLGG_BASE_URL + GOL_GG_GAME_ENDPOINT_GEN(64957)
    print(game)
    
    # with open("game.html", "w") as f:
    #     f.write(requests.get(game, headers=HEADERS).text)
    
    with open("game.html", "r") as f:
        html_content = f.read()
    
    # draft = scrape_draft_from_game(html_content)
    # print(draft)
    
    # teams = scrape_teams_side_winner_from_game(html_content)
    # print(teams)

    # patch = collect_match_patch(html_content)
    # print(patch)

    game_links = collect_matches_from_game(html_content, game)
    print(game_links)
    
if __name__ == "__main__":
    main()
