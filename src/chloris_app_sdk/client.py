""" This is the primary module of the chloris-app-sdk. """
import os
import uuid
from time import sleep
from typing import Any, Dict, Mapping, Optional, Sequence, Union
import json
from datetime import datetime, timedelta, timezone

from botocore.exceptions import ClientError
from urllib3 import PoolManager
import boto3
from .utils import is_token_expired
import logging

from botocore.config import Config

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("chloris_app_sdk.client")

class ChlorisAppClient:
    """A client for interacting with the Chloris App API."""

    def __init__(
        self,
        organization_id: str,
        id_token: Optional[str] = None,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        api_endpoint: Optional[str] = None,
        http_pool: Optional[PoolManager] = None,
    ) -> None:
        """
        Create a new client with the given authentication parameters.

        Args:
            organization_id: The organization id to use, may also be set via CHLORIS_ORGANIZATION_ID environment variable.
            id_token: The user id token to use, may also be set via CHLORIS_ID_TOKEN environment variable.
            access_token: The user access token to use, may also be set via CHLORIS_ACCESS_TOKEN environment variable.
            refresh_token: The user refresh token to use, may also be set via CHLORIS_REFRESH_TOKEN environment variable.
            api_endpoint: The Chloris App API endpoint to use, defaults to https://app.chloris.earth/api/, may also be set via CHLORIS_API_ENDPOINT environment variable.
            http_pool: The urllib3 PoolManager to use for HTTP requests, if not provided a new one will be created.
        """

        # lazily loaded variables
        self._sts_credentials = None  # type: Optional[Mapping[str, Any]]
        self._cognito_idp_client = None
        self._cognito_identity_client = None
        self._s3_bucket_resource = None
        self._s3_client = None

        # parameter parsing
        self.organization_id = organization_id
        self.api_endpoint = api_endpoint
        self.__id_token = id_token
        self.__access_token = access_token
        self.__refresh_token = refresh_token
        self._http_pool = http_pool if http_pool is not None else PoolManager()
        # attempt to get params from environment variables
        if self.organization_id is None:
            self.organization_id = os.environ.get("CHLORIS_ORGANIZATION_ID")
        if self.api_endpoint is None:
            self.api_endpoint = os.environ.get("CHLORIS_API_ENDPOINT")
        if self.api_endpoint is None:
            self.api_endpoint = "https://app.chloris.earth/api/"
        if not self.api_endpoint.endswith("/"):
            self.api_endpoint += "/"
        self.data_path = self.api_endpoint.replace("/api/", "/data/")
        if self.__id_token is None:
            self.__id_token = os.environ.get("CHLORIS_ID_TOKEN")
        if self.__access_token is None:
            self.__access_token = os.environ.get("CHLORIS_ACCESS_TOKEN")
        if self.__refresh_token is None:
            self.__refresh_token = os.environ.get("CHLORIS_REFRESH_TOKEN")
        # Ensure the access token we have is not expired
        if self.__access_token is not None:
            if is_token_expired(self.__access_token):
                self.__access_token = None
        if self.__id_token is not None:
            if is_token_expired(self.__id_token):
                self.__id_token = None
        # Ensure we have at least the id_token or refresh_token
        if self.__id_token is None and self.__refresh_token is None:
            raise ValueError("You must provide either an id_token or refresh_token. See help at: https://app.chloris.earth/docs/")
        self._get_api_info()

        # attempt to get access token from refresh token
        if self.__id_token is None:
            self.__id_token = self._get_id_token()

    def _get_api_info(self) -> None:
        """Get the environment-specific info for the Chloris API"""
        response = self._http_pool.request('GET', self.api_endpoint + 'info')
        if response.status != 200:
            raise Exception("Failed to retrieve info from Chloris API")
        response_json = json.loads(response.data.decode('utf-8'))
        self._aws_resources = response_json

    def _get_id_token(self) -> str:
        """
        Get the id token, refreshing it if needed.

        Returns: The id token.
        """
        # check that the id token is not about to expire (10 minutes)
        if self.__id_token is not None and is_token_expired(self.__id_token):
            self.__id_token = None
        # get a new id token using the refresh token if needed
        if self.__id_token is None:
            self.refresh_tokens()
        if self.__id_token is None:
            raise Exception("Failed to refresh id token for Chloris App")
        # return the id token
        return self.__id_token

    def _get_access_token(self) -> str:
        """Get the access token, refreshing it if needed.

        Returns: The access token.
        """
        # check that the access token is not about to expire (10 minutes)
        if self.__access_token is not None and is_token_expired(self.__access_token):
            self.__access_token = None
        # get a new access token using the refresh token if needed
        if self.__access_token is None:
            self.refresh_tokens()
        if self.__access_token is None:
            raise Exception("Failed to refresh access token for Chloris App")
        # return the access token
        return self.__access_token

    def refresh_tokens(self) -> None:
        """Refresh the id and access tokens using the refresh token."""
        if self.__refresh_token is None:
            raise Exception("Session expired and no refresh token provided")
        try:
            response = self._get_cognito_idp_client().initiate_auth(
                AuthFlow="REFRESH_TOKEN",
                AuthParameters={"REFRESH_TOKEN": self.__refresh_token},
                ClientId=self._aws_resources["awsUserPoolWebClientId"],
            )
            self.__access_token = response["AuthenticationResult"]["AccessToken"]
            self.__id_token = response["AuthenticationResult"]["IdToken"]
        except Exception as ex:
            raise Exception("Failed to refresh tokens for Chloris App") from ex

    def _get_cognito_idp_client(self) -> Any:
        """
        Get the boto3 cognito idp client, creating it if needed.

        Returns: The boto3 cognito idp client.
        """
        if self._cognito_idp_client is None:
            self._cognito_idp_client = boto3.client("cognito-idp", config=Config(region_name=self._aws_resources["awsRegion"]))
        return self._cognito_idp_client

    def _get_s3_client(self) -> Any:
        """
        Get the boto3 s3 client, creating it if needed.

        Returns: The boto3 s3 client.
        """
        # check if the credentials are expired
        if self._sts_credentials_expired():
            self._s3_client = None
        # get new client if needed
        if self._s3_client is None:
            credentials = self._get_sts_temporary_credentials()
            self._s3_client = boto3.client(
                "s3",
                aws_access_key_id=credentials["AccessKeyId"],
                aws_secret_access_key=credentials["SecretKey"],
                aws_session_token=credentials["SessionToken"],
                config=Config(region_name=self._aws_resources["awsRegion"], ))
        return self._s3_client

    def _get_s3_bucket_resource(self) -> Any:
        """
        Get the boto3 s3 bucket resource, creating it if needed.

        Returns: The boto3 s3 bucket resource.
        """

        # check if the credentials are expired
        if self._sts_credentials_expired():
            self._s3_bucket_resource = None
        # get new resource if needed
        if self._s3_bucket_resource is None:
            credentials = self._get_sts_temporary_credentials()
            s3_resource = boto3.resource(
                "s3",
                region_name=self._aws_resources["awsRegion"],
                aws_access_key_id=credentials["AccessKeyId"],
                aws_secret_access_key=credentials["SecretKey"],
                aws_session_token=credentials["SessionToken"],
            )
            self._s3_bucket_resource = s3_resource.Bucket(self._aws_resources["awsUserFilesS3Bucket"])
        return self._s3_bucket_resource

    def _get_sts_temporary_credentials(self) -> Mapping[str, Any]:
        """
        Get the STS temporary credentials, refreshing them if needed.

        Returns: The STS temporary credentials.

        """

        if self._cognito_identity_client is None:
            self._cognito_identity_client = boto3.client("cognito-identity", config=Config(region_name=self._aws_resources["awsRegion"]))
        # check if the credentials are expired
        if self._sts_credentials_expired():
            self._sts_credentials = None
        for i in range(12):
            # get new credentials if needed
            if self._sts_credentials is None:
                try:
                    logins = {f"""cognito-idp.{self._aws_resources['awsRegion']}.amazonaws.com/{self._aws_resources['awsUserPoolId']}""": self._get_id_token()}
                    # Get the identity ID associated with the Cognito access token.
                    response = self._cognito_identity_client.get_id(IdentityPoolId=self._aws_resources["awsCognitoIdentityPoolId"], Logins=logins)
                    identity_id = response["IdentityId"]
                    # Get temporary STS credentials for the identity ID.
                    response = self._cognito_identity_client.get_credentials_for_identity(IdentityId=identity_id, Logins=logins)
                    # Extract the temporary credentials.
                    self._sts_credentials = response["Credentials"]
                    self._sts_credentials["IdentityId"] = identity_id
                    break
                except Exception as ex:
                    # Handle rate limiting by backing off,
                    if "TooManyRequestsException" in str(ex):
                        if i <= 5:
                            logger.debug("Too many requests to Cognito, backing off.")
                            sleep(2 ** i)
                            continue
                        elif i < 12:
                            logger.warning("Too many requests to Cognito, backing off.")
                            sleep(2 ** i)
                            continue
                        else:
                            raise Exception("Too many requests to Cognito, please try again later.") from ex
                    # Handle any errors that may occur during the credential retrieval.
                    raise Exception("Failed to get temporary credentials for Chloris App") from ex
        return self._sts_credentials

    def _upload_file(
        self,
        key: str,
        body: Optional[str] = None,
        file_path: Optional[Union[str, os.PathLike]] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> None:
        """
        Upload a file to the user data bucket, either from disk (file_path) or from a string (body).

        Args:
            key: The path to the file in the protected space of the Chloris S3 bucket
            body: The string to upload
            file_path: The path to the file to upload

        Returns:
            None
        """
        if metadata is None:
            metadata = {}
        try:
            if body:
                self._get_s3_bucket_resource().put_object(Body=body, Key=key, Metadata=metadata)
            elif file_path:
                self._get_s3_bucket_resource().upload_file(file_path, key, ExtraArgs={"Metadata": metadata})
            else:
                raise ValueError("Either body or file_path must be provided")
        except Exception as ex: # retry once for expired token during long upload
            if "ExpiredToken" in str(ex):
                if body:
                    self._get_s3_bucket_resource().put_object(Body=body, Key=key, Metadata=metadata)
                elif file_path:
                    self._get_s3_bucket_resource().upload_file(file_path, key, ExtraArgs={"Metadata": metadata})
                else:
                    raise ValueError("Either body or file_path must be provided")


    def download_geojson_boundary(self, path):
        """
        Download a GeoJSON boundary from the user data bucket

        Args:
            path: The path to the file in the protected user space

        Returns:
            The GeoJSON content as a string
        """
        return self._get_s3_bucket_resource().Object(path).get()["Body"].read().decode("utf-8")

    def _get_object_metadata(self, key: str) -> Optional[Mapping[str, str]]:
        # type hint for the boto3 S3 object
        obj = self._get_s3_client().head_object(Bucket=self._aws_resources["awsUserFilesS3Bucket"], Key=key)
        return obj.get("Metadata")

    def _sts_credentials_expired(self):
        return self._sts_credentials is not None and datetime.now(timezone.utc) > self._sts_credentials.get("Expiration", 0) - timedelta(minutes=10)

    def _upload_boundary_remote_geojson(self, geojson_path: Union[str, os.PathLike], exclude_geometry_path: str = None) -> str:
        """
        Upload a geojson boundary to the Chloris S3 bucket from a remote server or S3 bucket, and wait for it to be normalized.

        If the boundary is a control site, we recommend you exclude the primary geometry's area
         by uploading it first, then passing the normalized result as `exclude_geometry_path`.

        Args:
            geojson_path: The geospatial boundary geojson, as a dictionary, local file path, or remote https url.
            exclude_geometry_path: The S3 path to a geometry to exclude from the boundary.

        Returns:
            The S3 path to the normalized boundary, to be used when submitting a new site.

        """
        if not isinstance(geojson_path, str):
            geojson_path = str(geojson_path)
        if geojson_path.startswith("http://"):
            raise ValueError("http urls not allowed when uploading from a remote server, please use https")

        if exclude_geometry_path and not exclude_geometry_path.startswith("s3://"):
            raise ValueError("exclude_geometry_path must be an previously normalized S3 path")
        upload_id = str(uuid.uuid4())  # generate random id for this upload
        # Use `POST /api/boundary` endpoint to submit the boundary for normalization.
        response = self._http_pool.request(
            "POST",
            self.api_endpoint + "boundary",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self._get_id_token(),
            },
            body=json.dumps(
                {
                    "organizationId": self.organization_id,
                    "uploadId": upload_id,
                    "uploadPath": geojson_path,
                    "excludeGeometryPath": exclude_geometry_path,
                }
            ),
        )
        if response.status != 200:
            raise Exception(f"Failed to submit boundary for normalization: {response.status} {response.data.decode('utf-8')}")

        # Poll S3 with exponential backoff up to 15 minutes for the boundary to be normalized
        boundary_path = self._wait_for_boundary_normalization(upload_id)
        if boundary_path is None:
            raise ValueError("Could not process your file in the time allowed, please simplify your boundary and try again.")
        return boundary_path


    def _upload_boundary_file(self, file: Union[str, os.PathLike], exclude_geometry_path: str = None) -> str:
        """
        Upload a geospatial boundary to the Chloris S3 bucket, and wait for it to be normalized.

          Compared to `_upload_boundary_remote_geojson()`, this function is more flexible in the types of files
          it can upload, but more applies stricter sparseness and complexity limits.

        Args:
            file: The geospatial boundary file to upload, for shapefile, just the path to the .shp.
            exclude_geometry_path: The S3 path to a geometry to exclude from the boundary.

        Returns:
            The S3 path to the normalized boundary, to be used when submitting a new site.

        Raises:
            ValueError: If there is an issue with the boundary
        """

        # Here are the steps we take to upload a boundary:
        # 1. Upload the boundary file(s) to the user data bucket under `apiUploads/`
        # 2. Call the `POST /api/boundary` endpoint to submit the boundary for normalization.
        # 2. Wait for the boundary to be normalized by polling S3 with exponential backoff up to 15 minutes.
        # 3. Return the path to the normalized boundary or, in the event that there was a
        #    specific issue with the boundary, the error message in the S3 metadata.
        # 4. (optional, after this function returns) Download the normalized boundary using
        #    `client.download_geojson_boundary()` and check that it matches your expectation.
        #    This is important because the normalization process may have changed the boundary in unexpected ways,
        #    as it attempts fix some common polygon issues and reading from certain
        #    formats (such as KML) can produce visual artifacts.

        if not isinstance(file, str):
            file = str(file)
        if file.endswith(".shp"):
            files = []
            # if the file is a shapefile, upload all the files in the shapefile
            for shp_ext in [".dbf", ".prj", ".shx"]:
                if os.path.exists(file.replace(".shp", shp_ext)):
                    files.append(file.replace(".shp", shp_ext))
            files.append(file)
        else:
            files = [file]

        # ensure that all the files exist
        for file in files:
            if not os.path.exists(file):
                raise ValueError(f"File does not exist: {file}")

        upload_id = str(uuid.uuid4())  # generate random id for this upload
        identity_id = self._get_sts_temporary_credentials()['IdentityId']

        # metadata just for traceability
        metadata = {"upload-id": upload_id, "organization-id": self.organization_id}

        upload_key = None
        for file in files:
            # split the file extensions (.aux.xml)
            file_ext = ".".join(os.path.basename(file).split(".")[1:])
            upload_key = f"private/{identity_id}/apiUploads/{upload_id}.{file_ext}"

            # upload the file
            self._upload_file(upload_key, file_path=file, metadata=metadata)

        # Initiate the normalization process
        response = self._http_pool.request(
            "POST",
            self.api_endpoint + "boundary",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self._get_id_token(),
            },
            body=json.dumps(
                {
                    "organizationId": self.organization_id,
                    "uploadId": upload_id,
                    "uploadPath": f"s3://{self._aws_resources['awsUserFilesS3Bucket']}/{upload_key}",
                    "excludeGeometryPath": exclude_geometry_path,
                }
            ),
        )

        if response.status != 200:
            raise Exception(f"Failed to initiate boundary normalization: {response.status} {response.data.decode('utf-8')}")

        boundary_path = self._wait_for_boundary_normalization(upload_id)
        if boundary_path is None:
            raise ValueError("Could not process your file in the time allowed, please simplify your boundary and try again.")
        return boundary_path

    def _wait_for_boundary_normalization(self, upload_id: str) -> Optional[str]:
        identity_id = self._get_sts_temporary_credentials()["IdentityId"]
        boundary_key = f"protected/{identity_id}/uploads/{upload_id}.geojson"
        # Poll S3 with exponential backoff up to 15 minutes for the boundary to be normalized
        i = 0
        time_remaining = 15 * 60  # 15 minutes
        while True:
            # check if the boundary has been normalized
            metadata = None
            try:
                metadata = self._get_object_metadata(boundary_key)
            except ClientError as ex:
                # ignore 404 and 403 errors, as they are expected until the boundary is normalized, re-raise any other errors
                if ex.response["Error"]["Code"] not in ["404", "403"]:
                    raise ex

            if metadata is not None:
                if metadata.get("error"):
                    raise ValueError(metadata["error"])
                # upload was successful
                return f"s3://{self._aws_resources['awsUserFilesS3Bucket']}/{boundary_key}"
            else:
                delay = 5 * (1.3 ** i)  # exponential backoff
                time_remaining -= delay
                if time_remaining <= 0:
                    break
                sleep(delay)

    def put_reporting_unit(self, reporting_unit_entry: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Create or update a reporting unit in the Chloris App.

        Args:
            reporting_unit_entry: The reporting unit entry to create or update.

        Returns: The new reporting unit entry.
        """
        # clone the reporting unit entry
        reporting_unit_entry = dict(reporting_unit_entry)
        # remove the downloads/stats/layersConfig fields since the API doesn't accept them
        reporting_unit_entry.pop("downloads", None)
        reporting_unit_entry.pop("stats", None)
        reporting_unit_entry.pop("layersConfig", None)
        response = self._http_pool.request(
            "PUT",
            self.api_endpoint + f"reportingUnit",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self._get_id_token(),
            },
            body=json.dumps(reporting_unit_entry),
        )
        if response.status != 200:
            raise Exception(f"Failed to create or update reporting unit: {response.status} {response.data.decode('utf-8')}")
        # return the reporting unit entry
        return json.loads(response.data.decode("utf-8"))

    def list_active_sites(self) -> Sequence[Mapping[str, Any]]:
        """
        List all active sites for the organization. This is a convenience function that filters the list of sites to only include active sites.

        Returns:
            A list of reporting unit entries.
        """
        # use POST /api/reportingUnit and nextToken to load all the sites
        sites = []
        next_token = None
        while True:
            response = self._http_pool.request(
                "POST",
                self.api_endpoint + f"reportingUnit",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + self._get_id_token(),
                },
                body=json.dumps({"organizationId": self.organization_id, "nextToken": next_token}),
            )
            if response.status != 200:
                raise Exception(f"Failed to list reporting units: {response.status} {response.data.decode('utf-8')}")
            response_json = json.loads(response.data.decode("utf-8"))
            for reporting_unit in response_json.get("reportingUnits", []):
                if reporting_unit.get("deletedAt") is None and reporting_unit.get("branchId") is None:
                    # Ensure "periodChangeStartYear" and "periodChangeEndYear" are integers
                    if isinstance(reporting_unit.get("periodChangeStartYear"), str):
                        reporting_unit["periodChangeStartYear"] = int(reporting_unit["periodChangeStartYear"])
                    if isinstance(reporting_unit.get("periodChangeEndYear"), str):
                        reporting_unit["periodChangeEndYear"] = int(reporting_unit["periodChangeEndYear"])

                    sites.append(reporting_unit)
            next_token = response_json.get("nextToken")
            if next_token is None:
                break

        return sites

    def get_reporting_unit(self, reporting_unit_id: str, include_stats=False, include_layers_config=False, include_downloads=False) -> Mapping[str, Any]:
        """
        Get a site with its control (if it has one). Optionally also retrieving all stats, layers config, and downloads index.

        Args:
            reporting_unit_id: The id of the site to get.
            include_stats: If True, also retrieve the stats for the site.
            include_layers_config: If True, also retrieve the layers config for the site.
            include_downloads: If True, also retrieve the downloads index for the site.

        Returns:
            The reporting unit entry like:
                {
                    "reportingUnitId": "string",
                    "label": "string",
                    "description": "string",
                    "tags": [ "string", ... ],
                    "createdAt": "string",
                    "updatedAt": "string",
                    "deletedAt": "string",
                    "controlReportingUnitId": {
                        "reportingUnitId": "string",
                        "label": "string",
                        # ...
                    },
                    "layersConfig": {
                        # ...
                    },
                    "downloads": {
                         # ...
                    }
                }
        """
        response = self._http_pool.request(
            "POST",
            self.api_endpoint + f"reportingUnit",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self._get_id_token(),
            },
            body=json.dumps({"organizationId": self.organization_id, "reportingUnitId": reporting_unit_id}),
        )
        if response.status != 200:
            raise Exception(f"Failed to get reporting unit: {response.status} {response.data.decode('utf-8')}")
        response_json = json.loads(response.data.decode("utf-8"))

        reporting_units = []
        for reporting_unit in response_json:
            # Ensure "periodChangeStartYear" and "periodChangeEndYear" are integers
            if isinstance(reporting_unit.get("periodChangeStartYear"), str):
                reporting_unit["periodChangeStartYear"] = int(reporting_unit["periodChangeStartYear"])
            if isinstance(reporting_unit.get("periodChangeEndYear"), str):
                reporting_unit["periodChangeEndYear"] = int(reporting_unit["periodChangeEndYear"])
            # retrieve optional data
            if include_stats:
                try:
                    stats = self.get_reporting_unit_stats(reporting_unit)
                    # merge stats into reporting unit (except for areaKm2, due to naming conflict)
                    reporting_unit = {**reporting_unit, **stats}
                except Exception:
                    # ignore errors getting stats
                    pass
            if include_layers_config:
                try:
                    reporting_unit["layersConfig"] = self.get_reporting_unit_layers_config(reporting_unit)
                except Exception:
                    # ignore errors getting layers config
                    pass
            if include_downloads:
                try:
                    reporting_unit["downloads"] = self.get_reporting_unit_downloads(reporting_unit)
                except Exception:
                    # ignore errors getting downloads
                    pass

            reporting_units.append(reporting_unit)

        # link up the control site
        reporting_unit = reporting_units[0]
        if len(reporting_units) > 1:
            reporting_unit["controlReportingUnit"] = reporting_units[1]

        return reporting_unit

    def get_reporting_unit_stats(self, reporting_unit_entry: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Get the stats for a site.

        Args:
            reporting_unit_entry: The site entry.

        Returns:
            The site stats.
        """
        if not (reporting_unit_entry.get("analysisCompletedAt") and reporting_unit_entry.get("qualityControlledAt")):
            raise ValueError("Analysis not completed")

        data_path = self._get_data_path(reporting_unit_entry)
        response = self._http_pool.request(
            "GET",
            data_path + "stats.json",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self._get_id_token(),
            },
        )
        if response.status != 200:
            raise Exception(f"Failed to get reporting unit stats: {response.status} {response.data.decode('utf-8')}")
        result = json.loads(response.data.decode("utf-8"))
        # Ensure "periodChangeStartYear" and "periodChangeEndYear" are integers
        if isinstance(result.get("periodChangeStartYear"), str):
            result["periodChangeStartYear"] = int(result["periodChangeStartYear"])
        if isinstance(result.get("periodChangeEndYear"), str):
            result["periodChangeEndYear"] = int(result["periodChangeEndYear"])
        # remove areaKm2 due to naming conflict with the reporting unit vector area
        result.pop("areaKm2", None)
        return result

    def _get_data_path(self, reporting_unit_entry: Mapping[str, Any]) -> str:
        data_path = reporting_unit_entry.get("dataPath")
        if data_path is None:
            versioned_reporting_unit_id = reporting_unit_entry['reportingUnitId']
            version_id = reporting_unit_entry.get("versionId")
            if version_id:
                versioned_reporting_unit_id = f"{versioned_reporting_unit_id}_{version_id}"
            data_path = '/'.join([self.data_path.rstrip('/'), reporting_unit_entry['organizationId'], versioned_reporting_unit_id, ''])
        else:
            data_path = data_path.rstrip("/") + "/"
        if data_path.startswith("s3://"):
            data_path = data_path.replace("s3://chloris-app-data/data/", self.data_path)
        return data_path

    def get_reporting_unit_layers_config(self, reporting_unit_entry: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Get the layers config for a site.

        Args:
            reporting_unit_entry: The site entry.

        Returns:
            The site layers config.
        """
        if not (reporting_unit_entry.get("analysisCompletedAt") and reporting_unit_entry.get("qualityControlledAt")):
            raise ValueError("Analysis not completed")

        data_path = self._get_data_path(reporting_unit_entry)
        response = self._http_pool.request(
            "GET",
            data_path + "layers.json",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self._get_id_token(),
            },
        )
        if response.status != 200:
            raise Exception(f"Failed to get reporting unit layers config: {response.status} {response.data.decode('utf-8')}")
        return json.loads(response.data.decode("utf-8"))

    def get_reporting_unit_downloads(self, reporting_unit_entry: Mapping[str, Any]) -> Optional[Mapping[str, Any]]:
        """
        Get the downloads index for a site, if available.

        Args:
            reporting_unit_entry: The site entry.

        Returns:
            The site downloads index or None if not available.
        """
        if not (
            reporting_unit_entry.get("analysisCompletedAt")
            and reporting_unit_entry.get("qualityControlledAt")
        ):
            # downloads not available, return early
            return None

        data_path = self._get_data_path(reporting_unit_entry)

        response = self._http_pool.request(
            "GET",
            data_path + "downloads.json",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self._get_id_token(),
            },
        )
        # parse the response, otherwise return None when downloads are not available
        if response.status != 200:
            return None
        try:
            return json.loads(response.data.decode("utf-8"))
        except json.JSONDecodeError:
            return None

    def submit_site(self,
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
                    **kwargs
                    ) -> Mapping[str, Any]:
        """A high-level function to submit a site to the Chloris App. Automatically chooses the best method to upload the boundary (geojson or S3 multipart upload).

        Args:
            label: The label for the site.
            tags: The tags for the site.
            description: The description for the site.
            boundary_path: The path to the boundary file to upload. Either a local file path or a https url to a geojson file on a remote server.
            control_boundary_path: The path to the control boundary file to upload. Either a local file path or a https url to a geojson file on a remote server.
            notify: Whether to send email notifications when the site is ready.
            period_change_start_year: The start of the period of interest
            period_change_end_year: The end of the period of interest (inclusive)
            resolution: The desired resolution of the outputs. Valid options are 30 and 10 (meters). Defaults to 30.
            forest_baseline_year: The year to use as the forest baseline year.

        Returns: The new reporting unit entry.
        """

        # First we upload the primary boundary, then the control boundary (if provided), then we submit the site.

        # these are the paths to the normalized boundaries
        _boundary_path = None
        _control_boundary_path = None

        if (
            boundary_path.startswith("http://") or
            (control_boundary_path is not None and control_boundary_path.startswith("http://"))
        ):
            raise ValueError("http urls not allowed when uploading from a remote server, please use https")

        if boundary_path.lower().startswith("https://"):
            _boundary_path = self._upload_boundary_remote_geojson(boundary_path)
        else:
            _boundary_path = self._upload_boundary_file(boundary_path)
        if control_boundary_path is not None:
            if control_boundary_path.lower().startswith("https://"):
                if control_boundary_path.lower().endswith(".geojson") or control_boundary_path.lower().endswith(".json"):
                    _control_boundary_path = control_boundary_path
                else:
                    raise ValueError("Only geojson files are supported when submitting sites from a remote url")
            else:
                if boundary_path.lower().startswith("https://"):
                    _control_boundary_path = self._upload_boundary_remote_geojson(control_boundary_path, exclude_geometry_path=_boundary_path)
                else:
                    _control_boundary_path = self._upload_boundary_file(control_boundary_path, exclude_geometry_path=_boundary_path)

        # ensure we have uploaded the boundaries appropriately
        if _boundary_path is None:
            raise ValueError("Failed to upload boundary")
        if control_boundary_path is not None and _control_boundary_path is None:
            raise ValueError("Failed to upload control boundary")

        return self.put_reporting_unit(
            {
                "organizationId": self.organization_id,
                "label": label,
                "description": description,
                "tags": tags,
                "boundaryPath": _boundary_path,
                "controlBoundaryPath": _control_boundary_path,
                "notify": notify,
                "periodChangeStartYear": period_change_start_year,
                "periodChangeEndYear": period_change_end_year,
                "resolution": resolution,
                "forestBaselineYear": forest_baseline_year,
                **kwargs
            }
        )
