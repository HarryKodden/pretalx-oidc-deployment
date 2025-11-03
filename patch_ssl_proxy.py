#!/usr/bin/env python3
"""
Patch Django settings to add SSL proxy awareness settings.
This ensures Django recognizes HTTPS when behind a reverse proxy.
"""

import re

settings_path = "/pretalx/src/pretalx/settings.py"

# Read the settings file
with open(settings_path, 'r') as f:
    content = f.read()

# Add SSL proxy settings after the existing security settings
ssl_proxy_config = '''
# SSL Proxy Settings - for deployments behind reverse proxy
# These settings ensure Django recognizes HTTPS when behind a proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = False  # Proxy handles SSL termination
SECURE_SSL_HOST = False      # Proxy handles SSL termination

# Additional proxy trust settings (if not already set)
if not hasattr(config, 'getboolean') or not config.getboolean('site', 'trust_x_forwarded_proto', fallback=False):
    print("[Settings] Added SSL proxy awareness settings")
'''

# Find a good place to insert - after CSRF_TRUSTED_ORIGINS or security settings
if 'SECURE_PROXY_SSL_HEADER' not in content:
    # Look for CSRF_TRUSTED_ORIGINS section or end of security settings
    if 'CSRF_TRUSTED_ORIGINS' in content:
        # Insert after CSRF_TRUSTED_ORIGINS
        pattern = r"(CSRF_TRUSTED_ORIGINS = .*?\n(?:\s+.*?\n)*)"
        content = re.sub(pattern, r"\1" + ssl_proxy_config, content, count=1)
        print("✓ Added SSL proxy awareness settings after CSRF config")
    else:
        # Find a general security section or add at the end
        # Look for ALLOWED_HOSTS as a reference point
        pattern = r"(ALLOWED_HOSTS = .*?\n(?:\s+.*?\n)*)"
        if re.search(pattern, content):
            content = re.sub(pattern, r"\1" + ssl_proxy_config, content, count=1)
            print("✓ Added SSL proxy awareness settings after ALLOWED_HOSTS")
        else:
            # Add at the end of the file
            content += "\n" + ssl_proxy_config
            print("✓ Added SSL proxy awareness settings at end of file")
else:
    print("✓ SSL proxy settings already configured")

# Write the patched settings
with open(settings_path, 'w') as f:
    f.write(content)