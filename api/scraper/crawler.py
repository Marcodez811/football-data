import requests
from bs4 import BeautifulSoup
import pandas as pd
from utils.helper import delay_seconds, create_header, parse_html

class MatchCrawler():
    BASE_URL = "https://fbref.com"

    def __init__(self, league_name, league_url: str):
        self.league_name = league_name
        self.league_url = league_url

    def crawl(self):
        """
        This function will crawl through the match data for the specified league
        and return the crawled data as a dataframe.

        Parameters
        ----------
        url : str
            The URL of the match data to be crawled.
        """
        data = requests.get(self.league_url, headers=create_header())
        soup = BeautifulSoup(data.text, "html.parser")
        standing_table = soup.select('table.stats_table')[0]
        if not standing_table:
            print("Can't find the table!")
            return None
        links = list(
                    filter(
                        lambda l: l and '/squads/' in l,
                        [l.get("href") for l in standing_table.find_all('a')]
                    ))
        team_urls = [self.BASE_URL + l for l in links]
        final_data = []
        for team_url in team_urls:
            team_name = team_url.split("/")[-1].replace("-Stats", "").replace("-", " ")
            print(f"Start to work on {team_name}'s data...")
            try:
                response = requests.get(team_url, headers=create_header())
                team_df = self.parse_team(response)
                if team_df is None:
                    print(f"Error in parsing {team_name}'s data!")
                    continue
                team_df = team_df[team_df["Comp"]== self.league_name]
                team_df["Team"] = team_name
                if team_df is not None:
                    print(f"Done with {team_name}'s data!")
                    final_data.append(team_df)
            except Exception as e:
                print(f"Error in {team_name}'s data: {e}")
        
        if not final_data:
            print("No data found!")
            return None
        matches_df = pd.concat(final_data)
        matches_df.columns = [c.lower() for c in matches_df.columns]
        return matches_df
             
    def parse_team(self, response):
        """
        This function will parse the individual team data, including the match
        data and shooting data, and merge them together.

        Parameters
        ----------
        response : requests.Response
            The response object from the request to the team URL.

        Returns
        -------
        pd.DataFrame
            The merged team data.
        """
        try:
            delay_seconds(5)
            match_df = pd.read_html(parse_html(response), match="Scores & Fixtures")[0]
        except (ValueError, IndexError) as e:
            print(f"Match data table not found in {response.url}! {e}")
            return None
        try:
            delay_seconds(5)
            shooting_data = pd.read_html(parse_html(response), match="Shooting")[0]
            soup = BeautifulSoup(response.text, "html.parser")
            links = [l.get("href") for l in soup.find_all('a')]
            links = [l for l in links if l and 'all_comps/shooting/' in l]
            shooting_urls = [f"https://fbref.com{l}" for l in links]
            if not shooting_urls:
                raise IndexError
            shooting_data = requests.get(shooting_urls[0], headers=create_header())
            if shooting_data is None:
                raise ValueError
            shooting_df = pd.read_html(parse_html(shooting_data), match="Shooting")[0]
            shooting_df.columns = shooting_df.columns.droplevel()
        except (ValueError, IndexError) as e:
            print(f"Shooting data table not found in {response.url}! {e}")
            return None
        # Merge the data
        merge_cols = ["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]
        try:
            team_data = match_df.merge(
                shooting_df[merge_cols],
                on="Date"
            )
            return team_data
        except ValueError as e:
            print(f"Error in merging data! {e}")
            return None
        
    def scrape(self):
        """
        Run the crawling process to scrape the match data.

        Returns
        -------
        pd.DataFrame
            The scraped match data.
        """
        return self.crawl()
