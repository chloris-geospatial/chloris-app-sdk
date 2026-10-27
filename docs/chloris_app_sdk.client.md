<!-- markdownlint-disable -->

<a href="https://github.com/chloris-geospatial/chloris-app-sdk/blob/main/src/chloris_app_sdk/client.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `chloris_app_sdk.client`
This is the primary module of the chloris-app-sdk.  



---

<a href="https://github.com/chloris-geospatial/chloris-app-sdk/blob/main/src/chloris_app_sdk/client.py#L24"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ChlorisAppClient`
A client for interacting with the Chloris App API. 

<a href="https://github.com/chloris-geospatial/chloris-app-sdk/blob/main/src/chloris_app_sdk/client.py#L27"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    organization_id: str,
    id_token: Optional[str] = None,
    access_token: Optional[str] = None,
    refresh_token: Optional[str] = None,
    api_endpoint: Optional[str] = None,
    http_pool: Optional[PoolManager] = None
) → None
```

Create a new client with the given authentication parameters. 



**Args:**
 
 - <b>`organization_id`</b>:  The organization id to use, may also be set via CHLORIS_ORGANIZATION_ID environment variable. 
 - <b>`id_token`</b>:  The user id token to use, may also be set via CHLORIS_ID_TOKEN environment variable. 
 - <b>`access_token`</b>:  The user access token to use, may also be set via CHLORIS_ACCESS_TOKEN environment variable. 
 - <b>`refresh_token`</b>:  The user refresh token to use, may also be set via CHLORIS_REFRESH_TOKEN environment variable. 
 - <b>`api_endpoint`</b>:  The Chloris App API endpoint to use, defaults to https://app.chloris.earth/api/, may also be set via CHLORIS_API_ENDPOINT environment variable. 
 - <b>`http_pool`</b>:  The urllib3 PoolManager to use for HTTP requests, if not provided a new one will be created. 




---

<a href="https://github.com/chloris-geospatial/chloris-app-sdk/blob/main/src/chloris_app_sdk/client.py#L985"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_collection`

```python
delete_collection(reporting_unit_id: str) → Mapping[str, Any]
```

Delete a collection in the Chloris App. This is a soft delete that sets the deletedAt timestamp. 



**Args:**
 
 - <b>`reporting_unit_id`</b>:  The reportingUnitId of the collection to delete. 

Returns: The API response message. 

---

<a href="https://github.com/chloris-geospatial/chloris-app-sdk/blob/main/src/chloris_app_sdk/client.py#L537"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_reporting_unit`

```python
delete_reporting_unit(reporting_unit_id: str) → Mapping[str, Any]
```

Delete a reporting unit in the Chloris App. This is a soft delete that sets the deletedAt timestamp. Restricted to organization administrators, owners, and managers. 



**Args:**
 
 - <b>`reporting_unit_id`</b>:  The id of the reporting unit to delete. 

Returns: The API response message. 

---

<a href="https://github.com/chloris-geospatial/chloris-app-sdk/blob/main/src/chloris_app_sdk/client.py#L284"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `download_geojson_boundary`

```python
download_geojson_boundary(path)
```

Download a GeoJSON boundary from the user data bucket 



**Args:**
 
 - <b>`path`</b>:  The path to the file in the protected user space 



**Returns:**
 The GeoJSON content as a string 

---

<a href="https://github.com/chloris-geospatial/chloris-app-sdk/blob/main/src/chloris_app_sdk/client.py#L670"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_reporting_unit`

```python
get_reporting_unit(
    reporting_unit_id: str,
    include_stats=False,
    include_layers_config=False,
    include_downloads=False
) → Mapping[str, Any]
```

Get a site with its control (if it has one). Optionally also retrieving all stats, layers config, and downloads index. 



**Args:**
 
 - <b>`reporting_unit_id`</b>:  The id of the site to get. 
 - <b>`include_stats`</b>:  If True, also retrieve the stats for the site. 
 - <b>`include_layers_config`</b>:  If True, also retrieve the layers config for the site. 
 - <b>`include_downloads`</b>:  If True, also retrieve the downloads index for the site. 



**Returns:**
 The reporting unit entry like:  { 
 - <b>`"reportingUnitId"`</b>:  "string", 
 - <b>`"label"`</b>:  "string", 
 - <b>`"description"`</b>:  "string", 
 - <b>`"tags"`</b>:  [ "string", ... ], 
 - <b>`"createdAt"`</b>:  "string", 
 - <b>`"updatedAt"`</b>:  "string", 
 - <b>`"deletedAt"`</b>:  "string", 
 - <b>`"controlReportingUnitId"`</b>:  { 
 - <b>`"reportingUnitId"`</b>:  "string", 
 - <b>`"label"`</b>:  "string", # ... }, 
 - <b>`"layersConfig"`</b>:  {  # ... }, 
 - <b>`"downloads"`</b>:  {  # ... } } 

---

<a href="https://github.com/chloris-geospatial/chloris-app-sdk/blob/main/src/chloris_app_sdk/client.py#L832"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_reporting_unit_downloads`

```python
get_reporting_unit_downloads(
    reporting_unit_entry: Mapping[str, Any]
) → Optional[Mapping[str, Any]]
```

Get the downloads index for a site, if available. 



**Args:**
 
 - <b>`reporting_unit_entry`</b>:  The site entry. 



**Returns:**
 The site downloads index or None if not available. 

---

<a href="https://github.com/chloris-geospatial/chloris-app-sdk/blob/main/src/chloris_app_sdk/client.py#L804"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_reporting_unit_layers_config`

```python
get_reporting_unit_layers_config(
    reporting_unit_entry: Mapping[str, Any]
) → Mapping[str, Any]
```

Get the layers config for a site. 



**Args:**
 
 - <b>`reporting_unit_entry`</b>:  The site entry. 



**Returns:**
 The site layers config. 

---

<a href="https://github.com/chloris-geospatial/chloris-app-sdk/blob/main/src/chloris_app_sdk/client.py#L756"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_reporting_unit_stats`

```python
get_reporting_unit_stats(
    reporting_unit_entry: Mapping[str, Any]
) → Mapping[str, Any]
```

Get the stats for a site. 



**Args:**
 
 - <b>`reporting_unit_entry`</b>:  The site entry. 



**Returns:**
 The site stats. 

---

<a href="https://github.com/chloris-geospatial/chloris-app-sdk/blob/main/src/chloris_app_sdk/client.py#L560"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_active_sites`

```python
list_active_sites() → Sequence[Mapping[str, Any]]
```

List all active sites for the organization. This is a convenience function that filters the list of sites to only include active sites. 



**Returns:**
  A list of reporting unit entries. 

---

<a href="https://github.com/chloris-geospatial/chloris-app-sdk/blob/main/src/chloris_app_sdk/client.py#L960"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `put_collection`

```python
put_collection(collection_entry: Mapping[str, Any]) → Mapping[str, Any]
```

Create or update a collection in the Chloris App. Omit the reportingUnitId field to create a new collection. 



**Args:**
 
 - <b>`collection_entry`</b>:  The collection entry to create or update. 

Returns: The new or updated collection. 

---

<a href="https://github.com/chloris-geospatial/chloris-app-sdk/blob/main/src/chloris_app_sdk/client.py#L474"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `put_reporting_unit`

```python
put_reporting_unit(reporting_unit_entry: Mapping[str, Any]) → Mapping[str, Any]
```

Create or update a reporting unit in the Chloris App. 

Errors are raised with the status code in the message: 


- 409: a site with the same label, resolution and area already exists in the organization.  Admins can pass `allowDuplicate=True`. Dryrun sites are exempt. 
- 403: `bypassAnalysis=True` was passed by a non-admin. 
- 502 "could not be submitted for analysis": the site was not submitted and was rolled back. This is  retried automatically up to 3 times with exponential backoff, except for `allowDuplicate` or  `calibratedFrom` entries. If the first attempt's job may still be running, its site is kept and the  retry raises a 409 naming it, and that site will still be analyzed. 
- Any other 502 (e.g. "Internal server error") is raised without retrying, since the site may already  exist. Check `list_active_sites()` before resubmitting. 

Other errors are not retried. 



**Args:**
 
 - <b>`reporting_unit_entry`</b>:  The reporting unit entry to create or update. A normalized `boundaryPath`  is purged after 30 days if no site references it, so submit soon after uploading  rather than reusing an old path. 

Returns: The new reporting unit entry. 



**Raises:**
 
 - <b>`Exception`</b>:  If the API rejects the request (see the status codes above). 

---

<a href="https://github.com/chloris-geospatial/chloris-app-sdk/blob/main/src/chloris_app_sdk/client.py#L136"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `refresh_tokens`

```python
refresh_tokens() → None
```

Refresh the id and access tokens using the refresh token. 

---

<a href="https://github.com/chloris-geospatial/chloris-app-sdk/blob/main/src/chloris_app_sdk/client.py#L598"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `search_sites`

```python
search_sites(
    label: str,
    limit: int = 1000,
    max_pages: int = 5
) → Sequence[Mapping[str, Any]]
```

Search active sites by label substring (case-sensitive). 

Results are returned in the order the server provides them: completed sites are sorted by analysisCompletedAt descending, with non-completed sites at the end. 



**Args:**
 
 - <b>`label`</b>:  Substring to match against site labels. 
 - <b>`limit`</b>:  Items scanned per page server-side, max 1000. 
 - <b>`max_pages`</b>:  Scan pages per request, max 50. Increase for sparse matches  in very large organizations. 



**Returns:**
 Matching reporting unit entries (excludes deleted sites and aggregation branches). 



**Raises:**
 
 - <b>`ValueError`</b>:  If label is empty or whitespace-only. Use list_active_sites()  to retrieve every site in the organization. 

---

<a href="https://github.com/chloris-geospatial/chloris-app-sdk/blob/main/src/chloris_app_sdk/client.py#L867"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `submit_site`

```python
submit_site(
    label: str,
    boundary_path: str,
    tags: Sequence[str] = None,
    description: str = None,
    control_boundary_path: Optional[str] = None,
    notify: Optional[bool] = True,
    period_change_start_year: Optional[int] = None,
    period_change_end_year: Optional[int] = None,
    resolution: Optional[int] = None,
    forest_baseline_year: Optional[int] = None,
    geometry_kwargs: Optional[Mapping[str, Any]] = {},
    **kwargs
) → Mapping[str, Any]
```

A high-level function to submit a site to the Chloris App. Automatically chooses the best method to upload the boundary (geojson or S3 multipart upload). 

See https://app.chloris.earth/docs -> API Reference -> PUT /reportingUnit for additional parameters. 



**Args:**
 
 - <b>`label`</b>:  The label for the site. 
 - <b>`tags`</b>:  The tags for the site. 
 - <b>`description`</b>:  The description for the site. 
 - <b>`boundary_path`</b>:  The path to the boundary file to upload. Either a local file path or a https url to a geojson file on a remote server. 
 - <b>`control_boundary_path`</b>:  The path to the control boundary file to upload. Either a local file path or a https url to a geojson file on a remote server. 
 - <b>`notify`</b>:  Whether to send email notifications when the site is ready. 
 - <b>`period_change_start_year`</b>:  The start of the period of interest 
 - <b>`period_change_end_year`</b>:  The end of the period of interest (inclusive) 
 - <b>`resolution`</b>:  The desired resolution of the outputs. Valid options are 30 and 10 (meters). Defaults to 30. 
 - <b>`forest_baseline_year`</b>:  The year to use as the forest baseline year. 
 - <b>`geometry_kwargs`</b>:  Optional arguments to pass to the boundary upload process. Admins only.  Set `simplifyGeometry=False` to keep the uploaded geometry unsmoothed.  `sparseConvexHullPercentLimit` and `sparseBboxPercentLimit` must be numbers from 0 to 1.  Wrong types or out-of-range values are rejected with a 400 from `POST /boundary`. 

Returns: The new reporting unit entry. 



**Raises:**
 
 - <b>`Exception`</b>:  If the API rejects the boundary or the site. The status codes are listed  in `put_reporting_unit()`. A 502 saying the site could not be submitted is retried  automatically up to 3 times. 


