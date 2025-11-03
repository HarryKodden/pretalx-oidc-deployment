# SPDX-FileCopyrightText: 2025-present Harry Kodden
# SPDX-License-Identifier: Apache-2.0

import logging
from django.conf import settings
from django.contrib.auth import login
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from pretalx.person.models import User

from .models import OIDCUserProfile

logger = logging.getLogger(__name__)
logger.warning("[OIDC Auth] auth.py module loaded - PretalxOIDCBackend class defined")


class PretalxOIDCBackend(OIDCAuthenticationBackend):
    """Custom OIDC authentication backend for pretalx."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.warning(f"[OIDC Auth] PretalxOIDCBackend instance created")

    def _is_admin_user(self, claims):
        """Check if user should have admin privileges based on claims."""
        from pretalx.common.settings.config import build_config
        config, _ = build_config()
        
        # Get admin users from config (comma-separated list)
        admin_users_str = config.get('oidc', 'admin_users', fallback='')
        if not admin_users_str:
            return False
        
        # Parse comma-separated list and strip whitespace
        admin_identifiers = [x.strip() for x in admin_users_str.split(',') if x.strip()]
        
        # Check if user's sub or email matches any admin identifier
        oidc_sub = claims.get('sub', '')
        email = claims.get('email', '')
        
        is_admin = oidc_sub in admin_identifiers or email in admin_identifiers
        
        if is_admin:
            logger.warning(f"[OIDC Auth] User matches admin identifier: sub={oidc_sub}, email={email}")
        
        return is_admin

    def create_user(self, claims):
        """Create a new user from OIDC claims."""
        logger.warning(f"[OIDC Auth] create_user() called with claims: {claims}")
        
        email = claims.get("email")
        if not email:
            logger.error("[OIDC Auth] No email in claims, cannot create user")
            return None

        # Check if user should be admin
        is_admin = self._is_admin_user(claims)

        # Create user with random password (OIDC-only authentication)
        user = User.objects.create_user(
            email=email,
            name=claims.get("name", "") or claims.get("preferred_username", ""),
        )
        
        # Set admin privileges if configured
        if is_admin:
            user.is_staff = True
            user.is_superuser = True
            user.save(update_fields=["is_staff", "is_superuser"])
            logger.warning(f"[OIDC Auth] Granted admin privileges to user: {user.email}")
        
        logger.warning(f"[OIDC Auth] Created user: {user.email} (id={user.pk}, admin={is_admin})")

        # Store OIDC ID
        oidc_profile = OIDCUserProfile.objects.create(
            user=user,
            oidc_id=claims.get("sub"),
            provider=getattr(settings, "OIDC_PROVIDER_NAME", "oidc"),
        )
        
        logger.warning(f"[OIDC Auth] Created OIDC profile for user {user.email} with sub={claims.get('sub')}")

        return user

    def update_user(self, user, claims):
        """Update existing user from OIDC claims."""
        logger.info(f"[OIDC Auth] Updating user {user.email} from claims: {claims}")
        
        # Update name if provided
        name = claims.get("name", "") or claims.get("preferred_username", "")
        if name and name != user.name:
            logger.info(f"[OIDC Auth] Updating user name from '{user.name}' to '{name}'")
            user.name = name
            user.save(update_fields=["name"])

        # Check and update admin status
        is_admin = self._is_admin_user(claims)
        if is_admin and not (user.is_staff and user.is_superuser):
            user.is_staff = True
            user.is_superuser = True
            user.save(update_fields=["is_staff", "is_superuser"])
            logger.warning(f"[OIDC Auth] Granted admin privileges to existing user: {user.email}")
        elif not is_admin and (user.is_staff or user.is_superuser):
            # Optionally revoke admin if no longer in admin list
            user.is_staff = False
            user.is_superuser = False
            user.save(update_fields=["is_staff", "is_superuser"])
            logger.warning(f"[OIDC Auth] Revoked admin privileges from user: {user.email}")

        return user

    def filter_users_by_claims(self, claims):
        """Return users matching the OIDC claims."""
        oidc_id = claims.get("sub")
        logger.info(f"[OIDC Auth] Filtering users by claims. sub={oidc_id}, email={claims.get('email')}")
        
        if not oidc_id:
            logger.error("[OIDC Auth] No 'sub' claim found")
            return User.objects.none()

        # Try to find user by OIDC ID
        try:
            profile = OIDCUserProfile.objects.select_related("user").get(
                oidc_id=oidc_id
            )
            logger.info(f"[OIDC Auth] Found existing user by OIDC ID: {profile.user.email}")
            return User.objects.filter(pk=profile.user.pk)
        except OIDCUserProfile.DoesNotExist:
            logger.info(f"[OIDC Auth] No existing OIDC profile found for sub={oidc_id}")
            
            # Try to find by email and link the account
            email = claims.get("email")
            if email:
                users = User.objects.filter(email__iexact=email)
                if users.exists():
                    # Link existing account to OIDC
                    user = users.first()
                    logger.info(f"[OIDC Auth] Linking existing user {user.email} to OIDC")
                    OIDCUserProfile.objects.create(
                        user=user,
                        oidc_id=oidc_id,
                        provider=getattr(settings, "OIDC_PROVIDER_NAME", "oidc"),
                    )
                    return User.objects.filter(pk=user.pk)

            logger.info("[OIDC Auth] No existing user found, will create new user")
            return User.objects.none()

    def authenticate(self, request, **kwargs):
        """Override to handle pretalx-specific authentication."""
        logger.info(f"[OIDC Auth] authenticate() called with kwargs: {kwargs.keys()}")
        
        user = super().authenticate(request, **kwargs)
        
        if user:
            logger.warning(f"[OIDC Auth] Authentication successful for user: {user.email}")
            logger.warning(f"[OIDC Auth]   - user.pk = {user.pk}")
            logger.warning(f"[OIDC Auth]   - user.is_active = {user.is_active}")
            logger.warning(f"[OIDC Auth]   - user.is_authenticated = {user.is_authenticated}")
            if request:
                # Log the authentication
                user.log_action(
                    "pretalx.user.oidc.login",
                    data={"provider": getattr(settings, "OIDC_PROVIDER_NAME", "oidc")},
                )
        else:
            logger.warning("[OIDC Auth] Authentication failed - no user returned")
        
        return user
