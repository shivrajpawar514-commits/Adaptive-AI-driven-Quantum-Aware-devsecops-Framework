import json
import os
import datetime
from typing import Tuple, Dict, Any

class ContextEngine:
    def __init__(self, profiles_path: str = None):
        if profiles_path is None:
            profiles_path = os.path.join(os.path.dirname(__file__), 'context_profiles.json')
            
        self.profiles_path = profiles_path
        self.profiles_data = self._load_profiles()

    def _load_profiles(self) -> Dict[str, Any]:
        if os.path.exists(self.profiles_path):
            with open(self.profiles_path, 'r') as f:
                return json.load(f)
        return {"profiles": {}, "version": "1.0.0"}

    def detect_context(self, timestamp: str = None, workload_profile: str = "Development") -> Tuple[str, str, str]:
        """
        Detects context and returns a tuple: (time_period, day_type, profile_name)
        """
        dt = None
        if timestamp:
            try:
                # Handle possible 'Z' suffix for UTC and other offsets
                ts_clean = timestamp.replace('Z', '+00:00')
                dt = datetime.datetime.fromisoformat(ts_clean)
            except Exception:
                pass
                
        if dt is None:
            dt = datetime.datetime.utcnow()

        # Determine day_type: Weekday or Weekend
        # weekday() returns 0 for Monday and 6 for Sunday
        if dt.weekday() in (5, 6):
            day_type = "Weekend"
        else:
            day_type = "Weekday"

        # Determine time_period: Morning, Afternoon, Evening, Night
        hour = dt.hour
        if 6 <= hour < 12:
            time_period = "Morning"
        elif 12 <= hour < 18:
            time_period = "Afternoon"
        elif 18 <= hour < 22:
            time_period = "Evening"
        else:
            time_period = "Night"

        # Determine profile name based on context rules
        if day_type == "Weekend":
            profile_name = "Weekend"
        elif time_period == "Night":
            profile_name = "Night"
        else:
            profile_name = "Business Hours"

        return time_period, day_type, profile_name

    def get_profile(self, profile_name: str) -> Dict[str, Any]:
        """
        Returns the data for the given profile. If profile does not exist, falls back to 'Standard'.
        """
        profiles = self.profiles_data.get("profiles", {})
        if profile_name in profiles:
            return profiles[profile_name]
        return profiles.get("Standard", {})

    def get_version(self) -> str:
        return self.profiles_data.get("version", "1.0.0")
