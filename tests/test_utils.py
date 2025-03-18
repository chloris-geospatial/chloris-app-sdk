import json
import math
import random
import pytest

import os

# workaround to import from src directory
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from chloris_app_sdk.utils import is_token_expired,decode_jwt, to_tco2e

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

