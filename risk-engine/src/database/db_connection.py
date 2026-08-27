from pymongo import MongoClient
import os

class RiskDatabase:
    def __init__(self):
        self.client = None
        self.db = None
        self.mock_db = []
        try:
            mongo_uri = os.getenv("MONGO_URI")
            if not mongo_uri:
                raise ValueError("MONGO_URI env var is not set")
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=1000)
            self.db = self.client.devsecops_db
            self.client.admin.command('ping')
            self.is_mock = False
            print("Connected to MongoDB successfully.")
        except Exception:
            self.is_mock = True
            print("MongoDB unavailable. Falling back to Mock Database.")

    def insert_evaluation(self, doc):
        if self.is_mock:
            self.mock_db.append(doc)
            return True
        try:
            self.db.riskevaluations.insert_one(doc)
            return True
        except Exception as e:
            print(f"MongoDB write failed: {str(e)}")
            self.mock_db.append(doc)
            return False

    def get_history(self, limit=100):
        if self.is_mock:
            return sorted(self.mock_db, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]
        try:
            cursor = self.db.riskevaluations.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
            return list(cursor)
        except Exception:
            return sorted(self.mock_db, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]

    def get_latest(self):
        if self.is_mock:
            return self.mock_db[-1] if self.mock_db else None
        try:
            doc = self.db.riskevaluations.find_one({}, {"_id": 0}, sort=[("timestamp", -1)])
            return doc
        except Exception:
            return self.mock_db[-1] if self.mock_db else None

    def get_stats(self):
        history = self.get_history(1000)
        if not history:
            return {"total_evaluations": 0, "decisions_count": {}}
            
        total = len(history)
        counts = {}
        for doc in history:
            dec = doc.get("decision", "Unknown")
            counts[dec] = counts.get(dec, 0) + 1
            
        return {
            "total_evaluations": total,
            "decisions_count": counts
        }
