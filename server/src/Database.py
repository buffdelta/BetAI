from WebScraper import WebScraper

import os

class Database:

    def build_database(self):
        # Make sure database is not populated
        webscraper = WebScraper()
        game_links = []

        for i in range(2005, 2006):
            game_links = webscraper.get_all_game_links_year(i)
            for j in range(len(game_links)):
                month_links = game_links[j]
                for link, date, visit_team, home_team in month_links:
                    os.makedirs('database/%s/%s' % (i, home_team), exist_ok=True)
                    game_data = webscraper.get_game_data(link, visit_team, home_team)
                    file_path = ('database/%s/%s/%s.csv' % (str(i), home_team, date))
                    game_data.to_csv(file_path, index=False)
