import pandas as pd
import numpy as np
from src.preprocessing.pipeline import PreprocessingPipeline

def test_pipeline_cleaning_and_transform():
    df = pd.DataFrame([
        {"cpu_utilization": 12.0, "memory_usage_percent": 30.5, "disk_usage_percent": 25.0, "packet_rate_in": 100, "packet_rate_out": 200},
        {"cpu_utilization": 8.5, "memory_usage_percent": 28.0, "disk_usage_percent": 25.0, "packet_rate_in": 120, "packet_rate_out": 210},
        {"cpu_utilization": 15.0, "memory_usage_percent": 35.0, "disk_usage_percent": 25.0, "packet_rate_in": 150, "packet_rate_out": 250}
    ])
    
    pipeline = PreprocessingPipeline()
    X_pca = pipeline.fit_transform(df)
    
    assert X_pca.shape[0] == 3
    assert X_pca.shape[1] > 0
