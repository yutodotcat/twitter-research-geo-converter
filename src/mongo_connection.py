import copy
import json
import os.path
from typing import Dict, List, Optional, Tuple

import pymongo


class MongoConnection:
    __SETTING_FILE: str = "/workspace/worker/config.json"
    __CONFIG_KEYS: Dict[str, str] = {
        key: key for key in [
            # must be same in config.json keys
            "auth",
            "database_name",
            "collection_name",
            "host",
            "port",
            "username",
            "password",
            "authSource",
            "authMechanism",
        ]
    }

    def __init__(self, settings: Dict[str, str]) -> None:
        self.collection: pymongo.MongoClient
        self.settings_cache: Dict[str, str]
        self.database_name_cache: str

        self.__validate_setting(settings)

        database_name: str = settings[
            self.__class__.__CONFIG_KEYS["database_name"]]
        collection_name: str = settings[
            self.__class__.__CONFIG_KEYS["collection_name"]]

        del settings[self.__class__.__CONFIG_KEYS["database_name"]]
        del settings[self.__class__.__CONFIG_KEYS["collection_name"]]

        # for subsequent instance createtion and validation
        self.settings_cache = settings
        self.database_name_cache = database_name
        self.collection_name_cache = collection_name

        # set self.collection
        self.__connect(database_name, collection_name, settings)

    def __validate_setting(self, settings: Dict[str, str]) -> None:
        """
        validate required arguments
        """
        key_list: List[str] = list(settings.keys())
        if self.__class__.__CONFIG_KEYS["database_name"] in key_list:
            return
        if self.__class__.__CONFIG_KEYS["collection_name"] in key_list:
            return

        raise KeyError(
            "both {} and {} are required to"
            "instantiate MongoConnection class".format(
                self.__class__.__CONFIG_KEYS["database_name"],
                self.__class__.__CONFIG_KEYS["collection_name"]
            )
        )

    def __connect(
        self,
        database_name: str = "",
        collection_name: str = "",
        settings: Dict[str, str] = {}
    ) -> None:

        if not (database_name and collection_name):
            raise ValueError("Both {} and {} are required".format(
                self.__class__.__CONFIG_KEYS["database_name"],
                self.__class__.__CONFIG_KEYS["collection_name"]
            ))

        AUTH: str = self.__class__.__CONFIG_KEYS["auth"]
        HOST: str = self.__class__.__CONFIG_KEYS["host"]
        PORT: str = self.__class__.__CONFIG_KEYS["port"]
        USERNAME: str = self.__class__.__CONFIG_KEYS["username"]
        PASSWORD: str = self.__class__.__CONFIG_KEYS["password"]
        AUTHSOURCE: str = self.__class__.__CONFIG_KEYS["authSource"]
        AUTHMECHANISM: str = self.__class__.__CONFIG_KEYS["authMechanism"]

        # todo: add branch on conditions
        # example: when host is undefined host is set as localhost
        if settings[AUTH] == "True":
            self.collection = pymongo.MongoClient(
                "{}:{}".format(settings[HOST], settings[PORT]),
                username=settings[USERNAME],
                password=settings[PASSWORD],
                authSource=settings[AUTHSOURCE],
                authMechanism=settings[AUTHMECHANISM]
            )[database_name][collection_name]
        else:
            self.collection = pymongo.MongoClient(
                "{}:{}".format(settings[HOST], settings[PORT])
            )[database_name][collection_name]

    def create_new_instance(
        self,
        **options: str,
    ) -> "MongoConnection":
        """
        create new instance from insntace setting cache
        is able to change target database and collection
        if options is not given config settings is used
        Args:
            * **options:
                * Dict[str, Union[str, bool]]
                database_name(str)
                collection_name(str)
                same_collection(bool)
        """
        deep_copied_settings: Dict[str, str] = copy.deepcopy(
            self.settings_cache
        )
        deep_copied_settings.update({
            self.__class__.__CONFIG_KEYS["database_name"]:
                self.database_name_cache,
            self.__class__.__CONFIG_KEYS["collection_name"]:
                self.collection_name_cache
        })

        if self.__class__.__CONFIG_KEYS["database_name"] in options:
            deep_copied_settings.update({
                self.__class__.__CONFIG_KEYS["database_name"]:
                    options[self.__class__.__CONFIG_KEYS["database_name"]]
            })
        if self.__class__.__CONFIG_KEYS["collection_name"] in options:
            deep_copied_settings.update({
                self.__class__.__CONFIG_KEYS["collection_name"]:
                    options[self.__class__.__CONFIG_KEYS["collection_name"]]
            })

        return self.__class__(deep_copied_settings)

    @classmethod
    def create_instance_from_config(cls) -> "MongoConnection":
        """
        read config.json and return new instance based on config
        config.json must be placed in same directory
        """
        new_instance: MongoConnection
        with open(cls.__SETTING_FILE, "r"
                  ) as setting_file:
            mongo_configs: Dict[str, str] = json.load(
                setting_file)["analysis"]["mongodb"]
            new_instance = MongoConnection(mongo_configs)
        return new_instance

    @classmethod
    def create_two_instance_for_analysis(
        cls,
        retrieve_collection_name: str,
        save_collection_name: Optional[str] = None,
    ) -> Tuple["MongoConnection", Optional["MongoConnection"]]:
        """
        Comment: return two mongo instance to be required by analysis
        Args:
            * **options:
                * whether accept same collection or not
                * Dict[Literal["same_collection"], bool]
        Return:
            MongoConnection: retrieve_mongo instance
            MongoConnection: save_mongo instance

            the order is important
        """
        save_mongo = None

        base_mongo: MongoConnection = cls.create_instance_from_config()
        retrieve_mongo: MongoConnection = base_mongo.create_new_instance(
            collection_name=retrieve_collection_name
        )
        if not (save_collection_name is None):
            save_mongo = retrieve_mongo.create_new_instance(
                collection_name=save_collection_name
            )
        return (retrieve_mongo, save_mongo)
