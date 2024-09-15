import requests
from bs4 import BeautifulSoup
import pandas as pd
from utils.helper import delay_seconds, create_header, parse_html

def obtain_match_df(team_url: str):
    """
    Obtain the dataframe of the team's matching data
    """
    delay_seconds(5)
    match_data = requests.get(team_url, headers=create_header())
    if match_data is None:
        return None
    match_df = pd.read_html(parse_html(match_data), match="Scores & Fixtures")[0]
    return match_df

def obtain_shooting_df(team_url: str):
    """
    Obtain the dataframe of the team's shooting data
    """
    delay_seconds(5)
    soup = BeautifulSoup(requests.get(team_url, headers=create_header()).text, "html.parser")
    links = [l.get("href") for l in soup.find_all('a')]
    links = [l for l in links if l and 'all_comps/shooting/' in l]
    
    shooting_urls = [f"https://fbref.com{l}" for l in links]
    if not shooting_urls:
        print("Can't find the shooting table!")
        return None
    
    shooting_url = shooting_urls[0]
    delay_seconds(5)
    shooting_data = requests.get(shooting_url, headers=create_header())
    if shooting_data is None:
        print("The request to obtain the shooting data failed!")
        return None
    
    shooting_df = pd.read_html(parse_html(shooting_data), match="Shooting")[0]
    shooting_df.columns = shooting_df.columns.droplevel()
    return shooting_df

def obtain_team_df(team_url: str):
    """
    Obtain the dataframe of the team's data
    """
    match_df = obtain_match_df(team_url)
    shooting_df = obtain_shooting_df(team_url)
    
    if match_df is None or shooting_df is None:
        return None
    
    # join the match_df with the shooting_df based on the 'Date' column
    try:
        team_df = match_df.merge(
                    shooting_df[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]], 
                    on="Date")
        return team_df
    except ValueError:
        return None
    

if __name__ == "__main__":
    standings_url = "https://fbref.com/en/comps/9/Premier-League-Stats"
    seasons = tuple(range(2024, 2020, -1))
    all_matches = []
    
    for season in seasons:
        delay_seconds(5)
        data = requests.get(standings_url, headers=create_header())
        soup = BeautifulSoup(data.text, "html.parser")
        standings_table = soup.select('table.stats_table')[0]
        links = [l.get("href") for l in standings_table.find_all('a')]
        links = [l for l in links if l and '/squads/' in l]
        team_urls = [f"https://fbref.com{l}" for l in links]

        for team_url in team_urls:
            team_name = team_url.split("/")[-1].replace("-Stats", "").replace("-", " ")
            print(f"Working on {team_name}'s data...")
            team_df = obtain_team_df(team_url)
            team_df = team_df[team_df["Comp"]== "Premier League"]
            # the data does not contain which season it was
            team_df["Season"] = season
            # nor does it contain which team the data belongs to
            team_df["Team"] = team_name
            if team_df is not None:
                all_matches.append(team_df)
            print(f"Done with {team_name}'s data!")
            
        previous_season = soup.select("a.prev")[0].get("href")
        standings_url = f"https://fbref.com{previous_season}"

    match_df = pd.concat(all_matches)
    match_df.columns = [c.lower() for c in match_df.columns]
    match_df.to_csv("matches.csv")
    print(match_df.head())