"""
Detect anomalies in user data to identify potential overtraining,
injury risks, or inconsistencies in workout logs.
"""

import numpy as np
from sklearn.ensemble import IsolationForest

# Example data: workout metrics (duration, intensity)
X = np.array([
    [30, 50], [35, 60], [40, 55], [20, 80],  # Normal
    [120, 90],  # Potential anomaly
])

# Train the model
model = IsolationForest(random_state=42)
model.fit(X)

# Predict anomalies
anomalies = model.predict(X)
print(f"Anomaly detection results: {anomalies}")
