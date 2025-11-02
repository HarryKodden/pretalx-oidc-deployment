# SPDX-FileCopyrightText: 2025-present Your Name
# SPDX-License-Identifier: Apache-2.0

import logging
from django.conf import settings
from django.contrib.auth import login
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
        # Store the next URL in session
        next_url = request.GET.get("next", "")
        if next_url:
            request.session["oidc_login_next"] = next_url
        return super().get(request)


class PretalxOIDCAuthenticationCallbackView(OIDCAuthenticationCallbackView):
    """Custom OIDC callback view for pretalx."""

    @property
    def success_url(self):
        """Return the URL to redirect to after successful authentication."""
        logger.warning(f"[OIDC View] success_url property called! User: {self.user}")
        
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

        logger.warning(f"[OIDC View] Redirecting to: {next_url}")
        return next_url

    @property
    def failure_url(self):
        """Return the URL to redirect to after failed authentication."""
        logger.error("[OIDC View] failure_url property called!")
        # Redirect to login page with error
        return reverse("orga:login") + "?oidc_error=1"
