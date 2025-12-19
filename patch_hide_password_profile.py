#!/usr/bin/env python3
"""
Patch the user profile template to hide password change section when OIDC is enabled.

"""

import re

template_path = "/pretalx/src/pretalx/cfp/templates/cfp/event/user_profile.html"

# Read the template
with open(template_path, 'r') as f:
    content = f.read()

# Find the "Your Account" section and wrap it in an if statement
# The section starts with <h2>{% translate "Your Account" %}</h2>
# and ends before the account deletion section

old_section = r'''    <h2>{% translate "Your Account" %}</h2>
    <p>{% translate "You can change your log in data here." %}</p>
    <form method="post" class="form password-input-form">
        {% csrf_token %}
        {{ login_form.old_password.as_field_group }}
        {{ login_form.email.as_field_group }}
        {{ login_form.password.as_field_group }}
        {{ login_form.password_repeat.as_field_group }}
        <div class="row">
            <div class="col-md-4 flip ml-auto">
                <input type="hidden" name="form" value="login">
                <button type="submit" class="btn btn-block btn-success btn-lg">
                    {{ phrases.base.save }}
                </button>
            </div>
        </div>
    </form>'''

new_section = r'''    {% if not oidc_hide_password_auth %}
    <h2>{% translate "Your Account" %}</h2>
    <p>{% translate "You can change your log in data here." %}</p>
    <form method="post" class="form password-input-form">
        {% csrf_token %}
        {{ login_form.old_password.as_field_group }}
        {{ login_form.email.as_field_group }}
        {{ login_form.password.as_field_group }}
        {{ login_form.password_repeat.as_field_group }}
        <div class="row">
            <div class="col-md-4 flip ml-auto">
                <input type="hidden" name="form" value="login">
                <button type="submit" class="btn btn-block btn-success btn-lg">
                    {{ phrases.base.save }}
                </button>
            </div>
        </div>
    </form>
    {% endif %}'''

if old_section in content:
    content = content.replace(old_section, new_section)
    print("✓ Wrapped password change section in conditional")
else:
    print("✗ Could not find password change section to patch")
    exit(1)

# Write the patched template
with open(template_path, 'w') as f:
    f.write(content)

print(f"✓ Successfully patched {template_path}")
