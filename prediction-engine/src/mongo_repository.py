"""Asynchronous MongoDB repository for prediction engine forecasts.

Persists complete forecast documents in the ``predicted_risk_forecasts``
collection including: resource_id, timestamp, urs_before, forecast,
timeline, confidence, business_impact, explanation, and algorithm_version.

All operations are deterministic — timestamps are supplied by the caller.
"""

import logging
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

COLLECTION_NAME: str = "predicted_risk_forecasts"


class MongoRepository:
    """Asynchronous MongoDB repository for prediction results.

    Parameters
    ----------
    mongo_uri : str
        MongoDB connection URI.
    db_name : str, optional
        Database name.  Defaults to ``"secops"``.
    """

    def __init__(self, mongo_uri: str, db_name: str = "devsecops_db") -> None:
        self.client: AsyncIOMotorClient = AsyncIOMotorClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[COLLECTION_NAME]
        logger.debug(
            "MongoRepository initialized: db=%s collection=%s",
            db_name,
            COLLECTION_NAME,
        )

    async def upsert_forecast(
        self,
        resource_id: str,
        forecast_doc: Dict[str, Any],
    ) -> None:
        """Insert or update the complete forecast for *resource_id*.

        Parameters
        ----------
        resource_id : str
            Unique identifier for the resource.
        forecast_doc : dict
            Complete forecast document.  Expected keys:
            ``timestamp``, ``urs_before``, ``projected_urs``, ``ctps``,
            ``factors``, ``risk_trend``, ``timeline``, ``confidence``,
            ``business_impact``, ``explanation``, ``algorithm_version``.
        """
        doc = {"resource_id": resource_id, **forecast_doc}
        await self.collection.update_one(
            {"resource_id": resource_id},
            {"$set": doc},
            upsert=True,
        )
        logger.info("Upserted forecast for %s", resource_id)

    async def get_forecast(
        self, resource_id: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve the stored forecast for *resource_id*.

        Returns ``None`` if no document exists.
        """
        doc = await self.collection.find_one(
            {"resource_id": resource_id}, {"_id": 0}
        )
        logger.debug("Fetched forecast for %s: %s", resource_id, bool(doc))
        return doc

    async def get_history(
        self, resource_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Return the most recent forecasts for *resource_id*.

        Parameters
        ----------
        limit : int
            Maximum number of documents to return.
        """
        cursor = (
            self.collection.find(
                {"resource_id": resource_id}, {"_id": 0}
            )
            .sort("timestamp", -1)
            .limit(limit)
        )
        results = await cursor.to_list(length=limit)
        logger.debug(
            "Forecast history for %s: %d documents", resource_id, len(results)
        )
        return results

    async def list_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Return the most recent forecast documents across all resources."""
        cursor = (
            self.collection.find({}, {"_id": 0})
            .sort("timestamp", -1)
            .limit(limit)
        )
        results = await cursor.to_list(length=limit)
        logger.debug("Listed all forecasts: %d documents", len(results))
        return results
