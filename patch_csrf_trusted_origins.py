#!/usr/bin/env python3
"""
Patch Django settings to add CSRF_TRUSTED_ORIGINS from site URL.
This is needed for logout and other POST requests to work with HTTPS.
"""

import re

settings_path = "/pretalx/src/pretalx/settings.py"

# Read the settings file
with open(settings_path, 'r') as f:
    content = f.read()

# Add CSRF_TRUSTED_ORIGINS configuration after ALLOWED_HOSTS
# Find the ALLOWED_HOSTS line
csrf_config = '''
# CSRF Trusted Origins - extracted from site URL
# This allows POST requests (like logout) to work correctly
CSRF_TRUSTED_ORIGINS = []
if config.has_option('site', 'url'):
    site_url = config.get('site', 'url')
    if site_url:
        # Add the origin (scheme + domain)
        from urllib.parse import urlparse
        parsed = urlparse(site_url)
        if parsed.scheme and parsed.netloc:
            origin = f"{parsed.scheme}://{parsed.netloc}"
            CSRF_TRUSTED_ORIGINS.append(origin)
            print(f"[Settings] Added CSRF trusted origin: {origin}")

'''

# Find a good place to insert - after ALLOWED_HOSTS configuration
if 'CSRF_TRUSTED_ORIGINS' not in content:
    # Look for ALLOWED_HOSTS section
    pattern = r"(ALLOWED_HOSTS = .*?\n(?:\s+config\.get.*?\n)*)"
    
    if re.search(pattern, content):
        content = re.sub(pattern, r"\1" + csrf_config, content, count=1)
        print("✓ Added CSRF_TRUSTED_ORIGINS configuration")
    else:
        print("✗ Could not find ALLOWED_HOSTS to insert CSRF config")
        exit(1)
else:
    print("✓ CSRF_TRUSTED_ORIGINS already configured")

# Write the patched settings
with open(settings_path, 'w') as f:
    f.write(content)

print(f"✓ Successfully patched {settings_path}")
