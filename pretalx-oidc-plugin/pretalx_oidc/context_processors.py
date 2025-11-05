# SPDX-FileCopyrightText: 2025-present Harry Kodden
# SPDX-License-Identifier: Apache-2.0

"""
Context processor to provide OIDC authentication status to templates.
"""
from django.conf import settings


def oidc_auth_context(request):
    """
    Add OIDC authentication status to template context.

    Checks if OIDC-only mode is enabled via the hide_password_form setting.
    When set to True in pretalx.cfg [oidc] section, password login/register
    forms will be hidden, leaving only the OIDC button.

    Returns:
        dict: Context variables for templates
            - oidc_only_auth: True if hide_password_form setting is enabled
            - has_password_auth: True if ModelBackend is enabled
            - has_oidc_auth: True if any OIDC backend is configured
    """
    # Get the config object from Django settings
    # The config object is set in settings.py from build_config()
    from pretalx.common.settings.config import build_config

    config, _ = build_config()

    # Check if hide_password_form is explicitly set to True in config
    hide_password = config.getboolean("oidc", "hide_password_form", fallback=False)

    auth_backends = getattr(settings, "AUTHENTICATION_BACKENDS", [])
    has_oidc = any("oidc" in backend.lower() for backend in auth_backends)
    has_password = "django.contrib.auth.backends.ModelBackend" in auth_backends

    return {
        "oidc_only_auth": hide_password and has_oidc,
        "oidc_hide_password_auth": hide_password,  # Used in templates to hide password forms
        "has_password_auth": has_password,
        "has_oidc_auth": has_oidc,
    }
