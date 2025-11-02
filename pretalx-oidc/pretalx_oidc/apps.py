# SPDX-FileCopyrightText: 2025-present Your Name
# SPDX-License-Identifier: Apache-2.0

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

print("[OIDC] apps.py module is being imported!")


class PretalxOIDCPlugin(AppConfig):
    name = "pretalx_oidc"
    verbose_name = _("OIDC Authentication")

    class PretalxPluginMeta:
        name = _("OIDC Authentication")
        author = "Your Name"
        description = _("Provides OpenID Connect authentication for pretalx")
        visible = True
        version = "1.0.0"
        category = "FEATURE"

    def ready(self):
        try:
            print("="*80)
            print("[OIDC APPS.PY] ready() is being called!")
            print("="*80)
            from .signals import add_oidc_login_button  # noqa: F401
            from .config import configure_oidc_settings
            
            print("[OIDC APPS.PY] Imported signals!")
            
            # Configure OIDC settings from pretalx.cfg
            configure_oidc_settings()
            
            print("[OIDC APPS.PY] Done with ready()!")
        except Exception as e:
            print(f"[OIDC] ERROR in ready(): {e}")
            import traceback
            traceback.print_exc()
            raise
