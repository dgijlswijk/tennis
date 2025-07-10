import pandas as pd
import numpy as np
import logging

class TennisTrainset:
    """
    A class to create and manage a dataset for training a machine learning model.
    """

    def __init__(self, ):
        """
        Initialize the Trainset with data and labels.

        Args:
            data (list or np.ndarray): The input features for training.
            labels (list or np.ndarray): The corresponding labels for the data.
        """

        # Load participants from a CSV file if available
        try:
            self.participants = pd.read_csv("dataprocessor/data/participants.csv")
            self.games = pd.read_csv("dataprocessor/data/games.csv")
        except FileNotFoundError as e:
            print ("Participants or games data file not found. Please ensure the files exist in the specified path.", e)

    def participant_features(self):
        part_df = self.participants.copy()
        np.random.seed(42)
        num_participants = part_df.shape[0]
        random_birthdates = pd.to_datetime(
            np.random.randint(
                pd.Timestamp("1970-01-01").value // 10**9,
                pd.Timestamp("2005-12-31").value // 10**9,
                num_participants
            ),
            unit='s'
        ).normalize()  # Set time to 00:00:00
        part_df['birthdate'] = random_birthdates
        return part_df

    def create_trainset(self):
        """
        Combine features from participants and games into a single DataFrame.
        """
        game_df = self.games.copy()
        part_df = self.participant_features()[['id', 'name', 'birthdate']]

        # Merge the two DataFrames on 'id'
        combined_df = pd.merge(
            game_df, 
            part_df.add_suffix('_home'),  # Add suffix to all columns in right table
            left_on='home_id', 
            right_on='id_home', 
            suffixes=('', ''), 
            how='inner'
        )
        combined_df = pd.merge(
            combined_df, 
            part_df.add_suffix('_away'),  # Add suffix to all columns in right table
            left_on='away_id', 
            right_on='id_away', 
            suffixes=('', ''), 
            how='inner'
        )

        combined_df.to_csv("trainset/data/combined_features.csv", index=False)
        
        logging.info("Combined features saved to trainset/data/combined_features.csv")

        return combined_df

if __name__ == "__main__":
    tts = TennisTrainset()
    tts.create_trainset()