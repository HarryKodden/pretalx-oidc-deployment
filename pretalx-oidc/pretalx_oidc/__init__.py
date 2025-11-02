# SPDX-FileCopyrightText: 2025-present Your Name
# SPDX-License-Identifier: Apache-2.0

# Manual signal registration version - with auto-discovery support

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

print("[OIDC __init__] Module is being imported!")


class PretalxOIDCPlugin(AppConfig):
    """Plugin to add OIDC authentication to pretalx."""

    name = "pretalx_oidc"
    verbose_name = "Pretalx OIDC Authentication"

    class PretalxPluginMeta:
        name = "Pretalx OIDC"
        author = "Your Name"
        description = "OIDC authentication plugin for Pretalx"
        visible = True
        version = "1.0.0"

    def ready(self):
        """Import signal handlers when the app is ready."""
        print("[OIDC __init__] Module is being imported!")
        print("[OIDC __init__] ready() is being called!")
        
        # Import the signal first
        from pretalx.common.signals import auth_html
        print(f"[OIDC __init__] Imported auth_html signal: {auth_html}")
        
        # Import signal handler
        from .signals import add_oidc_login_button
        print("[OIDC __init__] Imported signal handler function!")
        
        # Manually connect the signal
        auth_html.connect(add_oidc_login_button)
        print(f"[OIDC __init__] Manually connected signal handler!")
        print(f"[OIDC __init__] Signal receivers: {auth_html.receivers}")

        # Register context processor
        from django.conf import settings

        context_processor = "pretalx_oidc.context_processors.oidc_auth_context"
        if context_processor not in settings.TEMPLATES[0]["OPTIONS"]["context_processors"]:
            settings.TEMPLATES[0]["OPTIONS"]["context_processors"].append(
                context_processor
            )
            print(f"[OIDC __init__] Registered context processor: {context_processor}")

        # Configure OIDC settings from pretalx.cfg
        from .config import configure_oidc_settings
        configure_oidc_settings()

        print("[OIDC __init__] Done with ready()!")
