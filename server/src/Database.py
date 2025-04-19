from WebScraper import WebScraper
from Logger import Logger

import os
import pandas
from queue import LifoQueue
import shutil
import zipfile

class Database:

    def __init__(self):
        self.logger = Logger()

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

    STARTING_YEAR = 2005
    ENDING_YEAR = 2024
    END_YEAR = 2024

    def populate_game_queue(self):
        team_game_queue = {}
        for team in self.TEAMS:
            team_game_queue[team] = []
        return team_game_queue

    def get_average_past_three(self, home_team, visit_team, home_team_queue, visit_team_queue, game_data, key):
        if 'home' in key:
            queue = home_team_queue
            team = home_team
        else:
            queue = visit_team_queue
            team = visit_team

        num_games = min(len(queue), 3)
        games = queue

        total = 0.0
        count = 0.0

        if key == 'home_number_of_wins_past_three' or key == 'visit_number_of_wins_past_three':
            for i in range(num_games):
                if games[i]['game_result'] == team:
                    total += 1.0
            return total

        parts = key.split('_')
        for i in range(num_games):
            if team == games[i]['home_team']:
                total += float(games[i]['home_' + parts[1]])
            else:
                total += float(games[i]['visit_' + parts[1]])
            count += 1

        return round(total / count, 5) if count > 0 else 0

    def compute_extra_data(self, game_data, team_game_queue):
        home_team_queue = team_game_queue[game_data['home_team']]
        visit_team_queue = team_game_queue[game_data['visit_team']]
        data = {
          'visit_fg_avg3': 0,
          'home_fg_avg3': 0,
          'visit_fga_avg3': 0,
          'home_fga_avg3': 0,
          'visit_fg3_avg3': 0,
          'home_fg3_avg3': 0,
          'visit_fg3a_avg3': 0,
          'home_fg3a_avg3': 0,
          'visit_ft_avg3': 0,
          'home_ft_avg3': 0,
          'visit_fta_avg3': 0,
          'home_fta_avg3': 0,
          'visit_ast_avg3': 0,
          'home_ast_avg3': 0,
          'visit_stl_avg3': 0,
          'home_stl_avg3': 0,
          'visit_tov_avg3': 0,
          'home_tov_avg3': 0,
          'visit_pf_avg3': 0,
          'home_pf_avg3': 0,
          'visit_trb_avg3': 0,
          'home_trb_avg3': 0,
          'visit_number_of_wins_past_three': 0,
          'home_number_of_wins_past_three': 0
        }

        if len(home_team_queue) > 0 or len(visit_team_queue) > 0:
           self.logger.info("Database", "Gathering extra information")
           for key in data:
               data[key] = self.get_average_past_three(game_data['home_team'], game_data['visit_team'], home_team_queue, visit_team_queue, game_data, key)
           if len(home_team_queue) == 3:
               home_team_queue.pop(0)
           if len(visit_team_queue) == 3:
               visit_team_queue.pop(0)

        return data

    def build_database(self):

        webscraper = WebScraper()
        cwd = os.getcwd()

        if os.path.isdir(f'{cwd}/server/src/database'):
            self.logger.info('Database', 'Database folder already exists')
            return

        if os.path.exists(f'{cwd}/server/src/database.zip'):
            self.logger.info('Database', 'Database zip exists unzipping archive')
            with zipfile.ZipFile(f'{cwd}/server/src/database.zip', 'r') as zip_ref:
                zip_ref.extractall(f'{cwd}/server/src/database')
                return

        self.logger.info('Database', 'No data found, building new dataset')
        for i in range(self.STARTING_YEAR, 2006):
            game_links = webscraper.get_all_game_links_year(i)
            team_game_queue = self.populate_game_queue()
            for j in range(len(game_links)):
                month_links = game_links[j]
                for link, date, visit_team, home_team in month_links:
                    os.makedirs(f'{cwd}/server/src/database/{i}/{home_team}', exist_ok=True)

                    game_data = webscraper.get_game_data(link, visit_team, home_team)

                    computed_data = self.compute_extra_data(game_data, team_game_queue)
                    self.logger.debug('Database', computed_data)
                    team_game_queue[home_team].append(game_data)
                    team_game_queue[visit_team].append(game_data)
                    game_data.update(computed_data)

                    file_path = f'{cwd}/server/src/database/{i}/{home_team}/{date}.csv'
                    game_data = pandas.DataFrame([game_data])
                    self.logger.info('Database', f'Created {file_path}')
                    game_data.to_csv(file_path, index=False)

            self.logger.info('Database', f'Finished getting game data from year: {i}')

        self.logger.info('Database', f'Creating {cwd}/server/src/database.zip')
        shutil.make_archive(f'{cwd}/server/src/database', 'zip', f'{cwd}/server/src/database')
