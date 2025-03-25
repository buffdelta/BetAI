from bs4 import BeautifulSoup
from bs4 import Comment
import requests

TEAMS = ['BOS', 'NYK', 'TOR', 'BRK', 'PHI', # ATLANTIC DIVISION
         'CLE', 'IND', 'MIL', 'DET', 'CHI', # CENTRAL DIVISION
         'ATL', 'ORL', 'MIA', 'CHO', 'WAS', # SOUTHEAST DIVISION
         'OKC', 'DEN', 'MIN', 'POR', 'UTA', # NORTHWEST DIVISION
         'LAL', 'GSW', 'LAC', 'SAC', 'PHO', # PACIFIC DIVISION
         'HOU', 'MEM', 'DAL', 'SAS', 'NOP'] # SOUTHWEST DIVISION

# This function gets the team stats of a team, which are represented in the array above, and currently only for the year 2024. It can later be transfered into a pandas dataframe to work on the AI portion.

def get_team_stats(team, year):
    if team not in TEAMS:
        raise Exception('%s is not a valid team.' % (team))

    request_url = 'https://www.basketball-reference.com/teams/%s/%s.html' % (team, year)
    response = requests.get(request_url)

    soup = BeautifulSoup(response.text, 'html.parser')
    comments = str(soup.find_all(string=lambda text: isinstance(text, Comment)))

    soup = BeautifulSoup(comments, 'html.parser')
    table_rows = soup.find('table', id='team_and_opponent').find_all('td')

    team_stats_keys = []
    team_stats_values = []
    for i in range(len(table_rows)):
        if table_rows[i]['data-stat'] not in team_stats_keys:
            team_stats_keys.append(table_rows[i]['data-stat'])
            team_stats_values.append(table_rows[i].text)
    return dict(zip(team_stats_keys, team_stats_values))

print(get_team_stats('BOS', '2025'))
