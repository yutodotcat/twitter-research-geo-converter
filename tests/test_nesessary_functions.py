from typing import Any, Dict, List, Tuple, Type, Union

import pytest
from simple_geocoding import Geocoding


def test_simple_geo():
    """
    test simple_geo has been installed succssfully
    """
    LONGITUDE_LATITUDE_BY_LOCATION: Dict[str, Dict[str, float]] = {
        "hoya": {
            "latitude": 139.56770956492727,
            "longitude": 35.74836147033387
        },
        "okayama": {
            "latitude": 134.125872,
            "longitude": 34.777109
        }
    }
    HOYA_LATITUTDE_LONGITUDE: Dict[str, float] = LONGITUDE_LATITUDE_BY_LOCATION["hoya"]
    OKAYAMA_LATITUTDE_LONGITUDE: Dict[str, float] = LONGITUDE_LATITUDE_BY_LOCATION["okayama"]

    geo: Geocoding = Geocoding("./latest.csv")

    location_name: str = geo.addr(
        HOYA_LATITUTDE_LONGITUDE["longitude"],
        HOYA_LATITUTDE_LONGITUDE["latitude"]
    )

    assert "東京" in location_name and "保谷" in location_name

    okayama_location_name: str = geo.addr(
        OKAYAMA_LATITUTDE_LONGITUDE["longitude"],
        OKAYAMA_LATITUTDE_LONGITUDE["latitude"]
    )

    assert "岡山" in okayama_location_name
