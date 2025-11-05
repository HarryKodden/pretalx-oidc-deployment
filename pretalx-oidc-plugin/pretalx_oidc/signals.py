# SPDX-FileCopyrightText: 2025-present Harry Kodden
# SPDX-License-Identifier: Apache-2.0

import logging

from django.conf import settings
from django.dispatch import receiver
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from pretalx.cfp.signals import html_above_profile_page
from pretalx.cfp.signals import html_head as cfp_html_head
from pretalx.common.signals import auth_html
from pretalx.orga.signals import html_head as orga_html_head

logger = logging.getLogger(__name__)


def should_hide_password_form():
    """Check if password forms should be hidden based on configuration."""
    try:
        from pretalx.common.settings.config import build_config

        config, _ = build_config()
        if config.has_section("oidc"):
            return config.getboolean("oidc", "hide_password_form", fallback=False)
    except Exception:
        pass
    return False


# CSS to hide password authentication forms
PASSWORD_HIDE_CSS = """
<style>
    /* Hide password login and registration form elements */
    #id_login_email,
    #id_login_password,
    #id_register_name,
    #id_register_email,
    #id_register_password,
    #id_register_password_repeat,
    input[name=login_email],
    input[name=login_password],
    input[name=register_name],
    input[name=register_email],
    input[name=register_password],
    input[name=register_password_repeat],
    label[for=id_login_email],
    label[for=id_login_password],
    label[for=id_register_name],
    label[for=id_register_email],
    label[for=id_register_password],
    label[for=id_register_password_repeat],
    form#auth-form button.btn-success,
    form#auth-form button.btn-info,
    a[href*=reset],
    .password-progress,
    .password_strength_info,
    .user-profile .password-change,
    .user-settings .password-change,
    .auth-form-block h4 {
        display: none !important;
    }

    /* Hide password change fields on profile page */
    #id_old_password,
    #id_password,
    #id_password_repeat,
    label[for=id_old_password],
    label[for=id_password],
    label[for=id_password_repeat],
    input[name=old_password],
    input[name=password],
    input[name=password_repeat] {
        display: none !important;
    }

    /* Hide email field ONLY on profile page (not on login) */
    .speaker-profile-form ~ form #id_email,
    .speaker-profile-form ~ form label[for=id_email],
    .speaker-profile-form ~ form input[name=email] {
        display: none !important;
    }

    /* Hide the password change form on profile page - only if it has old_password field */
    form.password-input-form:not(#auth-form),
    /* Hide the empty div after the password form */
    form.password-input-form:not(#auth-form) + div,
    /* Hide h2 and h3 headings that contain account-related text */
    /* We target the second h2 which is "Your Account" */
    form.speaker-profile-form ~ h2:first-of-type,
    form.speaker-profile-form ~ h2:first-of-type + p,
    /* Also try targeting by text content proximity */
    h2 + p + form.password-input-form,
    h2:last-of-type,
    main > h2:last-of-type,
    main > h2:last-of-type + p {
        display: none !important;
    }

    /* Ensure OIDC button container is visible */
    #oidc-login-only {
        display: block !important;
    }
</style>
"""


@receiver(auth_html)
def add_oidc_login_button(sender, request, next_url=None, **kwargs):
    """Add OIDC login button to the authentication page."""
    logger.info(f"[OIDC] auth_html signal received - sender: {sender}")
    try:
        login_url = reverse("plugins:pretalx_oidc:oidc_authentication_init")

        if next_url:
            login_url = f"{login_url}?next={next_url}"

        # Get provider name from settings, fallback to "OIDC" if not set
        provider_name = getattr(settings, "OIDC_PROVIDER_NAME", "OIDC")
        button_text = _("Sign in with {provider}").format(provider=provider_name)

        # Check if we should hide password forms
        hide_password = should_hide_password_form()
        logger.info(f"[OIDC] hide_password_form config: {hide_password}")

        # Build the complete HTML including CSS and button
        # Note: We include CSS here because auth_html content is inserted into the page body
        html_parts = []

        if hide_password:
            logger.info("[OIDC] Injecting CSS to hide password forms")
            # Add timestamp to prevent caching issues
            import time

            timestamp = int(time.time())
            html_parts.append(f"<!-- OIDC CSS v{timestamp} -->")
            html_parts.append(PASSWORD_HIDE_CSS)

        # Add OIDC button with unique ID
        html_parts.append(
            f"""
    <div class="auth-form-block w-100" id="oidc-login-only">
        <a class="btn btn-lg btn-primary btn-block" href="{login_url}">
            <i class="fa fa-sign-in"></i> {button_text}
        </a>
    </div>
    """
        )

        result = "\n".join(html_parts)
        logger.info(
            f"[OIDC] Returning HTML (length: {len(result)}, has <style>: {'<style>' in result})"
        )
        return mark_safe(result)
    except Exception as e:
        logger.error(f"[OIDC] Error in signal handler: {e}", exc_info=True)
        return ""


@receiver(cfp_html_head)
def add_cfp_css(sender, request, **kwargs):
    """Inject CSS to hide password forms on CFP/frontend pages."""
    logger.info(
        f"[OIDC] cfp_html_head signal received - sender: {sender}, path: {request.path if request else 'no request'}"
    )
    # This signal is called for both event-specific and global pages
    # sender will be the event or None for global pages
    if should_hide_password_form():
        return mark_safe(PASSWORD_HIDE_CSS)
    return ""


@receiver(orga_html_head)
def add_orga_css(sender, request, **kwargs):
    """Inject CSS to hide password forms on organizer backend pages."""
    logger.info(
        f"[OIDC] orga_html_head signal received - sender: {sender}, path: {request.path if request else 'no request'}"
    )
    # This signal is called for both event-specific and global pages
    # sender will be the event or None for global pages (like /orga/ login)
    if should_hide_password_form():
        return mark_safe(PASSWORD_HIDE_CSS)
    return ""


@receiver(html_above_profile_page)
def add_profile_css(sender, request, **kwargs):
    """Inject CSS to hide password forms on the user profile page.

    This signal is specifically called on the profile page template and
    allows us to inject CSS even when cfp_html_head might not be working.
    """
    path = request.path if request else "no request"
    logger.info(
        f"[OIDC] html_above_profile_page signal received - sender: {sender}, path: {path}"
    )
    if should_hide_password_form():
        # Add timestamp to prevent caching
        import time

        timestamp = int(time.time())
        return mark_safe(f"<!-- OIDC Profile CSS v{timestamp} -->\n{PASSWORD_HIDE_CSS}")
    return ""
