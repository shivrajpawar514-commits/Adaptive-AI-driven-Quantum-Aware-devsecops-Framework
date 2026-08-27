import pytest
import sys
import pathlib
from unittest.mock import AsyncMock, MagicMock

engine_root = str(pathlib.Path(__file__).parents[1])
if engine_root not in sys.path:
    sys.path.insert(0, engine_root)

from src.mongo_repository import MongoRepository

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.mark.anyio
async def test_upsert_forecast():
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = AsyncMock()
    
    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection
    
    repo = MongoRepository("mongodb://localhost:27017")
    repo.client = mock_client
    repo.db = mock_db
    repo.collection = mock_collection
    
    forecast_doc = {
        "timestamp": "2026-07-24T22:00:00Z",
        "urs_before": 50.0,
        "projected_urs": {"1": 50.0},
        "ctps": 1.0,
        "factors": {},
        "risk_trend": "stable",
        "timeline": [],
        "confidence": {},
        "business_impact": {},
        "explanation": [],
        "algorithm_version": "v1"
    }
    
    await repo.upsert_forecast("res-123", forecast_doc)
    mock_collection.update_one.assert_called_once_with(
        {"resource_id": "res-123"},
        {"$set": {"resource_id": "res-123", **forecast_doc}},
        upsert=True
    )

@pytest.mark.anyio
async def test_get_forecast():
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = AsyncMock()
    
    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection
    
    repo = MongoRepository("mongodb://localhost:27017")
    repo.client = mock_client
    repo.db = mock_db
    repo.collection = mock_collection
    
    expected_doc = {"resource_id": "res-123", "urs_before": 50.0}
    mock_collection.find_one.return_value = expected_doc
    
    res = await repo.get_forecast("res-123")
    assert res == expected_doc
    mock_collection.find_one.assert_called_once_with(
        {"resource_id": "res-123"}, {"_id": 0}
    )
