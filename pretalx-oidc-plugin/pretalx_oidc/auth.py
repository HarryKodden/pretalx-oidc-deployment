# SPDX-FileCopyrightText: 2025-present Harry Kodden
# SPDX-License-Identifier: Apache-2.0

import logging

from django.conf import settings
from django.urls import reverse
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from mozilla_django_oidc.utils import absolutify
from pretalx.person.models import User

from .models import OIDCUserProfile

logger = logging.getLogger(__name__)

logger.warning("[OIDC Auth] auth.py module loaded - PretalxOIDCBackend class defined")


class PretalxOIDCBackend(OIDCAuthenticationBackend):
    """Custom OIDC authentication backend for pretalx."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.warning("[OIDC Auth] PretalxOIDCBackend instance created")

    def _is_admin_user(self, claims):
        """Check if user should have admin privileges based on claims."""
        from pretalx.common.settings.config import build_config

        config, _ = build_config()

        # Get admin users from config (comma-separated list)
        admin_users_str = config.get("oidc", "admin_users", fallback="")
        if not admin_users_str:
            return False, False  # is_admin, is_superuser

        # Parse comma-separated list and strip whitespace
        admin_identifiers = [x.strip() for x in admin_users_str.split(",") if x.strip()]

        # Check if user's sub or email matches any admin identifier
        oidc_sub = claims.get("sub", "")
        email = claims.get("email", "")

        is_admin = oidc_sub in admin_identifiers or email in admin_identifiers

        if is_admin:
            logger.warning(
                f"[OIDC Auth] User matches admin identifier: sub={oidc_sub}, email={email}"
            )

        return is_admin, False  # Regular admin, not superuser

    def _is_superuser(self, claims):
        """Check if user should have superuser privileges based on claims."""
        from pretalx.common.settings.config import build_config

        config, _ = build_config()

        # Get superuser users from config (comma-separated list)
        superuser_str = config.get("oidc", "superuser", fallback="")
        if not superuser_str:
            return False

        # Parse comma-separated list and strip whitespace
        superuser_identifiers = [
            x.strip() for x in superuser_str.split(",") if x.strip()
        ]

        # Check if user's sub or email matches any superuser identifier
        oidc_sub = claims.get("sub", "")
        email = claims.get("email", "")

        is_superuser = (
            oidc_sub in superuser_identifiers or email in superuser_identifiers
        )

        if is_superuser:
            logger.warning(
                f"[OIDC Auth] User matches superuser identifier: sub={oidc_sub}, email={email}"
            )

        return is_superuser

    def _get_user_privileges(self, claims):
        """Determine user privileges from OIDC claims."""
        is_admin, _ = self._is_admin_user(claims)  # Regular admin check
        is_superuser = self._is_superuser(claims)  # Superuser check

        # Superusers are also admins (staff)
        if is_superuser:
            is_admin = True

        return is_admin, is_superuser

    def _sync_user_privileges_and_teams(
        self, user, should_be_admin, should_be_superuser
    ):
        """
        Synchronize user privileges and team memberships with current config.
        This method ensures that:
        1. User Django flags (is_staff, is_superuser) are correctly set
        2. User is added to/removed from admin teams as needed
        """
        logger.info(
            f"[OIDC Auth] Syncing privileges for {user.email}: admin={should_be_admin}, superuser={should_be_superuser}"
        )

        # Update Django user flags
        user_updated = False
        if user.is_staff != should_be_admin:
            logger.warning(
                f"[OIDC Auth] Updating is_staff: {user.is_staff} → {should_be_admin}"
            )
            user.is_staff = should_be_admin
            user_updated = True

        if user.is_superuser != should_be_superuser:
            logger.warning(
                f"[OIDC Auth] Updating is_superuser: {user.is_superuser} → {should_be_superuser}"
            )
            user.is_superuser = should_be_superuser
            user_updated = True

        if user_updated:
            user.save(update_fields=["is_staff", "is_superuser"])

        # Handle team memberships for admin users
        from pretalx.event.models import Organiser, Team

        if should_be_admin:
            # User should be admin - ensure organiser and admin teams exist

            # Get or create default organiser
            organiser, created = Organiser.objects.get_or_create(
                slug="default-org",
                defaults={
                    "name": "Default Organisation",
                },
            )
            if created:
                logger.warning(
                    f"[OIDC Auth] Created default organiser: {organiser.name}"
                )

            # Get or create admin team for this organiser
            admin_team, team_created = Team.objects.get_or_create(
                organiser=organiser,
                name="Admin Team",
                defaults={
                    "can_create_events": True,
                    "can_change_teams": True,
                    "can_change_organiser_settings": True,
                    "can_change_event_settings": True,
                    "can_change_submissions": True,
                },
            )
            if team_created:
                logger.warning(f"[OIDC Auth] Created admin team: {admin_team.name}")

            # Add user to admin team if not already a member
            if not admin_team.members.filter(pk=user.pk).exists():
                admin_team.members.add(user)
                logger.warning(
                    f"[OIDC Auth] Added {user.email} to admin team: {admin_team.name}"
                )

        else:
            # User should NOT be admin - remove from ALL admin teams
            admin_teams = Team.objects.filter(
                can_create_events=True,
                can_change_teams=True,
                can_change_organiser_settings=True,
            )
            current_admin_teams = admin_teams.filter(members=user)
            for team in current_admin_teams:
                logger.warning(
                    f"[OIDC Auth] Removing {user.email} from admin team: {team.name}"
                )
                team.members.remove(user)

        # Log final state
        admin_teams = Team.objects.filter(
            can_create_events=True,
            can_change_teams=True,
            can_change_organiser_settings=True,
        )
        final_admin_teams = admin_teams.filter(members=user).count()
        logger.info(
            (
                f"[OIDC Auth] User {user.email} sync complete: staff={user.is_staff}, "
                f"superuser={user.is_superuser}, admin_teams={final_admin_teams}"
            )
        )

    def create_user(self, claims):
        """Create a new user from OIDC claims."""
        logger.warning(f"[OIDC Auth] create_user() called with claims: {claims}")

        email = claims.get("email")
        if not email:
            logger.error("[OIDC Auth] No email in claims, cannot create user")
            return None

        # Check user privileges
        is_admin, is_superuser = self._get_user_privileges(claims)

        # Create user with random password (OIDC-only authentication)
        user = User.objects.create_user(
            email=email,
            name=claims.get("name", "") or claims.get("preferred_username", ""),
        )

        # Sync privileges and team memberships
        self._sync_user_privileges_and_teams(user, is_admin, is_superuser)

        logger.warning(
            (
                f"[OIDC Auth] Created user: {user.email} "
                f"(id={user.pk}, admin={is_admin}, superuser={is_superuser})"
            )
        )

        # Store OIDC ID
        try:
            OIDCUserProfile.objects.create(  # noqa: F841
                user=user,
                oidc_id=claims.get("sub"),
                provider=getattr(settings, "OIDC_PROVIDER_NAME", "oidc"),
            )
            logger.warning(
                f"[OIDC Auth] Created OIDC profile for user {user.email} with sub={claims.get('sub')}"
            )
        except Exception as e:
            logger.error(
                f"[OIDC Auth] Failed to create OIDC profile for user {user.email}: {e}"
            )
            # Check if profile already exists and update it
            try:
                existing_profile = user.oidc_profile
                existing_profile.oidc_id = claims.get("sub")
                existing_profile.provider = getattr(
                    settings, "OIDC_PROVIDER_NAME", "oidc"
                )
                existing_profile.save()
                logger.warning(
                    f"[OIDC Auth] Updated existing OIDC profile for user {user.email}"
                )
            except OIDCUserProfile.DoesNotExist:
                logger.error(
                    f"[OIDC Auth] Could not create or update OIDC profile for user {user.email}"
                )
                # This is a critical error - user was created but profile couldn't be linked
                raise

        return user

    def update_user(self, user, claims):
        """Update existing user from OIDC claims."""
        logger.info(f"[OIDC Auth] Updating user {user.email} from claims: {claims}")

        # Update name if provided
        name = claims.get("name", "") or claims.get("preferred_username", "")
        if name and name != user.name:
            logger.info(
                f"[OIDC Auth] Updating user name from '{user.name}' to '{name}'"
            )
            user.name = name
            user.save(update_fields=["name"])

        # Always sync privileges and team memberships on every login
        # This ensures user permissions are always current with config
        is_admin, is_superuser = self._get_user_privileges(claims)
        self._sync_user_privileges_and_teams(user, is_admin, is_superuser)

        logger.warning(
            f"[OIDC Auth] Updated user {user.email}: admin={is_admin}, superuser={is_superuser}"
        )

        return user

    def filter_users_by_claims(self, claims):
        """Return users matching the OIDC claims."""
        oidc_id = claims.get("sub")
        logger.info(
            f"[OIDC Auth] Filtering users by claims. sub={oidc_id}, email={claims.get('email')}"
        )

        if not oidc_id:
            logger.error("[OIDC Auth] No 'sub' claim found")
            return User.objects.none()

        # Try to find user by OIDC ID
        try:
            profile = OIDCUserProfile.objects.select_related("user").get(
                oidc_id=oidc_id
            )
            logger.info(
                f"[OIDC Auth] Found existing user by OIDC ID: {profile.user.email}"
            )
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
                    logger.info(
                        f"[OIDC Auth] Linking existing user {user.email} to OIDC"
                    )

                    # Check if user already has an OIDC profile
                    try:
                        existing_profile = user.oidc_profile
                        # Update existing profile with new OIDC ID
                        logger.info(
                            (
                                f"[OIDC Auth] Updating existing OIDC profile for "
                                f"{user.email}: {existing_profile.oidc_id} → {oidc_id}"
                            )
                        )
                        existing_profile.oidc_id = oidc_id
                        existing_profile.provider = getattr(
                            settings, "OIDC_PROVIDER_NAME", "oidc"
                        )
                        existing_profile.save()
                    except OIDCUserProfile.DoesNotExist:
                        # Create new profile for user
                        logger.info(
                            f"[OIDC Auth] Creating new OIDC profile for {user.email}"
                        )
                        OIDCUserProfile.objects.create(
                            user=user,
                            oidc_id=oidc_id,
                            provider=getattr(settings, "OIDC_PROVIDER_NAME", "oidc"),
                        )

                    return User.objects.filter(pk=user.pk)

            logger.info("[OIDC Auth] No existing user found, will create new user")
            return User.objects.none()

    def authenticate(self, request, **kwargs):
        """Override to handle pretalx-specific authentication and HTTPS redirect URI enforcement."""
        logger.info(f"[OIDC Auth] authenticate() called with kwargs: {kwargs.keys()}")

        # First, store the original request
        self.request = request
        if not self.request:
            return None

        state = self.request.GET.get("state")
        code = self.request.GET.get("code")
        nonce = kwargs.pop("nonce", None)
        code_verifier = kwargs.pop("code_verifier", None)

        if not code or not state:
            return None

        # Get the reverse URL for callback
        reverse_url = self.get_settings(
            "OIDC_AUTHENTICATION_CALLBACK_URL", "oidc_authentication_callback"
        )

        # Generate redirect URI
        redirect_uri = absolutify(self.request, reverse(reverse_url))

        # Check if HTTPS redirect enforcement is enabled and fix the redirect URI
        force_https = getattr(settings, "OIDC_FORCE_HTTPS_REDIRECT", False)
        if force_https and redirect_uri.startswith("http://"):
            redirect_uri = redirect_uri.replace("http://", "https://", 1)
            logger.info("[OIDC Auth] Enforced HTTPS redirect URI for token exchange")

        # Build token payload with corrected redirect URI
        token_payload = {
            "client_id": self.OIDC_RP_CLIENT_ID,
            "client_secret": self.OIDC_RP_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        }

        # Send code_verifier with token request if using PKCE
        if code_verifier is not None:
            token_payload.update({"code_verifier": code_verifier})

        # Get the token
        token_info = self.get_token(token_payload)
        id_token = token_info.get("id_token")
        access_token = token_info.get("access_token")

        # Validate the token
        payload = self.verify_token(id_token, nonce=nonce)

        if payload:
            self.store_tokens(access_token, id_token)
            try:
                user = self.get_or_create_user(access_token, id_token, payload)

                if user:
                    logger.warning(
                        f"[OIDC Auth] Authentication successful for user: {user.email}"
                    )
                    logger.warning(f"[OIDC Auth]   - user.pk = {user.pk}")
                    logger.warning(f"[OIDC Auth]   - user.is_active = {user.is_active}")
                    logger.warning(
                        f"[OIDC Auth]   - user.is_authenticated = {user.is_authenticated}"
                    )
                    if request:
                        # Log the authentication
                        user.log_action(
                            "pretalx.user.oidc.login",
                            data={
                                "provider": getattr(
                                    settings, "OIDC_PROVIDER_NAME", "oidc"
                                )
                            },
                        )
                else:
                    logger.warning(
                        "[OIDC Auth] Authentication failed - no user returned"
                    )

                return user
            except Exception as exc:
                logger.warning("failed to get or create user: %s", exc)
                return None

        return None
