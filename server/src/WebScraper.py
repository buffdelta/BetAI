from datetime import datetime

from bs4 import BeautifulSoup
from Logger import Logger
from ratelimit import limits, sleep_and_retry
from tenacity import retry, stop_never, wait_fixed, retry_if_exception_type, RetryCallState

import pandas
import requests
import re

TEAMS = ['BOS', 'NYK', 'TOR', 'BRK', 'PHI', # ATLANTIC DIVISION
         'CLE', 'IND', 'MIL', 'DET', 'CHI', # CENTRAL DIVISION
         'ATL', 'ORL', 'MIA', 'CHO', 'WAS', # SOUTHEAST DIVISION
         'OKC', 'DEN', 'MIN', 'POR', 'UTA', # NORTHWEST DIVISION
         'LAL', 'GSW', 'LAC', 'SAC', 'PHO', # PACIFIC DIVISION
         'HOU', 'MEM', 'DAL', 'SAS', 'NOP'] # SOUTHWEST DIVISION

class WebScraper:

    def __init__(self):
        self.logger = Logger()

    def _before_sleep(self, retry_state: RetryCallState):
        self.logger.warning('WebScraper', f'Retrying due to: {retry_state.outcome.exception()}')

    @retry(
        stop=stop_never,
        wait=wait_fixed(3),
        retry=retry_if_exception_type((requests.exceptions.RequestException, requests.exceptions.ConnectionError)),
        before_sleep=lambda retry_state: WebScraper()._before_sleep(retry_state)
    )
    @sleep_and_retry
    @limits(calls=1, period=3.00)
    def make_request(self, request_url: str) -> str:
        response = requests.get(request_url, timeout=3.0)
        self.logger.info('WebScraper', f'Made successful request to: {request_url}')
        return response.text

    def get_game_data(self, request_url: str, visit_team: str, home_team: str) -> dict[str, str | float]:
        text = self.make_request(request_url)
        soup = BeautifulSoup(text, 'html.parser')

        data = {
            'match_date': datetime.strptime(request_url[47:55], '%Y%m%d'),
            'visit_team': visit_team,
            'home_team': home_team,
            # This needs to be different, as this checks the box-score, and a future game does not have a box series available.
            # Once a new season is back in swing, this can be revisited.
            'is_playoff': 1 if soup.find('span', { 'data-label':'All Games in Series'}) != None else 0
        }

        # This one as well.
        data['playoff_round'] = re.search(r'Game (\d)', soup.find('h1').text).group(1) if data['is_playoff'] == 1 else 0

        visit_stats = soup.find('table', id='box-' + visit_team + '-game-basic').find('tfoot').find_all('td', string=lambda text: text and text.strip())
        home_stats = soup.find('table', id='box-' + home_team + '-game-basic').find('tfoot').find_all('td', string=lambda text: text and text.strip())

        for i in range(len(visit_stats)):
            data['visit_' + visit_stats[i]['data-stat']] = visit_stats[i].text
            data['home_' + visit_stats[i]['data-stat']] = home_stats[i].text

        data['game_result'] = data['home_team'] if int(data['home_pts']) > int(data['visit_pts']) else data['visit_team']

        return data

    def get_all_month_links(self, text: str) -> list[str]:
        months = list(BeautifulSoup(text, 'html.parser').find('div', { 'class':'filter'}).find_all('a'))

        for j in range(len(months)):
            months[j] = "https://www.basketball-reference.com" + months[j].get('href')
        return months

    def get_all_game_links(self, text: str) -> list[(str, str, str, str)]:
        table_rows = BeautifulSoup(text, 'html.parser').find('tbody').find_all('tr')
        data = []

        for row in table_rows:
            if row.text == "Playoffs":
                continue
            team_names = row.find('td', {'data-stat':'visitor_team_name'}).get('csk')
            visit_team = team_names[0:3]
            home_team = team_names[13:16]
            match_date = row.find('th', {'data-stat': 'date_game'}).get('csk')[0:8]
            box_score = row.find('td', {'data-stat': 'box_score_text'}).find('a')
            match_link = None
            if box_score is not None:
                match_link = 'https://www.basketball-reference.com' + box_score.get('href')
            else:
                match_link = 'https://www.basketball-reference.com/boxscores/' + match_date + home_team + '0.html'

            data.append((match_link, match_date, visit_team, home_team))

        return data

    def get_all_game_links_year(self, year: int):
        request_url = f'https://www.basketball-reference.com/leagues/NBA_{year}_games.html'

        text = self.make_request(request_url)
        month_links = self.get_all_month_links(text)

        game_links = []
        game_links.append(self.get_all_game_links(text))
        for i in range(1, len(month_links)):
            text = self.make_request(month_links[i])
            game_links.append(self.get_all_game_links(text))

        return game_links

    def get_all_game_links_after(self, date, team):
        month_name = date.strftime('%B').lower()
        request_url = f'https://www.basketball-reference.com/leagues/NBA_{date.year}_games-{month_name}.html'

        text = self.make_request(request_url)
        
        games = list(BeautifulSoup(text, 'html.parser').find('tbody').find_all('tr'))
        
        for game in games:
            if game.find('th').get('csk') == date.strftime('%Y%m%d') + '0' + team:
                games = games[games.index(game) + 1:] 
                break
        
        game_links = []
        data = []
        for row in games:
            if row.text == "Playoffs":
                continue
            team_names = row.find('td', {'data-stat':'visitor_team_name'}).get('csk')
            visit_team = team_names[0:3]
            home_team = team_names[13:16]
            match_date = row.find('th', {'data-stat': 'date_game'}).get('csk')[0:8]
            box_score = row.find('td', {'data-stat': 'box_score_text'}).find('a')
            match_link = None
            if box_score is not None:
                match_link = 'https://www.basketball-reference.com' + box_score.get('href')
            else:
                match_link = 'https://www.basketball-reference.com/boxscores/' + match_date + home_team + '0.html'

            data.append((match_link, match_date, visit_team, home_team))

        game_links.append(data)

        months = list(BeautifulSoup(text, 'html.parser').find('div', { 'class':'filter'}).find_all('a'))
        
        month_index = 0
        for i in range(len(months)):
            if month_name in str(months[i]):
                month_index = i
                break

        for i in range(month_index + 1, len(months)):
            text = self.make_request('https://www.basketball-reference.com' + months[i].get('href'))
            game_links.append(self.get_all_game_links(text))

        return game_links
