from flask import Flask, jsonify
import mysql.connector
from flask_cors import CORS

# Create the Flask app — this sets up the web server
app = Flask(__name__)
CORS(app)  # This lets websites talk to your backend without browser security blocks

# Connect to your local MySQL database
db = mysql.connector.connect(
    host = "localhost", # means the database is on your computer
    port = 3307,
    user = "root",        # default username for MySQL
    password = "sports",  # the password you chose when setting up MySQL
    database ="sports_website"  # the database name we will create
)
cursor = db.cursor(dictionary=True)  # this lets us grab data and automatically turn it into dictionaries (key/value pairs)

@app.route('/')
def home():
    return "Your Flask backend is running! Try going to /teams or /players."

# When someone goes to /teams, this function runs:
@app.route('/teams')
def get_teams():
    cursor.execute("SELECT * FROM teams")  # grab all teams from the database
    teams = cursor.fetchall()  # get the result as a list
    return jsonify(teams)  # send the result as JSON (so your website can read it)

# When someone goes to /players, this function runs:
@app.route('/players')
def get_players():
    cursor.execute("SELECT * FROM players")
    players = cursor.fetchall()
    return jsonify(players)

@app.route('/teams/<int:team_id>/games')
def get_team_games(team_id):
    cursor.execute("""
        SELECT g.game_id, g.date, g.home_score, g.away_score,
               ht.name AS home_team, at.name AS away_team
        FROM games g
        JOIN teams ht ON g.home_team_id = ht.team_id
        JOIN teams at ON g.away_team_id = at.team_id
        WHERE g.home_team_id = %s OR g.away_team_id = %s
        ORDER BY g.date DESC
    """, (team_id, team_id))
    team_games = cursor.fetchall()
    return jsonify(team_games)

# Start the app when you run this file
if __name__ == '__main__':
    app.run(debug=True)
