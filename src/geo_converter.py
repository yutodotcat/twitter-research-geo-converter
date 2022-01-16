""" role
    * convert and save format of geo
    * depends on MongoConnection classs
"""
from typing import Any, Dict, List, Optional, Tuple

import pymongo
from pymongo.cursor import Cursor
from simple_geocoding import Geocoding
from tqdm import tqdm
from utils.logger import LoggerFactory
from utils.methods import create_default_update_message

from src.mongo_connection import MongoConnection


class GeoConverter:

    geo: Geocoding = Geocoding("./latest.csv")
    MONGO_LOCATION_FIELD_NAME: str = "location_name"
    logger = LoggerFactory.create_save_info_or_more()

    @classmethod
    def average_longitude_latitude(
        cls,
        longitude_latitude_list: List[List[float]]
    ) -> Tuple[float, float]:

        longitude_list: List[float] = []
        latitude_list: List[float] = []

        for longitude_latitude in longitude_latitude_list:
            longitude_list.append(longitude_latitude[1])
            latitude_list.append(longitude_latitude[0])

        average_longitude: float = sum(longitude_list) / len(longitude_list)
        average_latitude: float = sum(latitude_list) / len(latitude_list)

        return (average_longitude, average_latitude)

    @classmethod
    def convert_geo_reverse_and_save(
        cls,
        collection_name: str,
        optional_query: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Comments:
            * database in config.json is used
        Args:
            * collection_name: collection name to be updated
        """
        mongo: MongoConnection = MongoConnection.create_instance_from_config()
        target_mongodb: MongoConnection = mongo.create_new_instance(
            collection_name=collection_name,
            same_collection=True  # type: ignore
        )

        update_data: List[Dict[str, Any]] = []
        LIMIT: int = 40000

        cursor: Cursor = target_mongodb.collection.find(
            {} if optional_query is None else optional_query
        )
        total: int = cursor.count()

        for tweet in tqdm(cursor, total=total):
            longitude: float
            latitude: float
            try:
                longitude, latitude = cls.average_longitude_latitude(
                    tweet[
                        "tweet_data"
                    ]["place"]["bounding_box"]["coordinates"][0]
                )
            except TypeError as error:
                # when place is null
                cls.logger.error(error)
                longitude = float(
                    tweet["tweet_data"]["coordinates"]["coordinates"][1])
                latitude = float(
                    tweet["tweet_data"]["coordinates"]["coordinates"][0])

            location_name_as_jp: str = cls.geo.addr(
                longitude,
                latitude
            )

            update_data.append(
                pymongo.UpdateOne(
                    {"_id": tweet["_id"]},
                    {"$set": {
                        cls.MONGO_LOCATION_FIELD_NAME: location_name_as_jp
                    }}
                    # upsert is not needed
                    # documents are already saved
                )
            )

            if len(update_data) == LIMIT:
                target_mongodb.collection.bulk_write(update_data)
                update_data = []
                cls.logger.info(
                    create_default_update_message(LIMIT, tweet["_id"])
                )
        if len(update_data) > 0:
            target_mongodb.collection.bulk_write(update_data)
            cls.logger.info(create_default_update_message(
                len(update_data), tweet["_id"])
            )
