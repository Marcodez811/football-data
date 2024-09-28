from crawler import MatchCrawler

if __name__ == "__main__":
    standings_url = "https://fbref.com/en/comps/12/2023-2024/2023-2024-La-Liga-Stats"
    seasons = tuple(range(2023, 2020, -1))
    # all_matches = []
    
    # for season in seasons:
    #     delay_seconds(5)
    #     data = requests.get(standings_url, headers=create_header())
    #     soup = BeautifulSoup(data.text, "html.parser")
    #     standings_table = soup.select('table.stats_table')[0]
    #     links = [l.get("href") for l in standings_table.find_all('a')]
    #     links = [l for l in links if l and '/squads/' in l]
    #     team_urls = [f"https://fbref.com{l}" for l in links]

    #     for team_url in team_urls:
    #         team_name = team_url.split("/")[-1].replace("-Stats", "").replace("-", " ")
    #         print(f"Working on {team_name}'s data...")
    #         team_df = obtain_team_df(team_url)
    #         team_df = team_df[team_df["Comp"]== "Premier League"]
    #         # the data does not contain which season it was
    #         team_df["Season"] = season
    #         # nor does it contain which team the data belongs to
    #         team_df["Team"] = team_name
    #         if team_df is not None:
    #             all_matches.append(team_df)
    #         print(f"Done with {team_name}'s data!")
            
    #     previous_season = soup.select("a.prev")[0].get("href")
    #     standings_url = f"https://fbref.com{previous_season}"

    crawler = MatchCrawler('La Liga',standings_url)
    match_df = crawler.scrape()
    match_df.columns = [c.lower() for c in match_df.columns]
    match_df.to_csv("la_liga_train.csv")
    print(match_df.head())