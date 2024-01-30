<!-- markdownlint-disable -->

# API Overview

## Modules

- [`chloris_app_sdk`](./chloris_app_sdk.md#module-chloris_app_sdk)
- [`chloris_app_sdk.client`](./chloris_app_sdk.client.md#module-chloris_app_sdkclient): This is the primary module of the chloris-app-sdk. 
- [`chloris_app_sdk.utils`](./chloris_app_sdk.utils.md#module-chloris_app_sdkutils): General utility functions. 

## Classes

- [`client.ChlorisAppClient`](./chloris_app_sdk.client.md#class-chlorisappclient): A client for interacting with the Chloris App API.

## Functions

- [`utils.decode_jwt`](./chloris_app_sdk.utils.md#function-decode_jwt): Decode a JWT token without validating it and return the payload as a dictionary.
- [`utils.is_token_expired`](./chloris_app_sdk.utils.md#function-is_token_expired): Check if a JWT token is expired without validating it.
- [`utils.to_tco2e`](./chloris_app_sdk.utils.md#function-to_tco2e): Convert tons of biomass to CO2 equivalent tons.
