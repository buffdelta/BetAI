from bs4 import BeautifulSoup
from bs4 import Comment
from ratelimit import limits, sleep_and_retry
import datetime
import pandas
import requests

TEAMS = ['BOS', 'NYK', 'TOR', 'BRK', 'PHI', # ATLANTIC DIVISION
         'CLE', 'IND', 'MIL', 'DET', 'CHI', # CENTRAL DIVISION
         'ATL', 'ORL', 'MIA', 'CHO', 'WAS', # SOUTHEAST DIVISION
         'OKC', 'DEN', 'MIN', 'POR', 'UTA', # NORTHWEST DIVISION
         'LAL', 'GSW', 'LAC', 'SAC', 'PHO', # PACIFIC DIVISION
         'HOU', 'MEM', 'DAL', 'SAS', 'NOP'] # SOUTHWEST DIVISION

class WebScraper:

    REQUEST_LIMIT = 20
    ONE_MINUTE=60

    @sleep_and_retry
    @limits(calls=REQUEST_LIMIT, period=ONE_MINUTE)
    def make_request(self, request_url):
        response = requests.get(request_url)
        if response.status_code != 200:
            raise Exception("Invalid Request.")
        print("Made successful request to: %s" % request_url)
        return response

    def get_game_data(self, date, home_team):
        if date <= datetime.datetime(2004, 11, 2): # We will only get games from Novemeber 2, 2004, because this is when the last NBA expansion happened.
            raise Exception('Date is not valid')

        request_url = 'https://www.basketball-reference.com/boxscores/%s0%s.html' % (date.strftime('%Y%m%d'), home_team)
        response = make_request(request_url)

        soup = get_soup(response.text)

        scores = soup.find('table', id='line_score').find_all('td', {'data-stat': 'T'})
        visit_team = soup.find('table', id='line_score').find_all('th', {'data-stat': 'team', 'scope':'row'})[0].text
        visit_score = [scores[0].text] # Visiting team score
        home_score = [scores[1].text]  # Home team score

        for th in soup.find_all('th'):
            th.decompose()

        data = {
            'match_date': date,
            'home_team': home_team,
            'visit_team': visit_team,
            'home_score': home_score,
            'visit_score': visit_score,
            'game_result': int(home_score > visit_score) # 1 = home team win, 0 = home team loss.
        }

        visit_stats = soup.find('table', id='four_factors').find('tbody').find_all('tr')[0].find_all('td')
        home_stats = soup.find('table', id='four_factors').find('tbody').find_all('tr')[1].find_all('td')

        for i in range(len(visit_stats)):
            if visit_stats[i]['data-stat'] == 'pace':
                data['pace'] = visit_stats[i].text
                continue
            data['visit_' + visit_stats[i]['data-stat']] = visit_stats[i].text
            data['home_' + home_stats[i]['data-stat']] = home_stats[i].text

        soup = BeautifulSoup(response.text, 'html.parser')
        visit_stats = soup.find('table', id='box-' + visit_team + '-game-basic').find('tfoot').find_all('td', string=lambda text: text and text.strip())
        home_stats = soup.find('table', id='box-' + home_team + '-game-basic').find('tfoot').find_all('td', string=lambda text: text and text.strip())

        for i in range(len(visit_stats)):
            data['visit_' + visit_stats[i]['data-stat']] = visit_stats[i].text
            data['home_' + visit_stats[i]['data-stat']] = home_stats[i].text

        return pandas.DataFrame(data)

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
        table = BeautifulSoup(text, 'html.parser').find_all('th', { 'class':'left', 'data-stat': 'date_game' })
        links = []
        months = list(BeautifulSoup(text, 'html.parser').find('div', { 'class':'filter'}).find_all('a'))
        for j in range(len(months)):
            months[j] = "https://www.basketball-reference.com" + months[j].get('href')
        return months;

    def get_all_game_links(self, text):
        tags = BeautifulSoup(text, 'html.parser').find_all('td', {'data-stat':'box_score_text'})
        return ["https://www.basketball-reference.com" + list(tag.children)[0].get('href') for tag in tags]

    def get_all_game_links_year(self, year):
        request_url = 'https://www.basketball-reference.com/leagues/NBA_%s_games.html' % (year)
        response = self.make_request(request_url)

        month_links = self.get_all_month_links(response.text)
        game_links = []
        for i in range(1, len(month_links)):
            game_links.append(self.get_all_game_links(response.text))
            response = self.make_request(month_links[i])

        game_links.append(self.get_all_game_links(response.text))
        return game_links
