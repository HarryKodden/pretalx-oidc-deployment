# SPDX-FileCopyrightText: 2025-present Harry Kodden
# SPDX-License-Identifier: Apache-2.0

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PretalxOIDCPlugin(AppConfig):
    """Plugin to add OIDC authentication to pretalx."""

    name = "pretalx_oidc"
    verbose_name = _("Pretalx OIDC Authentication")

    class PretalxPluginMeta:
        name = _("Pretalx OIDC")
        author = "Harry Kodden"
        description = _("OpenID Connect (OIDC) authentication plugin for Pretalx")
        visible = True
        version = "1.0.0"
        category = "INTEGRATION"

    def ready(self):
        """Import signal handlers when the app is ready."""
        # Import signals - the @receiver decorator will auto-register them
        from . import signals  # noqa

        # Configure OIDC settings from pretalx.cfg
        from .config import configure_oidc_settings
        configure_oidc_settings()
