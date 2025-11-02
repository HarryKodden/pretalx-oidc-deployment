# SPDX-FileCopyrightText: 2025-present Your Name
# SPDX-License-Identifier: Apache-2.0

from django.db import models
from django.utils.translation import gettext_lazy as _


class OIDCUserProfile(models.Model):
    """Stores OIDC-specific user data."""

    user = models.OneToOneField(
        "person.User",
        on_delete=models.CASCADE,
        related_name="oidc_profile",
    )
    oidc_id = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("OIDC ID"),
        help_text=_("The unique identifier from the OIDC provider"),
    )
    provider = models.CharField(
        max_length=100,
        default="oidc",
        verbose_name=_("OIDC Provider"),
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("OIDC User Profile")
        verbose_name_plural = _("OIDC User Profiles")

    def __str__(self):
        return f"{self.user.email} - {self.provider}"
