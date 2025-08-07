import argparse
import os

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import pandas

from database import Database
from logger import Logger
from predictor import Predictor

database = Database()
app = Flask(__name__, static_folder=os.path.join(os.getcwd(), 'server', 'public'))
CORS(app)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory(app.static_folder, os.path.join('assets', filename))

@app.route('/logos/<path:filename>')
def serve_logo(filename):
    return send_from_directory(app.static_folder, os.path.join('logos', filename))

@app.route('/teams')
def get_teams():
    year = request.args.get('year')
    try:
        team_folders = []
        with os.scandir(f'{database.DATABASE_PATH}/{year}') as it:
            for entry in it:
                if entry.name:
                    team_folders.append(entry.name)
        return jsonify(sorted(team_folders))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/predict')
def predict_game():
    visit_team = request.args.get('team1')
    home_team = request.args.get('team2')

    if not home_team or not visit_team:
        return jsonify({'error': 'Both team1 and team2 must be provided'}), 400
    if home_team == visit_team:
        return jsonify({'error': 'Please select two different teams'}), 400

    winner = predictor.predict_outcome(visit_team, home_team)

    return jsonify({
        'team1': visit_team,
        'team2': home_team,
        'predicted_winner': winner
    })

def main(level):
    logger = Logger('App')
    logger.setLevel(level)
    app.logger = logger
    database.build_database(2020)
    predictor = Predictor(database)
    app.run(host = '0.0.0.0', port = int(os.environ.get('PORT', 5000)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Logging Levels')
    parser.add_argument('--level', type=str, default='INFO', help='INFO or DEBUG')
    args = parser.parse_args()
    main(level = args.level)
