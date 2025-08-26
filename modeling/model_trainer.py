# modeling/model_trainer.py
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

class ModelTrainer:
    def __init__(self):
        self.model = RandomForestClassifier()
        self.features = pd.read_csv('features/data/features.csv') 

    def train_model(self):
        # Prepare features and label
        X = self.features.drop(columns=['result', 'id_home', 'id_away'])
        y = self.features['result']

        gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
        train_idx, test_idx= next(gss.split(X, y, groups=self.features[['id_home', 'id_away']].apply(tuple, axis=1)))

        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        print(classification_report(y_test, y_pred))
        return self.model
    
if __name__ == "__main__":
    trainer = ModelTrainer()
    trained_model = trainer.train_model()
    print("Model trained successfully.")
    # save the model if needed
    # joblib.dump(trained_model, 'model.pkl')
