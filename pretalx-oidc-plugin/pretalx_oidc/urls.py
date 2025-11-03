# SPDX-FileCopyrightText: 2025-present Harry Kodden
# SPDX-License-Identifier: Apache-2.0

from django.urls import path

from .views import (
    PretalxOIDCAuthenticationCallbackView,
    PretalxOIDCAuthenticationRequestView,
)

app_name = "pretalx_oidc"

urlpatterns = [
    path(
        "oidc/authenticate/",
        PretalxOIDCAuthenticationRequestView.as_view(),
        name="oidc_authentication_init",
    ),
    path(
        "oidc/callback/",
        PretalxOIDCAuthenticationCallbackView.as_view(),
        name="oidc_authentication_callback",
    ),
]
