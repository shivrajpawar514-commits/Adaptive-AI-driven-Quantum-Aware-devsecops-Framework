from pymongo import MongoClient
import pandas as pd
import os

def load_data_from_mongodb():
    try:
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            raise ValueError("MONGO_URI env var is not set")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=1000)
        db = client.devsecops_db
        collection = db.monitoringmetrics
        cursor = collection.find().sort("createdAt", -1).limit(1000)
        data = list(cursor)
        if len(data) >= 20:
            return pd.DataFrame(data)
    except Exception as e:
        print(f"MongoDB connection failed: {str(e)}. Using synthetic fallback...")

    # Fallback: Seed with synthetic baseline metrics to ensure trainability
    print("Generating data fallback...")
    import random
    synthetic = []
    for _ in range(100):
        synthetic.append({
            "cpu": {"utilization": random.uniform(2.0, 15.0), "cores": 4},
            "memory": {"usagePercent": random.uniform(10.0, 45.0), "total": 8000, "free": 5000, "used": 3000},
            "disk": {"usagePercent": random.uniform(20.0, 30.0), "size": 100000, "used": 25000, "free": 75000},
            "network": {"bytesRx": random.randint(100, 5000), "bytesTx": random.randint(100, 5000)},
            "system": {"hostname": "synthetic-node", "uptime": 1000}
        })
    return pd.DataFrame(synthetic)
