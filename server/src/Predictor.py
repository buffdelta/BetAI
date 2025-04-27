import os
import joblib

from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

from Logger import Logger

class Predictor:

    def __init__(self, database):
        self.logger = Logger()
        self.database = database
        self.model = self._load_model()

    def _load_model(self):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'Predictor.pkl')
        return joblib.load(file_path)

    def predict_outcome(self, visit_team, home_team):
        df = self.database.get_future_game(visit_team, home_team)
        x = df.drop(columns=[
            'visit_team',
            'home_team',
            'match_date'
        ])
        y_pred = self.model.predict(x)
        return home_team if y_pred == 1 else visit_team

    def train_model(self) -> None:
        df = self.database.get_all_games_range(2020, 2023)
        x = df.drop(columns = [
            'game_result', 'home_team', 'visit_team',
            'match_date', 'visit_mp', 'home_mp',
            'visit_fg', 'home_fg', 'visit_fga',
            'home_fga', 'home_pf', 'visit_pf',
            'visit_fg3', 'home_fg3', 'visit_fg3a',
            'home_fg3a', 'visit_fg_pct', 'home_fg_pct',
            'visit_fg3_pct', 'home_fg3_pct', 'visit_ft',
            'home_ft', 'visit_fta', 'home_fta',
            'visit_ft_pct', 'home_ft_pct', 'visit_orb',
            'home_orb', 'visit_drb', 'home_drb',
            'visit_trb', 'home_trb', 'visit_ast',
            'home_ast', 'visit_stl', 'home_stl',
            'visit_blk', 'home_blk', 'visit_tov',
            'home_tov', 'visit_pts', 'home_pts']
            )

        scaler = StandardScaler()
        x = scaler.fit_transform(x)
        y = (df['game_result'] == df['home_team']).astype(int)

        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

        estimators = [
            ('rf', RandomForestClassifier(max_depth=7, n_estimators=50, max_samples=.8, random_state=42, min_samples_split=10, min_samples_leaf=20)),
            ('svm', SVC(C=.85, probability=True, gamma=.001, tol=.1, random_state=42)),
            ('mlp', MLPClassifier(hidden_layer_sizes=(150,), max_iter=100, random_state=42, batch_size=128)),
            ('mlp_sigmoid', MLPClassifier(hidden_layer_sizes=(100,),activation='logistic', max_iter=200, batch_size=64, random_state=42)),
            ('lgbm', LGBMClassifier(n_estimators=150, max_depth=4, num_leaves=7, learning_rate=0.017, min_child_samples=43, min_gain_to_split=3, subsample=1, random_state=42, verbosity=-1)),
            ('xgb', XGBClassifier(max_depth=5, n_estimators=150, reg_lambda=.75, random_state=42))
        ]

        stacking_clf = None
        file_path = f'{os.getcwd()}/server/src/Predictor.pkl'
        stacking_clf = StackingClassifier(estimators=estimators, final_estimator=LogisticRegression(solver='lbfgs', random_state=42, max_iter=1000, tol=.001))
        stacking_clf.fit(x_train, y_train)
        joblib.dump(stacking_clf, file_path)
        
        y_pred = stacking_clf.predict(x_test)
        print("Stacking Accuracy:", accuracy_score(y_test, y_pred))
        print("Stacking Classification Report:\n", classification_report(y_test, y_pred))

        df = self.database.get_all_games_year(2025)
        x = df.drop(columns = [
            'game_result', 'home_team', 'visit_team',
            'match_date', 'visit_mp', 'home_mp',
            'visit_fg', 'home_fg', 'visit_fga',
            'home_fga', 'home_pf', 'visit_pf',
            'visit_fg3', 'home_fg3', 'visit_fg3a',
            'home_fg3a', 'visit_fg_pct', 'home_fg_pct',
            'visit_fg3_pct', 'home_fg3_pct', 'visit_ft',
            'home_ft', 'visit_fta', 'home_fta',
            'visit_ft_pct', 'home_ft_pct', 'visit_orb',
            'home_orb', 'visit_drb', 'home_drb',
            'visit_trb', 'home_trb', 'visit_ast',
            'home_ast', 'visit_stl', 'home_stl',
            'visit_blk', 'home_blk', 'visit_tov',
            'home_tov', 'visit_pts', 'home_pts']
            )
        scaler = StandardScaler()
        x = scaler.fit_transform(x)
        y = (df['game_result'] == df['home_team']).astype(int)
        y_pred = stacking_clf.predict(x)
        print("Stacking Accuracy:", accuracy_score(y, y_pred))
