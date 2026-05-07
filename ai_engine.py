import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

class AIEngine:
    def __init__(self):
        self.model_path = 'models/anomaly_detector.pkl'
        self.model = None
        self.labels = ['NORMAL', 'CYBER_ATTACK', 'HARDWARE_FAILURE']
        
        # Ensure model directory exists
        if not os.path.exists('models'):
            os.makedirs('models')
            
        self._initialize_model()

    def _initialize_model(self):
        """Initializes or trains a baseline model if none exists."""
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
            except:
                self._train_baseline()
        else:
            self._train_baseline()

    def _train_baseline(self):
        """Generates synthetic data and trains a Random Forest classifier."""
        print("Training AI Baseline Model...")
        # Features: [Interval_Variance, Battery_Drain_Rate, Signal_Noise_Level]
        data = []
        
        # Normal
        for _ in range(100):
            data.append([np.random.normal(0.01, 0.005), np.random.normal(0.001, 0.0001), np.random.normal(0.02, 0.01), 0])
        
        # Cyber Attack (High variance, high battery drain)
        for _ in range(100):
            data.append([np.random.normal(0.5, 0.1), np.random.normal(0.05, 0.01), np.random.normal(0.02, 0.01), 1])
            
        # Hardware Failure (High noise, low battery drain)
        for _ in range(100):
            data.append([np.random.normal(0.01, 0.005), np.random.normal(0.001, 0.0001), np.random.normal(0.3, 0.1), 2])
            
        df = pd.DataFrame(data, columns=['variance', 'drain', 'noise', 'label'])
        X = df[['variance', 'drain', 'noise']]
        y = df['label']
        
        self.model = RandomForestClassifier(n_estimators=100)
        self.model.fit(X, y)
        joblib.dump(self.model, self.model_path)
        print("AI Model Trained and Saved.")

    def predict(self, features):
        """
        Predicts status based on features: [variance, drain, noise]
        """
        if self.model is None:
            return "UNKNOWN"
        
        X = np.array([features])
        prediction = self.model.predict(X)[0]
        confidence = np.max(self.model.predict_proba(X))
        
        return {
            "prediction": self.labels[int(prediction)],
            "confidence": round(float(confidence), 4)
        }

# Example usage:
# ai = AIEngine()
# result = ai.predict([0.01, 0.001, 0.02]) -> NORMAL
