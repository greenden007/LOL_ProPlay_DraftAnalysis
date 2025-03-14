import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

GOLGG_BASE_URL = "https://gol.gg/"
GOLGG_TOURNAMENT_ENDPOINT = "tournament/list/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
}

def get_tourney_links_golgg():
    url = f"{GOLGG_BASE_URL}{GOLGG_TOURNAMENT_ENDPOINT}"
    response = requests.get(url, headers=HEADERS)
    if (response.status_code != 200):
        print("Failed")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    links = []

    

def get_match_draft_data_liquipedia(tourney_url):
    response = requests.get(tourney_url, headers=HEADERS)
    if response.status_code != 200:
        print("Failed")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    matches = []

    # TODO: Modify this based on Liquipedia structure, used temp vars
    for match in soup.select(".bracket-game"):
        teams = match.select(".team-name")
        bans = match.select(".bans")
        picks = match.select(".picks")

        if len(teams) == 2:
            match_data = {
                "Team 1": teams[0].text.strip(),
                "Team 2": teams[1].text.strip(),
                "Bans": [ban.text.strip() for ban in bans],
                "Picks": [pick.text.strip() for pick in picks],
            }
            matches.append(match_data)

    return matches


