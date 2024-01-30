<!-- markdownlint-disable -->

<a href="https://github.com/chloris-geospatial/chloris-app-sdk/blob/main/chloris-app-sdk/src/chloris_app_sdk/utils.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `chloris_app_sdk.utils`
General utility functions.  


---

<a href="https://github.com/chloris-geospatial/chloris-app-sdk/blob/main/chloris-app-sdk/src/chloris_app_sdk/utils.py#L8"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `is_token_expired`

```python
is_token_expired(token: str, expiration_tolerance: int = 10) → bool
```

Check if a JWT token is expired without validating it. 



**Args:**
 
 - <b>`token`</b> (str):  The JWT token to check. 
 - <b>`expiration_tolerance`</b> (int, optional):  The number of minutes before the token expires to consider it expired. Defaults to 10. 



**Returns:**
 
 - <b>`bool`</b>:  True if the token is expired, False otherwise. 


---

<a href="https://github.com/chloris-geospatial/chloris-app-sdk/blob/main/chloris-app-sdk/src/chloris_app_sdk/utils.py#L33"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `decode_jwt`

```python
decode_jwt(token: str) → Mapping[str, Any]
```

Decode a JWT token without validating it and return the payload as a dictionary. 



**Args:**
 
 - <b>`token`</b> (str):  The JWT token to decode. 



**Returns:**
 
 - <b>`Mapping[str, Any]`</b>:  The decoded payload as a dictionary. 


---

<a href="https://github.com/chloris-geospatial/chloris-app-sdk/blob/main/chloris-app-sdk/src/chloris_app_sdk/utils.py#L50"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `to_tco2e`

```python
to_tco2e(x: Optional[float]) → Optional[float]
```

Convert tons of biomass to CO2 equivalent tons. 



**Args:**
 
 - <b>`x`</b> (float):  Tons biomass 



**Returns:**
 
 - <b>`float`</b>:  Tons CO2 equivalent 


