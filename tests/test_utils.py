import json
import math
import random
import pytest

import os

# workaround to import from src directory
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from chloris_app_sdk.utils import is_token_expired,decode_jwt, to_tco2e, to_legacy_layers_config

test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE2OTA5MjE3NDN9.W8ELUqPcKB6bgIVT_5tMuTJ7mTFnDNFnBTzad4FCZek"

def test_is_token_expired():
    assert is_token_expired(test_token) == True


# decode_jwt
def test_decode_jwt():
    assert decode_jwt(test_token) == {'sub': '1234567890', 'name': 'John Doe', 'iat': 1516239022, 'exp': 1690921743}


# to_tco2e
def test_to_tco2e():
    assert round(to_tco2e(1),2) == pytest.approx(1.83)
    assert to_tco2e(None) is None
    assert to_tco2e(0) == 0
    assert to_tco2e(float('inf')) == float('inf')
    assert math.isnan(to_tco2e(float('NaN')))

def test_layers_config_forwards_compatibility():
    layers_config = json.loads("""
    {
  "organizationId": "0194dfc7-24fe-7fe3-81a7-9a092df9fdff",
  "reportingUnitId": "0194dfd8-a826-7fb3-9c82-204571bc113f_2025-02-07T09:58Z",
  "annualLayers": [
    {
      "productType": "stock",
      "resolution": 10,
      "urlTemplate": "/tiles/cog/tiles/WebMercatorQuad/{z}/{x}/{y}.webp?url=s3://chloris-app-data/data/0194dfc7-24fe-7fe3-81a7-9a092df9fdff/0194dfd8-a826-7fb3-9c82-204571bc113f_2025-02-07T09:58Z/cogs/stock/index.vrt&bidx={yearBand}&colormap_name={mapStyle}&rescale=0,276.0&return_mask=true",
      "years": [
        2017,
        2018,
        2019,
        2020,
        2021,
        2022,
        2023
      ],
      "scale": [
        0,
        276
      ],
      "scaleUnit": "t/ha",
      "mapStyle": "2024-04-09_stock_light_650",
      "minZoom": 0,
      "maxZoom": 15,
      "format": "WEBP",
      "tileSize": 512,
      "tileMethod": "dynamic",
      "carbonPool": "agb"
    },
    {
      "productType": "change",
      "resolution": 10,
      "urlTemplate": "/tiles/cog/tiles/WebMercatorQuad/{z}/{x}/{y}.webp?url=s3://chloris-app-data/data/0194dfc7-24fe-7fe3-81a7-9a092df9fdff/0194dfd8-a826-7fb3-9c82-204571bc113f_2025-02-07T09:58Z/cogs/change/index.vrt&bidx={yearBand}&colormap_name={mapStyle}&return_mask=true",
      "years": [
        2018,
        2019,
        2020,
        2021,
        2022,
        2023
      ],
      "scale": [
        0,
        0,
        0
      ],
      "scaleUnit": "t/ha",
      "mapStyle": "2022-11-18_change_light",
      "minZoom": 0,
      "maxZoom": 15,
      "format": "WEBP",
      "tileSize": 512,
      "carbonPool": "agb"
    }
  ],
  "formatVersion": "1.0"
}
    """)
    legacy_layers_config = to_legacy_layers_config(layers_config)
    assert legacy_layers_config["stock"]["dynamic-10m"]["urlTemplate"]  is not None
    assert legacy_layers_config["change"]["dynamic-10m-user-period"]["urlTemplate"] is not None

