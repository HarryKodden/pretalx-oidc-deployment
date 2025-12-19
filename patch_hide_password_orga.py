#!/usr/bin/env python3
"""
Patch the organizer user settings template to hide password change section when OIDC is enabled.
"""

import re

template_path = "/pretalx/src/pretalx/orga/templates/orga/user.html"

# Read the template
with open(template_path, 'r') as f:
    content = f.read()

# Find the "Login settings" fieldset and wrap it in an if statement
old_section = '''    <fieldset class="m-2 password-input-form">
        <legend id="login">{% translate "Login settings" %}</legend>
        {% include "orga/includes/base_form.html" with form=login_form submit_buttons=login_submit %}
    </fieldset>'''

new_section = '''    {% if not oidc_hide_password_auth %}
    <fieldset class="m-2 password-input-form">
        <legend id="login">{% translate "Login settings" %}</legend>
        {% include "orga/includes/base_form.html" with form=login_form submit_buttons=login_submit %}
    </fieldset>
    {% endif %}'''

if old_section in content:
    content = content.replace(old_section, new_section)
    print("✓ Wrapped login settings section in conditional")
else:
    print("✗ Could not find login settings section to patch")
    exit(1)

# Write the patched template
with open(template_path, 'w') as f:
    f.write(content)

print(f"✓ Successfully patched {template_path}")
