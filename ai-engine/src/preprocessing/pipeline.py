import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
import joblib
import os

class PreprocessingPipeline:
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.pca = PCA(n_components=0.95)
        self.feature_cols = [
            'cpu_utilization', 'memory_usage_percent', 
            'disk_usage_percent', 'packet_rate_in', 'packet_rate_out'
        ]

    def fit_transform(self, df):
        df_clean = self._clean_data(df)
        X = df_clean[self.feature_cols].values
        X_scaled = self.scaler.fit_transform(X)
        X_pca = self.pca.fit_transform(X_scaled)
        return X_pca

    def transform(self, df):
        df_clean = self._clean_data(df)
        X = df_clean[self.feature_cols].values
        X_scaled = self.scaler.transform(X)
        X_pca = self.pca.transform(X_scaled)
        return X_pca

    def _clean_data(self, df):
        df = df.copy()
        
        if 'cpu' in df.columns:
            df['cpu_utilization'] = df['cpu'].apply(lambda x: x.get('utilization', 0) if isinstance(x, dict) else 0)
            df['memory_usage_percent'] = df['memory'].apply(lambda x: x.get('usagePercent', 0) if isinstance(x, dict) else 0)
            df['disk_usage_percent'] = df['disk'].apply(lambda x: x.get('usagePercent', 0) if isinstance(x, dict) else 0)
            df['packet_rate_in'] = df['network'].apply(lambda x: x.get('bytesRx', 0) if isinstance(x, dict) else 0)
            df['packet_rate_out'] = df['network'].apply(lambda x: x.get('bytesTx', 0) if isinstance(x, dict) else 0)

        for col in self.feature_cols:
            if col not in df.columns:
                df[col] = 0.0
                
        df = df.dropna(subset=self.feature_cols)
        df = df.drop_duplicates(subset=self.feature_cols)
        return df

    def save(self, filepath_dir):
        os.makedirs(filepath_dir, exist_ok=True)
        joblib.dump(self.scaler, os.path.join(filepath_dir, 'scaler.pkl'))
        joblib.dump(self.pca, os.path.join(filepath_dir, 'pca.pkl'))

    def load(self, filepath_dir):
        self.scaler = joblib.load(os.path.join(filepath_dir, 'scaler.pkl'))
        self.pca = joblib.load(os.path.join(filepath_dir, 'pca.pkl'))
