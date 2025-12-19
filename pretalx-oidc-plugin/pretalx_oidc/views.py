# SPDX-FileCopyrightText: 2025-present Harry Kodden
# SPDX-License-Identifier: Apache-2.0

import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from mozilla_django_oidc.views import (
    OIDCAuthenticationCallbackView,
    OIDCAuthenticationRequestView,
)

logger = logging.getLogger(__name__)


class PretalxOIDCAuthenticationRequestView(OIDCAuthenticationRequestView):
    """Custom OIDC login initiation view for pretalx."""

    def get(self, request):
        """Override get method to enforce HTTPS redirect URIs."""
        logger.info("[OIDC] Processing authentication request")

        # Call parent get method to get the response
        response = super().get(request)

        # Check if HTTPS redirect enforcement is enabled
        force_https = getattr(settings, "OIDC_FORCE_HTTPS_REDIRECT", False)

        # If it's a redirect response and HTTPS enforcement is enabled
        if force_https and hasattr(response, "url"):
            original_url = response.url

            # Check if URL contains HTTP redirect_uri and replace with HTTPS
            if "redirect_uri=http%3A%2F%2F" in original_url:
                modified_url = original_url.replace(
                    "redirect_uri=http%3A%2F%2F", "redirect_uri=https%3A%2F%2F"
                )
                response = HttpResponseRedirect(modified_url)
                logger.info("[OIDC] Enforced HTTPS redirect URI")

        return response


class PretalxOIDCAuthenticationCallbackView(OIDCAuthenticationCallbackView):
    """Custom OIDC callback view for pretalx."""

    @property
    def success_url(self):
        """Return the URL to redirect to after successful authentication."""
        logger.info("[OIDC] Authentication successful, determining redirect URL")

        # Get the stored next URL
        next_url = self.request.session.pop("oidc_login_next", None)

        # Default fallback URLs
        if not next_url:
            if hasattr(self.request, "event"):
                # If we're in an event context, redirect to event page
                next_url = self.request.event.urls.base
            else:
                # Otherwise go to organizer dashboard or event list
                next_url = reverse("orga:event.list")

        logger.info(f"[OIDC] Redirecting to: {next_url}")
        return next_url

    @property
    def failure_url(self):
        """Return the URL to redirect to after failed authentication."""
        logger.error("[OIDC] Authentication failed")
        # Redirect to login page with error
        return reverse("orga:login") + "?oidc_error=1"
