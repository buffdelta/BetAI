from WebScraper import WebScraper

import os
import pandas
import queue
import rich

from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.console import Group

class Database:

    TEAMS = ['NJN', # Older brooklyn nets
             'NOH', # Older new orleans pelicans
             'CHA', # Older new orleans pelicans
             'SEA', # Seattle SuperSonics
             'BOS', 'NYK', 'TOR', 'BRK', 'PHI', # ATLANTIC DIVISION
             'CLE', 'IND', 'MIL', 'DET', 'CHI', # CENTRAL DIVISION
             'ATL', 'ORL', 'MIA', 'CHO', 'WAS', # SOUTHEAST DIVISION
             'OKC', 'DEN', 'MIN', 'POR', 'UTA', # NORTHWEST DIVISION
             'LAL', 'GSW', 'LAC', 'SAC', 'PHO', # PACIFIC DIVISION
             'HOU', 'MEM', 'DAL', 'SAS', 'NOP'] # SOUTHWEST DIVISION

    def populate_game_queue(self):
        team_game_queue = {}
        for team in self.TEAMS:
            team_game_queue[team] = queue.Queue()
        return team_game_queue

    def get_average_past_three(self, home_team_queue, visit_team_queue, game_data, key):
        if 'home' in key:
            queue = home_team_queue
        else:
            queue = visit_team_queue

        num_games = min(queue.qsize(), 3)
        if num_games < 3 and (key == 'home_number_of_wins_past_three' or key == 'visit_number_of_wins_past_three'):
            return None

        games = list(queue.queue)
        total = 0
        count = 0

        for i in range(num_games):
                last_underscore = key.rfind('_')
                total += round(int(games[i][key[0:last_underscore]]), 3)
                count += 1

        if num_games > 3:
            queue.get()

        return total / count if count > 0 else 0

    def compute_extra_data(self, game_data, team_game_queue):
        home_team_queue = team_game_queue[game_data['home_team']]
        visit_team_queue = team_game_queue[game_data['visit_team']]
        data = {
          'home_ast_avg3': 0,
          'home_fg3_avg3': 0,
          'home_fg3a_avg3': 0,
          'home_fg_avg3': 0,
          'home_fga_avg3': 0,
          'home_ft_avg3': 0,
          'home_fta_avg3': 0,
          'home_pf_avg3': 0,
          'home_stl_avg3': 0,
          'home_tov_avg3': 0,
          'home_trb_avg3': 0,
          'visit_ast_avg3': 0,
          'visit_fg3_avg3': 0,
          'visit_fg3a_avg3': 0,
          'visit_fg_avg3': 0,
          'visit_fga_avg3': 0,
          'visit_ft_avg3': 0,
          'visit_fta_avg3': 0,
          'visit_pf_avg3': 0,
          'visit_stl_avg3': 0,
          'visit_tov_avg3': 0,
          'visit_trb_avg3': 0,
          'home_number_of_wins_past_three': 0,
          'visit_number_of_wins_past_three': 0,
        }
        if home_team_queue.qsize() > 0 and visit_team_queue.qsize() > 0:
           print('Getting extra information')
           for key in data:
               data[key] = self.get_average_past_three(home_team_queue, visit_team_queue, game_data, key)

        return data

    progress = Progress(
        TextColumn("📦 {task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    )
    task = progress.add_task("Processing items", total=1230)

    status_message = Panel("Gathering Month Links")

    def render(self):
        return Group(self.status_message, self.progress)


    def build_database(self):
        # Make sure database is not populated
        webscraper = WebScraper(self.status_message)
        game_links = []
        
        with Live(self.render(), refresh_per_second=1) as live:
            for i in range(2005, 2006):
                game_links = webscraper.get_all_game_links_year(i)
                self.progress.update(self.task, advance=len(game_links))
                team_game_queue = self.populate_game_queue()
                for j in range(len(game_links)):
                    month_links = game_links[j]
                    for link, date, visit_team, home_team in month_links:
                        os.makedirs('database/%s/%s' % (i, home_team), exist_ok=True)

                        game_data = webscraper.get_game_data(link, visit_team, home_team)

                        game_data.update(self.compute_extra_data(game_data, team_game_queue))
                        team_game_queue[home_team].put(game_data)

                        file_path = ('database/%s/%s/%s.csv' % (str(i), home_team, date))
                        game_data = pandas.DataFrame([game_data])
                        game_data.to_csv(file_path, index=False)
                        self.progress.update(self.task, advance=1)
