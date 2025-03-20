from bs4 import BeautifulSoup
import requests

TEAMS = ['buf', 'mia', 'nyj', 'nwe', # AFC EAST
         'htx', 'clt', 'jax', 'oti', # AFC SOUTH
         'rav', 'pit', 'cin', 'cle', # AFC NORTH
         'kan', 'sdg', 'den', 'rai', # AFC WEST
         'phi', 'was', 'dal', 'nyg', # NFC EAST
         'tam', 'atl', 'car', 'nor', # NFC SOUTH
         'det', 'min', 'gnb', 'chi', # NFC NORTH
         'ram', 'sea', 'crd', 'sfo'] # NFC WEST

# This function gets the team stats of a team, which are represented in the array above, and currently only for the year 2024. It can later be transfered into a pandas dataframe to work on the AI portion.

def get_team_stats(team, year):
    if team not in TEAMS:
        raise Exception('%s is not a valid team.' % (team))
    if year != '2024':
        raise Exception('%s is not a valid year.' % (year))

    request_url = 'https://www.pro-football-reference.com/teams/%s/%s.htm' % (team, year)
    response = requests.get(request_url)
    table_rows = BeautifulSoup(response.text, 'html.parser').find('table', {'id':'team_stats'}).find_all('td')

    team_stats_keys = []
    team_stats_values = []
    for i in range(len(table_rows)):
        if table_rows[i]['data-stat'] not in team_stats_keys:
            team_stats_keys.append(table_rows[i]['data-stat'])
            team_stats_values.append(table_rows[i].text)
    return dict(zip(team_stats_keys, team_stats_values)))

get_team_stats('buf', '2024')
