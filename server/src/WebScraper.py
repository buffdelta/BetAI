from bs4 import BeautifulSoup
from bs4 import Comment
from Logger import Logger
from ratelimit import limits, sleep_and_retry
import pandas
import requests

TEAMS = ['BOS', 'NYK', 'TOR', 'BRK', 'PHI', # ATLANTIC DIVISION
         'CLE', 'IND', 'MIL', 'DET', 'CHI', # CENTRAL DIVISION
         'ATL', 'ORL', 'MIA', 'CHO', 'WAS', # SOUTHEAST DIVISION
         'OKC', 'DEN', 'MIN', 'POR', 'UTA', # NORTHWEST DIVISION
         'LAL', 'GSW', 'LAC', 'SAC', 'PHO', # PACIFIC DIVISION
         'HOU', 'MEM', 'DAL', 'SAS', 'NOP'] # SOUTHWEST DIVISION

class WebScraper:

    def __init__(self):
        self.logger = Logger()

    @sleep_and_retry
    @limits(calls=1, period=3.00)
    def make_request(self, request_url):
        response = requests.get(request_url)
        if (response.status_code == 104):
            response = request.get(request_url)
            self.logger.warning("WebScraper", "Made unsuccessful request to: %s" % (request_url))
        self.logger.info("WebScraper", "Made successful request to: %s" % (request_url))
        return response.text

    def get_game_data(self, request_url, visit_team, home_team):
        text = self.make_request(request_url)
        soup = BeautifulSoup(text, 'html.parser')

        data = {
            'match_date': request_url[47:56],
            'visit_team': visit_team,
            'home_team': home_team
        }

        visit_stats = soup.find('table', id='box-' + visit_team + '-game-basic').find('tfoot').find_all('td', string=lambda text: text and text.strip())
        home_stats = soup.find('table', id='box-' + home_team + '-game-basic').find('tfoot').find_all('td', string=lambda text: text and text.strip())

        for i in range(len(visit_stats)):
            data['visit_' + visit_stats[i]['data-stat']] = visit_stats[i].text
            data['home_' + visit_stats[i]['data-stat']] = home_stats[i].text

        data['game_result'] = data['home_team'] if int(data['home_pts']) > int(data['visit_pts']) else data['visit_team']

        return data

    def get_team_stats(self, team, year):
        if team not in TEAMS:
            raise Exception('%s is not a valid team.' % (team))
        if int(year) < 2004:
            raise Exception('%s is not a valid year.' % (year))

        request_url = 'https://www.basketball-reference.com/teams/%s/%s.html' % (team, year)
        response = self.make_request(request_url)
        soup = self.get_soup(response.text)
        table_rows = soup.find('table', id='team_and_opponent').find_all('td')

        team_stats_keys = []
        team_stats_values = []
        for i in range(len(table_rows)):
            if table_rows[i]['data-stat'] not in team_stats_keys:
                team_stats_keys.append(table_rows[i]['data-stat'])
                team_stats_values.append([table_rows[i].text])

        return pandas.DataFrame(dict(zip(team_stats_keys, team_stats_values)))

    def get_soup(self, text):
        soup = BeautifulSoup(text, 'html.parser')
        comments = str(soup.find_all(string=lambda text: isinstance(text, Comment))) # Tables are stored in comments on basketball-reference.
        return BeautifulSoup(comments, 'html.parser')

    def get_all_month_links(self, text):
        months = list(BeautifulSoup(text, 'html.parser').find('div', { 'class':'filter'}).find_all('a'))

        for j in range(len(months)):
            months[j] = "https://www.basketball-reference.com" + months[j].get('href')
        return months;

    def get_all_game_links(self, text):
        table_rows = BeautifulSoup(text, 'html.parser').find('tbody').find_all('tr')
        data = []

        for row in table_rows:
            if (row.text == "Playoffs"):
                continue
            date = row.find('th', {'data-stat': 'date_game'}).get('csk')[0:8]
            link = 'https://www.basketball-reference.com' + row.find('td', {'data-stat': 'box_score_text'}).find('a').get('href')
            team_names = row.find('td', {'data-stat':'visitor_team_name'}).get('csk')
            visit_team = team_names[0:3]
            home_team = team_names[13:16]
            data.append((link, date, visit_team, home_team))

        return data

    def get_all_game_links_year(self, year):
        request_url = 'https://www.basketball-reference.com/leagues/NBA_%s_games.html' % (year)

        text = self.make_request(request_url)
        month_links = self.get_all_month_links(text)

        game_links = []
        game_links.append(self.get_all_game_links(text))
        for i in range(1, len(month_links)):
            text = self.make_request(month_links[i])
            game_links.append(self.get_all_game_links(text))

        return game_links
