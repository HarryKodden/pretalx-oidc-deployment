# SPDX-FileCopyrightText: 2025-present Harry Kodden
# SPDX-License-Identifier: Apache-2.0

"""
Configuration utilities for reading OIDC settings from pretalx.cfg
Supports auto-discovery and manual endpoint configuration
Version: 2.0 with backend verification
"""

import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def discover_oidc_endpoints(discovery_url):
    """
    Fetch OIDC configuration from the well-known discovery endpoint.

    Args:
        discovery_url: URL to the OIDC discovery endpoint or base issuer URL.
                      Will automatically append /.well-known/openid-configuration
                      if not already present.

    Returns:
        dict: Dictionary containing the discovered endpoints, or None on error
    """
    # Normalize the discovery URL
    if not discovery_url.endswith("/.well-known/openid-configuration"):
        # Remove trailing slash if present
        discovery_url = discovery_url.rstrip("/")
        # Add well-known path
        discovery_url = f"{discovery_url}/.well-known/openid-configuration"

    try:
        logger.info(f"[OIDC] Fetching discovery document from: {discovery_url}")
        response = requests.get(discovery_url, timeout=10)
        response.raise_for_status()

        discovery_doc = response.json()

        endpoints = {
            "authorization_endpoint": discovery_doc.get("authorization_endpoint"),
            "token_endpoint": discovery_doc.get("token_endpoint"),
            "userinfo_endpoint": discovery_doc.get("userinfo_endpoint"),
            "jwks_uri": discovery_doc.get("jwks_uri"),
            "issuer": discovery_doc.get("issuer"),
        }

        # Validate that we got all required endpoints
        missing = [k for k, v in endpoints.items() if not v and k != "issuer"]
        if missing:
            logger.error(
                f"[OIDC] Discovery document missing required endpoints: {missing}"
            )
            return None

        logger.info(
            f"[OIDC] Successfully discovered endpoints from {endpoints.get('issuer', 'provider')}"
        )
        logger.info(f"  - Authorization: {endpoints['authorization_endpoint']}")
        logger.info(f"  - Token: {endpoints['token_endpoint']}")
        logger.info(f"  - UserInfo: {endpoints['userinfo_endpoint']}")
        logger.info(f"  - JWKS: {endpoints['jwks_uri']}")

        return endpoints

    except requests.RequestException as e:
        logger.error(
            f"[OIDC] Failed to fetch discovery document from {discovery_url}: {e}"
        )
        return None
    except (KeyError, ValueError) as e:
        logger.error(f"[OIDC] Invalid discovery document format: {e}")
        return None


def get_oidc_config(key, default=None):
    """
    Get OIDC configuration from pretalx config.
    Falls back to Django settings if not in config file.
    """
    try:
        from pretalx.settings import config
    except (ImportError, Exception):
        # If we can't import config, just use Django settings
        setting_name = f"OIDC_{key.upper()}"
        return getattr(settings, setting_name, default)

    # Map config keys to setting names
    config_mapping = {
        "rp_client_id": "OIDC_RP_CLIENT_ID",
        "rp_client_secret": "OIDC_RP_CLIENT_SECRET",
        "op_authorization_endpoint": "OIDC_OP_AUTHORIZATION_ENDPOINT",
        "op_token_endpoint": "OIDC_OP_TOKEN_ENDPOINT",
        "op_user_endpoint": "OIDC_OP_USER_ENDPOINT",
        "op_jwks_endpoint": "OIDC_OP_JWKS_ENDPOINT",
        "op_discovery_endpoint": "OIDC_OP_DISCOVERY_ENDPOINT",
        "provider_name": "OIDC_PROVIDER_NAME",
        "rp_sign_algo": "OIDC_RP_SIGN_ALGO",
        "rp_scopes": "OIDC_RP_SCOPES",
    }

    setting_name = config_mapping.get(key, f"OIDC_{key.upper()}")

    # Try to get from config file first
    try:
        value = config.get("oidc", key)
        if value:
            return value
    except (KeyError, AttributeError):
        pass

    # Fall back to Django settings
    return getattr(settings, setting_name, default)


# This will be called from the AppConfig.ready() method
def configure_oidc_settings():  # noqa: C901
    """
    Configure django-oidc settings from pretalx.cfg.
    Supports both auto-discovery and manual endpoint configuration.
    """
    from django.conf import settings as django_settings
    from pretalx.common.settings.config import build_config

    config, _ = build_config()

    # Check if OIDC section exists in config
    if not config.has_section("oidc"):
        logger.info("[OIDC] No [oidc] section found in pretalx.cfg")
        return

    logger.info("[OIDC] Configuring OIDC settings from pretalx.cfg")

    # Basic OIDC settings (always required)
    rp_client_id = config.get("oidc", "rp_client_id", fallback="")
    rp_client_secret = config.get("oidc", "rp_client_secret", fallback="")

    if not rp_client_id or not rp_client_secret:
        logger.warning("[OIDC] Missing rp_client_id or rp_client_secret in config")
        return

    setattr(django_settings, "OIDC_RP_CLIENT_ID", rp_client_id)
    setattr(django_settings, "OIDC_RP_CLIENT_SECRET", rp_client_secret)

    # Check for discovery URL first (preferred method)
    discovery_url = config.get("oidc", "op_discovery_endpoint", fallback=None)

    if discovery_url:
        # Use auto-discovery
        logger.info(f"[OIDC] Using auto-discovery from: {discovery_url}")

        endpoints = discover_oidc_endpoints(discovery_url)

        if endpoints:
            setattr(
                django_settings,
                "OIDC_OP_AUTHORIZATION_ENDPOINT",
                endpoints["authorization_endpoint"],
            )
            setattr(
                django_settings, "OIDC_OP_TOKEN_ENDPOINT", endpoints["token_endpoint"]
            )
            setattr(
                django_settings, "OIDC_OP_USER_ENDPOINT", endpoints["userinfo_endpoint"]
            )
            setattr(django_settings, "OIDC_OP_JWKS_ENDPOINT", endpoints["jwks_uri"])

            # Store issuer for validation if needed
            if endpoints.get("issuer"):
                setattr(django_settings, "OIDC_OP_ISSUER", endpoints["issuer"])
        else:
            logger.error(
                "[OIDC] Discovery failed, falling back to manual configuration if available"
            )
            # Try manual configuration as fallback
            discovery_url = None

    if not discovery_url:
        # Use manual endpoint configuration
        logger.info("[OIDC] Using manual endpoint configuration")

        oidc_config_mapping = {
            "op_authorization_endpoint": "OIDC_OP_AUTHORIZATION_ENDPOINT",
            "op_token_endpoint": "OIDC_OP_TOKEN_ENDPOINT",
            "op_user_endpoint": "OIDC_OP_USER_ENDPOINT",
            "op_jwks_endpoint": "OIDC_OP_JWKS_ENDPOINT",
        }

        for config_key, setting_name in oidc_config_mapping.items():
            value = config.get("oidc", config_key, fallback="")
            if value:
                setattr(django_settings, setting_name, value)
            else:
                logger.warning(f"[OIDC] Missing {config_key} in config")

    # Additional OIDC settings with defaults
    setattr(
        django_settings,
        "OIDC_RP_SIGN_ALGO",
        config.get("oidc", "rp_sign_algo", fallback="RS256"),
    )
    setattr(
        django_settings,
        "OIDC_RP_SCOPES",
        config.get("oidc", "rp_scopes", fallback="openid email profile"),
    )

    # Session/Auth settings
    setattr(
        django_settings,
        "OIDC_STORE_ACCESS_TOKEN",
        config.getboolean("oidc", "store_access_token", fallback=True),
    )
    setattr(
        django_settings,
        "OIDC_STORE_ID_TOKEN",
        config.getboolean("oidc", "store_id_token", fallback=True),
    )
    setattr(
        django_settings,
        "OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS",
        config.getint("oidc", "renew_id_token_expiry_seconds", fallback=3600),
    )

    # User creation settings - CRITICAL for auto-creating users
    setattr(
        django_settings,
        "OIDC_CREATE_USER",
        config.getboolean("oidc", "create_user", fallback=True),
    )
    setattr(
        django_settings,
        "OIDC_USE_NONCE",
        config.getboolean("oidc", "use_nonce", fallback=True),
    )

    # Callback URL configuration
    setattr(
        django_settings,
        "LOGIN_REDIRECT_URL",
        config.get("oidc", "login_redirect_url", fallback="/orga/"),
    )
    setattr(
        django_settings,
        "LOGOUT_REDIRECT_URL",
        config.get("oidc", "logout_redirect_url", fallback="/"),
    )

    # Tell mozilla-django-oidc the namespaced URL names for our plugin
    setattr(
        django_settings,
        "OIDC_AUTHENTICATION_CALLBACK_URL",
        "plugins:pretalx_oidc:oidc_authentication_callback",
    )
    setattr(
        django_settings,
        "OIDC_AUTHENTICATION_REQUEST_URL",
        "plugins:pretalx_oidc:oidc_authentication_init",
    )

    # CRITICAL: Tell mozilla-django-oidc which authentication backend class to use
    # Without this, it won't know to use our custom backend!
    setattr(
        django_settings,
        "OIDC_AUTHENTICATION_BACKEND",
        "pretalx_oidc.auth.PretalxOIDCBackend",
    )

    # Optional: Provider name for logging/display
    setattr(
        django_settings,
        "OIDC_PROVIDER_NAME",
        config.get("oidc", "provider_name", fallback="OIDC"),
    )

    # HTTPS redirect enforcement
    setattr(
        django_settings,
        "OIDC_FORCE_HTTPS_REDIRECT",
        config.getboolean("oidc", "force_https_redirect", fallback=False),
    )

    logger.info("[OIDC] Configuration complete:")
    logger.info(f"  - Client ID: {django_settings.OIDC_RP_CLIENT_ID}")
    logger.info(f"  - Provider: {django_settings.OIDC_PROVIDER_NAME}")
    logger.info(
        f"  - Request URL name: {django_settings.OIDC_AUTHENTICATION_REQUEST_URL}"
    )
    logger.info(
        f"  - Callback URL name: {django_settings.OIDC_AUTHENTICATION_CALLBACK_URL}"
    )
    logger.info(
        f"  - Auth Backend Class: {django_settings.OIDC_AUTHENTICATION_BACKEND}"
    )
    logger.info(f"  - Create User: {django_settings.OIDC_CREATE_USER}")

    # Log the authentication backends to verify our backend is included
    auth_backends = getattr(django_settings, "AUTHENTICATION_BACKENDS", [])
    logger.info(f"  - Configured Auth Backends ({len(auth_backends)}):")
    for backend in auth_backends:
        logger.info(f"      - {backend}")

    if hasattr(django_settings, "OIDC_OP_AUTHORIZATION_ENDPOINT"):
        logger.info(
            f"  - Authorization: {django_settings.OIDC_OP_AUTHORIZATION_ENDPOINT}"
        )
    if hasattr(django_settings, "OIDC_OP_TOKEN_ENDPOINT"):
        logger.info(f"  - Token: {django_settings.OIDC_OP_TOKEN_ENDPOINT}")
