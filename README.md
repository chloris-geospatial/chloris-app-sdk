# The Chloris Platform Python SDK

The Chloris Platform Python SDK (_chloris-app-sdk_) is a Python package that provides a convenient interface to the Chloris Platform API. It is designed to be used by both humans and machines, but if you are a human you may find it easier to use the [Chloris Platform](https://app.chloris.earth/) web interface. Note that the API is only available for use with premium organizations, please contact us if you are interested in using the API.

See the [API documentation](https://app.chloris.earth/docs/index.html) for more information about the Chloris Platform API.

See the [Python API reference](./docs/index.md) for the full list of functions and classes available in the SDK.

## Installation

To install the Chloris Platform Python SDK run:

```bash
pip install chloris_app_sdk
```

## Usage

### Authentication

The Chloris Platform API uses [OAuth 2.0](https://oauth.net/2/) for authentication. You can authenticate using either a refresh token or an ID token. Refresh tokens are long-lived and can be used to generate new ID tokens. ID tokens are short-lived and can be used directly for authentication. Refresh tokens are recommended for use in scripts and ID tokens are recommended for use in web applications.

See the [Chloris Platform API documentation](https://app.chloris.earth/docs/index.html) for more information about authentication.

### Listing sites

Here is an example which lists active sites in your organization, then prints the annual stock for the first site, and then the average biomass density for 2015:

```python
from chloris_app_sdk import ChlorisAppClient
from chloris_app_sdk.utils import to_tco2e

# create the client
client = ChlorisAppClient(
    organization_id="your-organization-id",
    refresh_token="your-refresh-token", # env: CHLORIS_REFRESH_TOKEN
    # or
    # id_token="your-id-token" # env: CHLORIS_ID_TOKEN
)

# list all active sites and get the stats for the first one
reporting_units = client.list_active_sites()
stats = client.get_reporting_unit_stats(reporting_units[0])

# print the annual stock (in tons co2e) for each year
for i, year in enumerate(stats["annualYears"]):
    stock = to_tco2e(stats["annualStock"][i])
    print(f"{year}: {stock} tco₂e")

# calculate average biomass density in t/ha for 2015:
i = stats["annualYears"].index(2015)
biomass_density = stats["annualStock"][i] / (stats["annualAreaKm2"][i] * 100)
print(f"Average biomass density in 2015: {biomass_density} t/ha")

```


