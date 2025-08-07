import os
import shutil
import zipfile
import pandas
import datetime
import time

from datetime import datetime
from pathlib import Path

from webscraper import WebScraper
from logger import Logger

class Database:

    DATABASE_PATH = f'{os.getcwd()}/server/src/database'

    def __init__(self):
        self.logger = Logger('database')

    TEAMS = ['NJN', # Older brooklyn nets
             'NOH', # Older new orleans pelicans
             'CHA',
             'SEA', # Seattle SuperSonics
             'NOK',
             'BOS', 'NYK', 'TOR', 'BRK', 'PHI', # ATLANTIC DIVISION
             'CLE', 'IND', 'MIL', 'DET', 'CHI', # CENTRAL DIVISION
             'ATL', 'ORL', 'MIA', 'CHO', 'WAS', # SOUTHEAST DIVISION
             'OKC', 'DEN', 'MIN', 'POR', 'UTA', # NORTHWEST DIVISION
             'LAL', 'GSW', 'LAC', 'SAC', 'PHO', # PACIFIC DIVISION
             'HOU', 'MEM', 'DAL', 'SAS', 'NOP'] # SOUTHWEST DIVISION

    def _populate_game_queue(self):
        team_game_queue = {}
        for team in self.TEAMS:
            team_game_queue[team] = []
        return team_game_queue

    def _get_average_past_three(self, home_team: str, visit_team: str, home_team_queue: dict, visit_team_queue: dict, key: str):
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

    def _compute_extra_data(self, game_data: dict, team_game_queue: dict) -> dict:
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
            self.logger.info('Gathering extra information')
            for key in data:
                data[key] = self._get_average_past_three(game_data['home_team'], game_data['visit_team'], home_team_queue, visit_team_queue, key)
            if len(home_team_queue) == 3:
                home_team_queue.pop(0)
            if len(visit_team_queue) == 3:
                visit_team_queue.pop(0)

        return data

    def get_game(self, year: int, home_team: str, file_name: str) -> pandas.DataFrame:
        return pandas.read_csv(f'{self.DATABASE_PATH}/{year}/{home_team}/{file_name}')

    def get_all_games(self) -> pandas.DataFrame:
        games = []
        for year in os.listdir('{self.DATABASE_PATH}'):
            for home_team in os.listdir(f'{self.DATABASE_PATH}/{year}'):
                for game in os.listdir(f'{self.DATABASE_PATH}/{year}/{home_team}'):
                    games.append(pandas.read_csv(f'{self.DATABASE_PATH}/{year}/{home_team}/{game}'))
        return pandas.concat(games, ignore_index=True)

    def get_all_games_year(self, year: int) -> pandas.DataFrame:
        games = []
        base_path = f'{self.DATABASE_PATH}/{year}'

        for home_team in os.listdir(base_path):
            if home_team == 'future_games':
                continue
            team_path = os.path.join(base_path, home_team)
            if not os.path.isdir(team_path):
                continue
            entries = sorted(
                entry for entry in os.listdir(team_path)
                if os.path.isfile(os.path.join(team_path, entry))
            )
            for game in entries:
                games.append(pandas.read_csv(os.path.join(team_path, game)))

        return pandas.concat(games, ignore_index=True)

    def get_all_games_range(self, start_year: int, end_year: int) -> pandas.DataFrame:
        games = []
        for year in range(start_year, end_year + 1):
            for home_team in os.scandir(f'{self.DATABASE_PATH}/{year}'):
                for game in os.scandir(f'{self.DATABASE_PATH}/{year}/{home_team.name}'):
                    games.append(pandas.read_csv(f'{self.DATABASE_PATH}/{year}/{home_team.name}/{game.name}'))
        return pandas.concat(games, ignore_index=True)

    def get_future_game(self, visit_team: str, home_team: str) -> pandas.DataFrame:
        current_year = datetime.now().year
        dir_path = f'{self.DATABASE_PATH}/{current_year}/future_games/{home_team}/'
        files = sorted(os.listdir(dir_path))
        first_file = files[0] if files else None
        self.logger.debug(f'Getting data from future game: {dir_path}{first_file}')
        return pandas.read_csv(f'{dir_path}{first_file}')

    def get_all_team_games(self, team: str, year: str) -> list:
        all_files = []
        for root, _, files in os.walk(f'{self.DATABASE_PATH}/{year}'):
            for file in files:
                game_data = pandas.read_csv(os.path.join(root, file))
                if (game_data['home_team'].iloc[0] == team) or (game_data['visit_team'].iloc[0] == team):
                    all_files.append(game_data.iloc[0].to_dict())
        all_files = sorted(
            all_files,
            key=lambda game: datetime.fromisoformat(game['match_date'])
        )
        return all_files

    def _fill_database(self, game_links: list, year: str):
        current_date = datetime.today().date()
        team_game_queue = self._populate_game_queue()

        file_count = 0
        for _, _, files in os.walk(f'{self.DATABASE_PATH}/{year}'):
            file_count += len(files)

        if file_count > 0:
            for team in os.listdir(f'{self.DATABASE_PATH}/{year}'):
                games = self.get_all_team_games(team, year)
                team_game_queue[team].extend(games[-3:])

        webscraper = WebScraper()
        for month_links in game_links:
            for match_link, match_date, visit_team, home_team in month_links:
                os.makedirs(f'{self.DATABASE_PATH}/{year}/{home_team}', exist_ok=True)
                game_data = None
                file_path = ''

                if current_date > datetime.strptime(match_date, '%Y%m%d').date():
                    game_data = webscraper.get_game_data(match_link, visit_team, home_team)
                    computed_data = self._compute_extra_data(game_data, team_game_queue)
                    self.logger.debug(computed_data)
                    game_data.update(computed_data)

                    team_game_queue[home_team].append(game_data)
                    team_game_queue[visit_team].append(game_data)
                    file_path = f'{self.DATABASE_PATH}/{year}/{home_team}/{match_date}.csv'
                    game_data = pandas.DataFrame([game_data])
                    game_data.to_csv(file_path, index=False)
                    self.logger.info(f'Created {file_path}')
                else:
                    game_data = {
                        'match_date': match_date,
                        'visit_team': visit_team,
                        'home_team': home_team
                    }
                    os.makedirs(f'{self.DATABASE_PATH}/{year}/future_games/{home_team}', exist_ok=True)
                    file_path = f'{self.DATABASE_PATH}/{year}/future_games/{home_team}/{match_date}.csv'

                    computed_data = self._compute_extra_data(game_data, team_game_queue)
                    self.logger.debug(computed_data)
                    game_data.update(computed_data)

                    game_data = pandas.DataFrame([game_data])
                    game_data.to_csv(file_path, index=False)
                    self.logger.info(f'Created {file_path}')

            self.logger.info(f'Finished getting game data from year: {year}')

    def build_database(self, start_year: int, end_year=None):
        if end_year is None:
            end_year = datetime.today().date().year

        years = list(range(start_year, end_year + 1))
        webscraper = WebScraper()

        create_archive = False

        if os.path.isdir(self.DATABASE_PATH):
            most_recent_time = 0
            most_recent_file = None
            for year_directory in os.scandir(self.DATABASE_PATH):
                if int(year_directory.name) in years:
                    file_count = 0
                    most_recent_file = None
                    most_recent_time = 0
                    for root, dirs, files in os.walk(f'{self.DATABASE_PATH}/{year_directory.name}'):
                        file_count += len(files)
                        for file in files:
                            filepath = os.path.join(root, file)
                            mod_time = os.stat(filepath).st_mtime_ns
                            if mod_time > most_recent_time:
                                most_recent_file = Path(filepath)
                                most_recent_time = mod_time
                    if file_count == 0:
                        continue
                    if file_count <= 1230 and int(year_directory.name) != 2020 and int(year_directory.name) != 2021:
                        team = most_recent_file.parent.name
                        date = datetime.strptime(most_recent_file.name[0:-4], "%Y%m%d").date()
                        game_links = webscraper.get_all_game_links_after(date, team, year_directory.name)
                        self._fill_database(game_links, int(year_directory.name))
                        create_archive = True
                    years.remove(int(year_directory.name))

        for year in years:
            self.logger.info(f'No data found for {year}, building new dataset')
            game_links = webscraper.get_all_game_links_year(year)
            team_game_queue = self._populate_game_queue()
            self._fill_database(game_links, year)
            create_archive = True

        if create_archive:
            self.logger.info(f'Creating {DATAHASE_PATH}/server/src/database.zip')
            shutil.make_archive(DATABASE_PATH, 'zip', self.DATABASE_PATH)

        if os.path.exists(f'{self.DATABASE_PATH}/database.zip'):
            self.logger.info('Database zip exists unzipping archive')
            with zipfile.ZipFile(f'{self.DATABASE_PATH}/database.zip', 'r') as zip_ref:
                os.makedirs(self.DATABASE_PATH)
                zip_ref.extractall(self.DATABASE_PATH)
                return
