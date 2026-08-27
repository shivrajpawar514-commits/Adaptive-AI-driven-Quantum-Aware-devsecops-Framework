import pytest
import sys
import pathlib
from unittest.mock import AsyncMock, MagicMock

engine_root = str(pathlib.Path(__file__).parents[1])
if engine_root not in sys.path:
    sys.path.insert(0, engine_root)

# Mock MongoRepository dependency during import/startup
import os
from unittest.mock import patch

with patch('src.mongo_repository.MongoRepository') as MockRepo:
    MockRepo.return_value.upsert_forecast = AsyncMock()
    from src.prediction_api import app

from fastapi.testclient import TestClient

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "OK"

def test_prediction_endpoint():
    response = client.get("/prediction/test-res?current_urs=50.0")
    assert response.status_code == 200
    data = response.json()
    assert data["resource_id"] == "test-res"
    assert data["current_urs"] == 50.0
    assert "projected_urs" in data
    assert "ctps" in data
    assert "timeline" in data
    assert "confidence" in data
    assert "business_impact" in data
    assert "explanation" in data
    assert data["algorithm_version"] == "CTPS-v1.0"

def test_prediction_endpoint_invalid_urs():
    response = client.get("/prediction/test-res?current_urs=-5.0")
    assert response.status_code == 422
