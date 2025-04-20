from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

import pandas
from Database import Database

class Predictor:

    def predict_outcome(self):
        database = Database()
        database.build_database()
        df = database.get_all_games()
        X = df.drop(columns=['game_result', 'home_team', 'visit_team', 'match_date', 'visit_mp', 'home_mp', 'visit_fg', 'home_fg', 'visit_fga', 'home_fga', 'home_pf', 'visit_pf', 'visit_fg3', 'home_fg3', 'visit_fg3a', 'home_fg3a', 'visit_fg_pct', 'home_fg_pct', 'visit_fg3_pct', 'home_fg3_pct', 'visit_ft', 'home_ft', 'visit_fta', 'home_fta', 'visit_ft_pct', 'home_ft_pct', 'visit_orb', 'home_orb', 'visit_drb', 'home_drb', 'visit_trb', 'home_trb', 'visit_ast', 'home_ast', 'visit_stl', 'home_stl', 'visit_blk', 'home_blk', 'visit_tov', 'home_tov', 'visit_pts', 'home_pts'])
        y = (df['game_result'] == df['home_team']).astype(int)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        print("Accuracy:", accuracy_score(y_test, y_pred))
        print(classification_report(y_test, y_pred))
        X = pandas.DataFrame([df.iloc[0]])
        X = X.drop(columns=['game_result', 'home_team', 'visit_team', 'match_date', 'visit_mp', 'home_mp', 'visit_fg', 'home_fg', 'visit_fga', 'home_fga', 'home_pf', 'visit_pf', 'visit_fg3', 'home_fg3', 'visit_fg3a', 'home_fg3a', 'visit_fg_pct', 'home_fg_pct', 'visit_fg3_pct', 'home_fg3_pct', 'visit_ft', 'home_ft', 'visit_fta', 'home_fta', 'visit_ft_pct', 'home_ft_pct', 'visit_orb', 'home_orb', 'visit_drb', 'home_drb', 'visit_trb', 'home_trb', 'visit_ast', 'home_ast', 'visit_stl', 'home_stl', 'visit_blk', 'home_blk', 'visit_tov', 'home_tov', 'visit_pts', 'home_pts'])
        print(model.predict(X))

