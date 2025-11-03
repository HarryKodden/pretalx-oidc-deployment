# SPDX-FileCopyrightText: 2025-present Harry Kodden
# SPDX-License-Identifier: Apache-2.0

import logging

from django.conf import settings
from django.dispatch import receiver
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)
logger.warning("OIDC signals module is being loaded!")

# Import the signal
from pretalx.common.signals import auth_html
logger.warning(f"Successfully imported auth_html signal: {auth_html}")


@receiver(auth_html)
def add_oidc_login_button(sender, request, next_url=None, **kwargs):
    """Add OIDC login button to the authentication page."""
    logger.warning(f"[OIDC SIGNAL CALLED] sender={sender}, path={request.path if request else 'NO REQUEST'}")
    try:
        login_url = reverse("plugins:pretalx_oidc:oidc_authentication_init")

        if next_url:
            login_url = f"{login_url}?next={next_url}"

        # Get provider name from settings, fallback to "OIDC" if not set
        provider_name = getattr(settings, 'OIDC_PROVIDER_NAME', 'OIDC')
        button_text = _("Sign in with {provider}").format(provider=provider_name)

        button_html = f"""
    <div class="auth-form-block w-100">
        <a class="btn btn-lg btn-primary btn-block" href="{login_url}">
            <i class="fa fa-sign-in"></i> {button_text}
        </a>
    </div>
    """

        logger.warning(f"[OIDC] Returning button HTML (length={len(button_html)})")
        return mark_safe(button_html)
    except Exception as e:
        logger.error(f"[OIDC] Error in signal handler: {e}", exc_info=True)
        return ""


logger.warning(f"OIDC signal handler registered: {add_oidc_login_button}")
