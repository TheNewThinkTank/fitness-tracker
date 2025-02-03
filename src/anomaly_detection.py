"""
Detect anomalies in user data to identify potential overtraining,
injury risks, or inconsistencies in workout logs.
"""

from loguru import logger  # type: ignore
import numpy as np
from sklearn.ensemble import IsolationForest  # type: ignore


def train_anomaly_detector(data):
    """Trains an Isolation Forest model on the given data.

    :param data: The input data for training the model.
    :type data: np.ndarray
    :return: The trained model.
    :rtype: IsolationForest
    """

    model = IsolationForest(random_state=42)
    model.fit(data)
    return model


def predict_anomalies(model, data):
    """Predicts anomalies in the data using the provided model.

    :param model: The trained Isolation Forest model.
    :type model: IsolationForest
    :param data: The data to predict anomalies on.
    :type data: np.ndarray
    :return: An array of -1 for anomalies and 1 for normal points.
    :rtype: np.ndarray
    """

    anomalies = model.predict(data)
    logger.debug(f"Anomaly detection results: {anomalies}")
    return anomalies


# Example data: workout metrics (duration, intensity)
X = np.array([
    [30, 50], [35, 60], [40, 55], [20, 80],  # Normal
    [120, 90],  # Potential anomaly
])

# Train the model
model = train_anomaly_detector(X)

# Predict anomalies
anomalies = predict_anomalies(model, X)
