import json
import random
import pytest

import os

# workaround to import from src directory
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from chloris_app_sdk import ChlorisAppClient

test_resources_path = os.path.join(os.path.dirname(__file__), "test_resources")

TEST_ORGANIZATION_ID = 'dev-0183c887-4cb1-752d-8767-d328337a4312'
TEST_API = 'https://app-dev.chloris.earth/api/'



def test_client() -> None:
    # requires CHLORIS_REFRESH_TOKEN env variable to be set, makes real calls to AWS
    client = ChlorisAppClient(TEST_ORGANIZATION_ID, api_endpoint=TEST_API)

    id_token = client._get_id_token()
    assert id_token is not None
    creds = client._get_sts_temporary_credentials()
    assert creds is not None
    test_file = f"protected/{creds['IdentityId']}/{random.randint(0, 1000000)}_test.txt"
    client._upload_file(key=test_file, body="test")
    client._get_object_metadata(key=test_file)
    # test geojson boundary upload succeeds (remote url)
    boundary_path = client._upload_boundary_remote_geojson(
        "https://raw.githubusercontent.com/chloris-geospatial/chloris-app-sdk/main/tests/test_resources/test_small_site.geojson")
    assert boundary_path is not None

    # test boundary upload succeeds
    boundary_path = client._upload_boundary_file(os.path.join(test_resources_path, "test_small_site.geojson"))
    assert boundary_path is not None
    # test boundary upload fails (too large)
    with pytest.raises(Exception):
        client._upload_boundary_file(os.path.join(test_resources_path, "test_too_big_site.geojson"))

    # test site submission succeeds
    reporting_unit = client.submit_site(
        label="site 1",
        boundary_path=os.path.join(test_resources_path, "test_small_site.geojson"),
        control_boundary_path=os.path.join(test_resources_path, "test_small_site.geojson"),
        description="test description",
        tags=['test'],
        dryrun=True,
        notify=False,
        period_change_start_year=2000,
        period_change_end_year=2023
    )
    assert reporting_unit.get('reportingUnitId') is not None


def test_list_active_sites():
    client = ChlorisAppClient(TEST_ORGANIZATION_ID, api_endpoint=TEST_API)

    reporting_units = client.list_active_sites()

    assert len(reporting_units) > 0


def test_get_reporting_unit():
    client = ChlorisAppClient(TEST_ORGANIZATION_ID, api_endpoint=TEST_API)

    reporting_unit_id = '018a7b00-6d6f-79bd-8c2f-14624ead55c1'

    # using include_downloads=True will fetch the downloads index
    reporting_unit_entry = client.get_reporting_unit(reporting_unit_id, include_stats=True, include_layers_config=True, include_downloads=True)

    assert reporting_unit_entry['reportingUnitId'] == reporting_unit_id
    assert reporting_unit_entry['layersConfig'] is not None
    assert reporting_unit_entry['annualYears'] is not None
    # assert reporting_unit_entry['downloads'] is not None


def test__get_sts_temporary_credentials():
    client = ChlorisAppClient(TEST_ORGANIZATION_ID, api_endpoint=TEST_API)

    creds = client._get_sts_temporary_credentials()

    assert creds is not None
    assert client._get_id_token() is not None

@pytest.mark.skipif(os.environ.get('CHLORIS_ID_TOKEN') is not None and os.environ.get('CHLORIS_REFRESH_TOKEN') is None, reason="requires refresh token")
def test_refresh_tokens():
    client = ChlorisAppClient(TEST_ORGANIZATION_ID, api_endpoint=TEST_API)

    assert client._get_id_token() is not None

    client.refresh_tokens()

    assert client._get_id_token() is not None
    assert client._get_sts_temporary_credentials() is not None

    client = ChlorisAppClient(TEST_ORGANIZATION_ID, api_endpoint=TEST_API)

    assert client._get_id_token() is not None
