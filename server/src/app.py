from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from Database import Database
from Logger import Logger
from Predictor import Predictor
import argparse
import os
import pandas as pd


# app = Flask(__name__, static_folder = 'static')
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
app = Flask(__name__, static_folder = STATIC_DIR)
CORS(app)

import os
# Folder where CSV game files are stored
DATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'server', 'src', 'database')
)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

# ✅ List all available teams from latest year folder
@app.route('/teams')
def get_teams():
    try:
        years = sorted(os.listdir(DATA_PATH), reverse=True)
        latest_year = years[0]
        team_folders = os.listdir(os.path.join(DATA_PATH, latest_year))
        return jsonify(sorted(team_folders))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ✅ Predict winner between two teams
@app.route('/predict')
def predict_game():
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')

    if not team1 or not team2:
        return jsonify({'error': 'Both team1 and team2 must be provided'}), 400
    if team1 == team2:
        return jsonify({'error': 'Please select two different teams'}), 400

    def get_avg_points(team_code):
        points = []
        for year in os.listdir(DATA_PATH):
            team_path = os.path.join(DATA_PATH, year, team_code)
            if os.path.exists(team_path):
                for file in os.listdir(team_path):
                    if file.endswith(".csv"):
                        df = pd.read_csv(os.path.join(team_path, file))
                        if not df.empty:
                            game = df.iloc[0]
                            if game['home_team'] == team_code:
                                points.append(int(game['home_pts']))
                            elif game['visit_team'] == team_code:
                                points.append(int(game['visit_pts']))
        return sum(points) / len(points) if points else 0

    team1_avg = get_avg_points(team1)
    team2_avg = get_avg_points(team2)
    winner = team1 if team1_avg > team2_avg else team2

    return jsonify({
        "team1": team1,
        "team2": team2,
        "team1_avg_pts": round(team1_avg, 1),
        "team2_avg_pts": round(team2_avg, 1),
        "predicted_winner": winner
    })

def main(level):
    logger = Logger(level)
    database = Database()
    database.build_database()
    predictor = Predictor()
    predictor.predict_outcome()
    logger.info('App', 'Starting flask server with host: 0.0.0.0, Port: 5000')
    app.run(host = '0.0.0.0', port = int(os.environ.get('PORT', 5000)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Logging Levels")
    parser.add_argument("--level", type=str, default='INFO', help='INFO or DEBUG')
    args = parser.parse_args()
    main(level = args.level)
