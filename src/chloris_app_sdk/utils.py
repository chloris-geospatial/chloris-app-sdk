""" General utility functions. """
import base64
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping, Optional


def is_token_expired(token: str, expiration_tolerance: int = 10) -> bool:
    """Check if a JWT token is expired without validating it.

    Args:
        token (str): The JWT token to check.
        expiration_tolerance (int, optional): The number of minutes before the token expires to consider it expired. Defaults to 10.

    Returns:
        bool: True if the token is expired, False otherwise.
    """
    try:
        # Decode the JWT payload.
        payload = decode_jwt(token)

        # Extract the 'exp' claim from the payload (expiration timestamp in seconds).
        exp_timestamp = payload.get("exp")

        if exp_timestamp is None:
            return True
        # Check if the token will expire in the next 10 minutes.
        return datetime.now(tz=timezone.utc) >= (datetime.fromtimestamp(exp_timestamp, tz=timezone.utc) - timedelta(minutes=expiration_tolerance))
    except Exception as ex:
        return True


def decode_jwt(token: str) -> Mapping[str, Any]:
    """Decode a JWT token without validating it and return the payload as a dictionary.

    Args:
        token (str): The JWT token to decode.

    Returns:
        Mapping[str, Any]: The decoded payload as a dictionary.
    """
    # extract and decode the payload from the token
    payload = token.split(".")[1]
    decoded_payload = base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)).decode("utf-8")

    # Parse the decoded payload as JSON and return it.
    return json.loads(decoded_payload)


def to_tco2e(x: Optional[float]) -> Optional[float]:
    """Convert tons of biomass to CO2 equivalent tons.

    Args:
        x (float): Tons biomass

    Returns:
        float: Tons CO2 equivalent
    """
    if x is None:
        return None
    # woody biomass has a carbon content of 50%, but when burned that carbon
    # binds to oxygen to form CO2, so we need to multiply by 44/12 to get the
    # CO2 equivalent.
    return x * 0.5 * (44 / 12)

def to_legacy_layers_config(layers_config):
    layers_list = layers_config.get('annualLayers', [])
    layers_dict = dict()
    for product_type, product_variant_template in (
            ("stock", "dynamic-{resolution}m"),
            ("stock", "static-{resolution}m"),
            ("forest", "dynamic-{resolution}m"),
            ("forest", "static-{resolution}m"),
            ("change", "dynamic-{resolution}m-user-period"),
            ("change", "static-{resolution}m-user-period"),
            ("cumulative_change", "dynamic-{resolution}m-user-period"),
            ("cumulative_change", "static-{resolution}m-user-period"),
            ("forest_area_loss", "dynamic-{resolution}m-user-period"),
            ("forest_area_loss", "static-{resolution}m-user-period"),
            ("forest_area_gain", "dynamic-{resolution}m-user-period"),
            ("forest_area_gain", "static-{resolution}m-user-period"),
            ("forest_area_degradation", "dynamic-{resolution}m-user-period"),
            ("forest_area_degradation", "static-{resolution}m-user-period"),
    ):
        for resolution in (10, 30):
            product_variant = product_variant_template.format(resolution=resolution)
            for _layer in layers_list:
                if (_layer.get('productType') == product_type and
                        _layer.get('resolution') == resolution and
                        _layer.get('carbonPool') == "agb"):
                    layers_dict.setdefault(product_type,{})[product_variant] = _layer
    return layers_dict