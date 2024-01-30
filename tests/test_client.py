import random
import pytest
from chloris_app_sdk.client import ChlorisAppClient
from chloris_app_sdk.utils import is_token_expired
import os

test_resources_path = os.path.join(os.path.dirname(__file__), "test_resources")

TEST_ORGANIZATION_ID = 'dev-0183c887-4cb1-752d-8767-d328337a4312'
TEST_API = 'https://api-dev.chloris.earth/api/'

def test_is_token_expired():
    test_token_expired = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE2OTA5MjE3NDN9.W8ELUqPcKB6bgIVT_5tMuTJ7mTFnDNFnBTzad4FCZek"
    assert is_token_expired(test_token_expired) == True


# @pytest.mark.skip(reason="This is an integration-level test and makes real calls to AWS")
def test_client() -> None:
    # requires CHLORIS_REFRESH_TOKEN env variable to be set, makes real calls to AWS
    client = ChlorisAppClient(TEST_ORGANIZATION_ID, api_endpoint=TEST_API)
    access_token = client._get_access_token()
    assert access_token is not None
    id_token = client._get_id_token()
    assert id_token is not None
    creds = client._get_sts_temporary_credentials()
    # print(creds)
    assert creds is not None
    test_file = f"protected/{creds['IdentityId']}/{random.randint(0, 1000000)}_test.txt"
    client._upload_file(key=test_file, body="test")
    client._get_object_metadata(key=test_file)
    # test boundary upload succeeds
    with open(os.path.join(test_resources_path, "test_small_site.geojson"), "rt", encoding="utf-8") as f:
        test_file = f.read()
    boundary_path = client.upload_boundary_file(test_file)
    assert boundary_path is not None
    # test boundary upload fails (too large)
    with open(os.path.join(test_resources_path, "test_too_big_site.geojson"), "rt", encoding="utf-8") as f:
        test_file = f.read()
    with pytest.raises(Exception):
        client.upload_boundary_file(test_file)

def test_list_active_sites():
    from chloris_app_sdk import ChlorisAppClient

    client = ChlorisAppClient (TEST_ORGANIZATION_ID, api_endpoint=TEST_API)

    reporting_units = client.list_active_sites()

    assert len(reporting_units) > 0

def test_get_reporting_unit():
    from chloris_app_sdk import ChlorisAppClient

    client = ChlorisAppClient (TEST_ORGANIZATION_ID, api_endpoint=TEST_API)

    reporting_unit_id = '018a7b00-6d6f-79bd-8c2f-14624ead55c1'

    # using include_downloads=True will fetch the downloads index
    reporting_unit_entry = client.get_reporting_unit(reporting_unit_id, include_stats=True, include_layers_config=True, include_downloads=True)

    assert reporting_unit_entry['reportingUnitId'] == reporting_unit_id
    assert reporting_unit_entry['layersConfig'] is not None
    assert reporting_unit_entry['stats'] is not None
    assert reporting_unit_entry['downloads'] is not None

