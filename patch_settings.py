#!/usr/bin/env python3
"""
Patch pretalx settings.py to support custom AppConfig classes in plugins.
This is required for Django 3.2+ which removed default_app_config support.
"""

import re
import sys

settings_file = '/pretalx/src/pretalx/settings.py'

try:
    with open(settings_file, 'r') as f:
        content = f.read()

    # Find and replace the plugin loading code
    old_code = '    INSTALLED_APPS.append(entry_point.module)'
    
    new_code = '''    # Use entry_point.value to get the full path including the AppConfig class
    # This is needed for Django 3.2+ where default_app_config was removed
    # Convert colon notation (entrypoint style) to dot notation (Python import style)
    app_config_path = entry_point.value.replace(':', '.')
    INSTALLED_APPS.append(app_config_path)'''

    if old_code in content:
        content = content.replace(old_code, new_code)
        
        with open(settings_file, 'w') as f:
            f.write(content)
        
        print("✓ Successfully patched settings.py for plugin AppConfig support")
        sys.exit(0)
    else:
        print("⚠ Warning: Could not find expected code pattern in settings.py")
        print("The file may already be patched or have a different structure.")
        sys.exit(0)  # Exit with success anyway
        
except FileNotFoundError:
    print(f"✗ Error: {settings_file} not found")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error patching settings.py: {e}")
    sys.exit(1)
