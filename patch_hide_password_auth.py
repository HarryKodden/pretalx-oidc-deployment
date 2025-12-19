#!/usr/bin/env python3
"""
Patch pretalx to hide username/password authentication when OIDC is the only backend.

This modifies the auth.html template to check if OIDC is configured as the only
authentication backend, and if so, automatically hides the password login and
registration forms, leaving only the OIDC button visible.

"""
import sys


def patch_auth_template():
    """Patch the auth.html template to hide password auth when only OIDC is used."""
    template_file = '/pretalx/src/pretalx/common/templates/common/auth.html'
    
    try:
        with open(template_file, 'r') as f:
            content = f.read()

        # Check if already patched with the NEW version
        if 'AUTO-DETECT OIDC-ONLY MODE: Always render auth signal' in content:
            print("⚠ Template already patched for OIDC-only authentication")
            return True

        # APPROACH: 
        # 1. Add oidc_only_auth check to hide_login and hide_register conditions
        # 2. ALSO add the signal call after CSRF token so OIDC button always appears
        
        # Patch the hide_login condition
        old_hide_login = "{% if not hide_login %}"
        new_hide_login = "{% if not hide_login and not oidc_only_auth %}"
        
        # Patch the hide_register condition  
        old_hide_register = "{% if not hide_register %}"
        new_hide_register = "{% if not hide_register and not oidc_only_auth %}"
        
        # Add signal call right after CSRF token so it's always called
        old_csrf = """{% csrf_token %}

{% if not hide_login"""
        new_csrf = """{% csrf_token %}

{# AUTO-DETECT OIDC-ONLY MODE: Always render auth signal for OIDC button #}
{% html_signal "pretalx.common.signals.auth_html" sender=request.event request=request next_url=success_url %}

{% if not hide_login"""
        
        # Add comment at top to mark as patched
        old_start = """{% load html_signal %}
{% load i18n %}"""
        
        new_start = """{% load html_signal %}
{% load i18n %}

{# AUTO-DETECT OIDC-ONLY MODE: Modified to check oidc_only_auth and always show OIDC button #}"""

        content = content.replace(old_start, new_start, 1)
        content = content.replace(old_csrf, new_csrf, 1)
        content = content.replace(old_hide_login, new_hide_login)
        content = content.replace(old_hide_register, new_hide_register)

        with open(template_file, 'w') as f:
            f.write(content)
        
        print("✓ Successfully patched auth.html to hide password authentication when OIDC-only")
        return True
        
    except FileNotFoundError:
        print(f"✗ Error: {template_file} not found")
        return False
    except Exception as e:
        print(f"✗ Error patching auth.html: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    success = patch_auth_template()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
