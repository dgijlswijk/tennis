import pandas as pd

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
        self.participants = None
        try:
            self.participants = pd.read_csv("dataprocessor/participants.csv")
            self.games = pd.read_csv("dataprocessor/games.csv")
        except FileNotFoundError:
            print ("Participants or games data file not found. Please ensure the files exist in the specified path.")
