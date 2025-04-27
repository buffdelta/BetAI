import os
import shutil
import zipfile
import pandas
from datetime import datetime

from WebScraper import WebScraper
from Logger import Logger

class Database:

    def __init__(self):
        self.logger = Logger()
        self._build_database()

    TEAMS = ['NJN', # Older brooklyn nets
             'NOH', # Older new orleans pelicans
             'CHA', # Older new orleans pelicans
             'SEA', # Seattle SuperSonics
             'NOK',
             'BOS', 'NYK', 'TOR', 'BRK', 'PHI', # ATLANTIC DIVISION
             'CLE', 'IND', 'MIL', 'DET', 'CHI', # CENTRAL DIVISION
             'ATL', 'ORL', 'MIA', 'CHO', 'WAS', # SOUTHEAST DIVISION
             'OKC', 'DEN', 'MIN', 'POR', 'UTA', # NORTHWEST DIVISION
             'LAL', 'GSW', 'LAC', 'SAC', 'PHO', # PACIFIC DIVISION
             'HOU', 'MEM', 'DAL', 'SAS', 'NOP'] # SOUTHWEST DIVISION

    STARTING_YEAR = 2005
    ENDING_YEAR = 2024

    def _populate_game_queue(self):
        team_game_queue = {}
        for team in self.TEAMS:
            team_game_queue[team] = []
        return team_game_queue

    def _get_average_past_three(self, home_team, visit_team, home_team_queue, visit_team_queue, key):
        if 'home' in key:
            queue = home_team_queue
            team = home_team
        else:
            queue = visit_team_queue
            team = visit_team

        total = 0.0
        count = 0.0

        num_games = min(len(queue), 3)
        games = queue

        if key == 'home_number_of_wins_past_three' or key == 'visit_number_of_wins_past_three':
            for i in range(num_games):
                if games[i]['game_result'] == team:
                    total += 1.0
            return total

        if key == 'home_previous_game_result' or key == 'visit_previous_game_result':
            if num_games >= 1:
                if games[-1]['game_result'] == team:
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

    def _compute_extra_data(self, game_data, team_game_queue):
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
          'home_number_of_wins_past_three': 0,
          'visit_previous_game_result': 0,
          'home_previous_game_result': 0
        }

        if len(home_team_queue) > 0 or len(visit_team_queue) > 0:
            self.logger.info("Database", "Gathering extra information")
            for key in data:
                data[key] = self._get_average_past_three(game_data['home_team'], game_data['visit_team'], home_team_queue, visit_team_queue, key)
            if len(home_team_queue) == 3:
                home_team_queue.pop(0)
            if len(visit_team_queue) == 3:
                visit_team_queue.pop(0)

        return data

    def get_all_games(self) -> pandas.DataFrame:
        games = []
        for year in os.listdir('database/'):
            for home_team in os.listdir(f'database/{year}'):
                for game in os.listdir(f'database/{year}/{home_team}'):
                    games.append(pandas.read_csv(f'database/{year}/{home_team}/{game}'))
        return pandas.concat(games, ignore_index=True)

    def get_all_games_year(self, year: int) -> pandas.DataFrame:
        games = []
        for home_team in os.listdir(f'database/{year}'):
            entries = sorted(
                entry for entry in os.listdir(f'database/{year}/{home_team}')
                if entry not in f'database/{year}/'
            )
        for game in entries:
                games.append(pandas.read_csv(f'database/{year}/{home_team}/{game}'))
        return pandas.concat(games, ignore_index=True)

    def get_all_games_range(self, start_year: int, end_year: int) -> pandas.DataFrame:
        games = []
        for i in range(start_year, end_year + 1):
            for home_team in os.listdir(f'database/{i}'):
                for game in os.listdir(f'database/{i}/{home_team}'):
                    games.append(pandas.read_csv(f'database/{i}/{home_team}/{game}'))
        return pandas.concat(games, ignore_index=True)

    def get_future_game(self, visit_team, home_team):
        current_year = datetime.now().year
        dir_path = f'{os.getcwd()}/database/{current_year}/future_games/{home_team}/'
        files = sorted(os.listdir(dir_path))
        first_file = files[0] if files else None
        return pandas.read_csv(f'{dir_path}{first_file}')

    def _build_database(self):

        webscraper = WebScraper()
        cwd = os.getcwd()
        current_date = datetime.today()

        if os.path.isdir(f'{cwd}/database'):
            self.logger.info('Database', 'Database folder already exists')
            return

        if os.path.exists(f'{cwd}/database.zip'):
            self.logger.info('Database', 'Database zip exists unzipping archive')
            with zipfile.ZipFile(f'{cwd}/database.zip', 'r') as zip_ref:
                zip_ref.extractall(f'{cwd}/database')
                return

        self.logger.info('Database', 'No data found, building new dataset')
        for i in range(2025, 2026):
            game_links = webscraper.get_all_game_links_year(i)
            team_game_queue = self._populate_game_queue()
            for j in range(6, len(game_links)):
                month_links = game_links[j]
                for match_link, match_date, visit_team, home_team in month_links:
                    os.makedirs(f'{cwd}/database/{i}/{home_team}', exist_ok=True)
                    game_data = None
                    file_path = ''

                    if current_date > datetime.strptime(match_date, '%Y%m%d').date():
                        game_data = webscraper.get_game_data(match_link, visit_team, home_team)
                        team_game_queue[home_team].append(game_data)
                        team_game_queue[visit_team].append(game_data)
                        file_path = f'{cwd}/database/{i}/{home_team}/{match_date}.csv'
                    else:
                        game_data = {
                            'match_date': match_date,
                            'visit_team': visit_team,
                            'home_team': home_team
                        }
                        os.makedirs(f'{cwd}/database/{i}/future_games/{home_team}', exist_ok=True)
                        file_path = f'{cwd}/database/{i}/future_games/{home_team}/{match_date}.csv'

                    computed_data = self._compute_extra_data(game_data, team_game_queue)
                    self.logger.debug('Database', computed_data)
                    game_data.update(computed_data)

                    game_data = pandas.DataFrame([game_data])
                    game_data.to_csv(file_path, index=False)
                    self.logger.info('Database', f'Created {file_path}')

            self.logger.info('Database', f'Finished getting game data from year: {i}')

        self.logger.info('Database', f'Creating {cwd}/database.zip')
        shutil.make_archive(f'{cwd}/database', 'zip', f'{cwd}/database')
