# Pretalx with OIDC Authentication

[![Docker Build](https://github.com/HarryKodden/pretalx-oidc-deployment/actions/workflows/docker-build.yml/badge.svg)](https://github.com/HarryKodden/pretalx-oidc-deployment/actions/workflows/docker-build.yml)
[![Lint](https://github.com/HarryKodden/pretalx-oidc-deployment/actions/workflows/lint.yml/badge.svg)](https://github.com/HarryKodden/pretalx-oidc-deployment/actions/workflows/lint.yml)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Pretalx](https://img.shields.io/badge/Pretalx-v2025.2.0-orange)](https://pretalx.com)
[![OIDC](https://img.shields.io/badge/OIDC-Enabled-green)](https://openid.net/connect/)

---

A complete Docker-based deployment for [pretalx](https://pretalx.com) with OpenID Connect (OIDC) authentication support. This setup enables OIDC-only authentication while hiding traditional password-based login forms.

> **🔌 Plugin-Based** | **🔒 SSO Authentication** | **📦 Docker Compose**

## Features

✨ **OIDC Authentication**
- Single Sign-On (SSO) via OpenID Connect
- Auto-discovery from OIDC provider's `.well-known/openid-configuration` endpoint
- Automatic user creation and profile synchronization on first login
- Support for any standards-compliant OIDC provider (Keycloak, Auth0, Azure AD, etc.)

🔒 **Security & Access Control**
- OIDC-only mode (password authentication hidden via CSS injection)
- Admin and superuser role assignment via OIDC claims
- Automatic privilege synchronization on every login
- Per-event plugin enablement for granular control

🎨 **Clean User Experience**
- Login pages show only OIDC button
- Password forms hidden on login, registration, and profile pages
- CSS-based form hiding (no template patching required)
- Seamless integration with pretalx's existing UI

🏗️ **Architecture**
- Native pretalx plugin using Django signals
- No core pretalx modifications required
- Configuration via `pretalx.cfg` (standard pretalx config file)
- Docker Compose setup with PostgreSQL, Redis, and MailHog

## Table of Contents

- [Quick Start](#quick-start)
- [Configuration](#configuration)
  - [Required Settings](#required-settings)
  - [HTTPS Redirect URI Configuration](#https-redirect-uri-configuration)
  - [Email Configuration](#email-configuration)
  - [OIDC Provider Setup](#oidc-provider-setup)
  - [Admin Users & Superusers](#admin-users--superusers)
- [Docker Deployment](#docker-deployment)
- [Architecture](#architecture)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Quick Reference](#quick-reference)
- [License](#license)

## Key Technical Decisions

This deployment makes several important architectural choices:

1. **CSS-based Form Hiding**: Password forms are hidden via injected CSS rather than template modifications. This approach:
   - Survives pretalx updates (no template patching needed)
   - Can be toggled via configuration (`hide_password_form`)
   - Uses Django signals for clean integration

2. **Per-Event Plugin Enablement**: The plugin must be manually enabled for each event. This is by design because:
   - Pretalx doesn't provide signals for event creation
   - Gives organizers control over which events use OIDC
   - Follows pretalx's plugin architecture patterns

3. **No Core Modifications**: The entire OIDC integration is achieved through:
   - A standard pretalx plugin installed via pip
   - Django signal receivers for UI injection
   - Standard `pretalx.cfg` configuration
   - Zero changes to pretalx core code

4. **Automatic Privilege Sync**: User privileges (admin/superuser) sync on every OIDC login:
   - No manual sync commands needed
   - Configuration changes take effect immediately
   - Both Django permissions and team memberships updated

## Quick Start

### Prerequisites

- Docker and Docker Compose
- An OIDC provider (Keycloak, Auth0, Okta, Azure AD, etc.)
- OIDC client credentials (client ID and secret)

### 1. Clone this repository

```bash
git clone <your-repo-url>
cd pretalx-oidc-deployment
```

### 2. Create configuration file

Copy the example configuration and edit it:

```bash
cp pretalx.cfg.example pretalx.cfg
```

Edit `pretalx.cfg` with your settings (see [Configuration](#configuration) below).

### 3. Build and start

```bash
docker compose build
docker compose up -d
```

### 4. Initialize database and access pretalx

The first time you start the containers, the database will be automatically migrated and static files built.

Access pretalx at the URL configured in `pretalx.cfg` section `[site]` → `url`.

### 5. Enable the OIDC plugin for each event

**Important**: The OIDC plugin must be manually enabled for each event:

1. Log in via OIDC (or use password auth for initial setup)
2. Go to event settings: `/orga/event/{event-slug}/settings/plugins`
3. Find "OIDC Authentication" in the plugin list
4. Check the box to enable it
5. Click Save

Once enabled, the event will have:
- OIDC login button on login pages
- Password forms hidden (if `hide_password_form = true`)
- Clean OIDC-only authentication experience

## Configuration

### Required Settings

Edit `pretalx.cfg`:

```ini
[site]
url = https://your-domain.com
# For local development: url = http://localhost:8355

[oidc]
# OIDC Provider auto-discovery URL
op_discovery_endpoint = https://your-oidc-provider.com/realms/your-realm

# OIDC Client credentials
rp_client_id = your-client-id
rp_client_secret = your-client-secret

# Provider display name
provider_name = Your Provider Name

# Hide password authentication (recommended for OIDC-only)
hide_password_form = true

# Force HTTPS redirect URIs (recommended for production behind reverse proxy)
force_https_redirect = true

# Admin users (comma-separated list of OIDC 'sub' or email)
admin_users = user-sub-claim-id, admin@example.com
```

### HTTPS Redirect URI Configuration

When deploying pretalx behind a reverse proxy (nginx, Apache, Caddy, etc.), you may encounter issues where OIDC redirect URIs are generated with `http://` instead of `https://`, causing authentication failures.

#### The Problem

```
Error: invalid_redirect_uri
Expected: https://your-domain.com/oidc/callback/
Received: http://your-domain.com/oidc/callback/
```

#### The Solution

Configure both **proxy settings** and **HTTPS enforcement**:

```ini
[site]
# Use HTTPS URLs for production
url = https://your-domain.com
media_url = https://your-domain.com/media/
static_url = https://your-domain.com/static/

# Trust proxy headers (CRITICAL for HTTPS detection)
trust_x_forwarded_proto = true
trust_x_forwarded_for = true
secure_proxy_ssl_header = true
use_x_forwarded_host = true

[oidc]
# Force HTTPS redirect URIs (plugin-level enforcement)
force_https_redirect = true
```

#### Reverse Proxy Configuration

**Caddy** (automatic):
```caddy
your-domain.com {
    reverse_proxy pretalx-container:8000
    # Caddy automatically sets proper headers
}
```

**Nginx**:
```nginx
location / {
    proxy_pass http://pretalx-container:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $host;
}
```

**Apache**:
```apache
ProxyPreserveHost On
ProxyPass / http://pretalx-container:8000/
ProxyPassReverse / http://pretalx-container:8000/
RequestHeader set X-Forwarded-Proto "https"
RequestHeader set X-Forwarded-For %{REMOTE_ADDR}s
```

This ensures that pretalx generates correct HTTPS redirect URIs that match your OIDC provider's registered callback URLs.
```

### Email Configuration

The deployment includes MailHog for development/testing email functionality:

```ini
[mail]
# Development setup with MailHog (included)
from = noreply@your-domain.com
host = mailhog
port = 1025
user = 
password = 
tls = false
ssl = false
```

**Access the mail frontend**: `https://mail.your-domain.com`

#### Development vs Production Email Behavior

- **Development Mode** (`DEBUG=true`): pretalx uses console email backend by default, printing emails to logs instead of sending them. MailHog is available for manual SMTP testing.
- **Production Mode** (`DEBUG=false`): pretalx automatically uses the SMTP settings from the `[mail]` section.

For production, configure with your SMTP provider (Gmail, SendGrid, AWS SES, etc.):

```ini
[mail]
# Production SMTP example (Gmail)
from = noreply@your-domain.com
host = smtp.gmail.com
port = 587
user = your-email@gmail.com
password = your-app-password
tls = true
```

### OIDC Provider Setup

#### Keycloak Example

1. Create a new client in Keycloak
2. Set **Access Type** to `confidential`
3. Add **Valid Redirect URIs**:
   - `https://your-domain.com/oidc/callback/`
   - `http://localhost:8355/oidc/callback/` (for development)
4. Note the client secret from the Credentials tab
5. Use the discovery URL: `https://keycloak-url/realms/your-realm`

#### Auth0 Example

1. Create a Regular Web Application
2. Add **Allowed Callback URLs**: `https://your-domain.com/oidc/callback/`
3. Note the Domain and Client ID/Secret
4. Discovery URL: `https://your-domain.auth0.com`

#### Azure AD Example

1. Register an application in Azure AD
2. Add redirect URI: `https://your-domain.com/oidc/callback/`
3. Create a client secret
4. Discovery URL: `https://login.microsoftonline.com/{tenant-id}/v2.0`

### Admin Users & Superusers

You can configure two levels of administrative access:

#### Admin Users (Staff Access)
To grant admin privileges, add OIDC user identifiers to `admin_users`:

```ini
[oidc]
# Use the 'sub' claim from OIDC tokens
admin_users = c946913e-bbda-41a1-bbc4-63e61ab81b3c

# Or use email addresses
admin_users = admin@example.com, manager@example.com

# Or mix both
admin_users = c946913e-bbda-41a1-bbc4-63e61ab81b3c, admin@example.com
```

#### Superusers (Full System Access)
To grant full superuser privileges, add OIDC user identifiers to `superuser`:

```ini
[oidc]
# Superusers have complete admin access including Django admin
superuser = superadmin@example.com

# Or use sub claims
superuser = c946913e-bbda-41a1-bbc4-63e61ab81b3c

# Or mix both
superuser = c946913e-bbda-41a1-bbc4-63e61ab81b3c, superadmin@example.com
```

**Note**: Superusers automatically get admin privileges as well. You only need to specify users in one list.

To find a user's `sub` claim, check the OIDC token or logs after first login.

### Automatic Privilege Synchronization

User privileges are **automatically synchronized** with the current configuration every time they log in via OIDC. This means:

✅ **No manual sync required** - privileges update on every authentication  
✅ **Always current** - users immediately get/lose access when config changes  
✅ **Safe configuration changes** - edit `admin_users`/`superuser` and changes take effect on next login  
✅ **Complete sync** - both Django permissions and team memberships are updated  

#### How It Works

1. **On every OIDC login**: The system reads current `admin_users` and `superuser` from `pretalx.cfg`
2. **Privilege reset**: User's current privileges are completely reset based on config
3. **Team membership**: Admin teams are automatically managed (add/remove as needed)
4. **Immediate effect**: Changes take effect immediately without waiting or manual intervention

#### Example Workflow

1. **Add a new admin**: Edit `pretalx.cfg` and add user to `admin_users`
   ```ini
   [oidc]
   admin_users = existing@example.com, newadmin@example.com
   ```

2. **User gets privileges**: Next time `newadmin@example.com` logs in, they automatically get admin access

3. **Remove admin**: Remove user from `admin_users` in config

4. **Privileges revoked**: Next time that user logs in, admin access is automatically removed

#### Manual Testing (Optional)

If you want to see what privileges a user currently has:

```bash
# Check user privileges in Django shell
docker compose exec pretalx python manage.py shell
>>> from pretalx.person.models import User
>>> user = User.objects.get(email="user@example.com")
>>> print(f"Staff: {user.is_staff}, Superuser: {user.is_superuser}")
>>> from pretalx.event.models import Team
>>> admin_teams = Team.objects.filter(members=user, can_create_events=True)
>>> print(f"Admin teams: {admin_teams.count()}")
```

## Docker Deployment

### Production Deployment

For production, configure HTTPS and proper URLs:

```ini
[site]
url = https://pretalx.yourdomain.com
media_url = https://pretalx.yourdomain.com/media/
static_url = https://pretalx.yourdomain.com/static/
trust_x_forwarded_proto = true
trust_x_forwarded_for = true
```

Mount volumes for persistent data:

```yaml
# docker-compose.yml
volumes:
  - ./data:/data
  - ./media:/public/media
  - ./static:/public/static
```

### Environment Variables

You can override settings with environment variables in `docker-compose.yml`:

```yaml
environment:
  - PRETALX_OIDC_CLIENT_ID=${OIDC_CLIENT_ID}
  - PRETALX_OIDC_CLIENT_SECRET=${OIDC_CLIENT_SECRET}
```

## Architecture

This deployment uses a **clean plugin-based architecture** following pretalx best practices:

### Components

1. **pretalx-oidc Plugin** (`pretalx-oidc-plugin/`)
   - Custom OIDC authentication backend extending `mozilla-django-oidc`
   - Django signal receivers for injecting UI modifications
   - No template patching - all UI changes via CSS injection
   - Configuration via standard `pretalx.cfg`

2. **Docker Setup**
   - **pretalx**: Main application container (Python 3.10)
   - **postgres**: PostgreSQL 14 database
   - **redis**: Cache and session storage
   - **mailhog**: Development email testing (SMTP server + web UI)

### Plugin Architecture

The `pretalx_oidc` plugin uses Django signals to integrate cleanly with pretalx:

- **`auth.py`** - OIDC authentication backend with admin role mapping
- **`signals.py`** - Signal receivers that:
  - Inject OIDC login button (`auth_html` signal)
  - Inject CSS to hide password forms (`cfp_html_head`, `orga_html_head`, `html_above_profile_page` signals)
- **`views.py`** - Custom OIDC login/callback handlers
- **`config.py`** - Auto-discovery and Django settings configuration
- **`context_processors.py`** - Template context for configuration access
- **`urls.py`** - OIDC callback URL routing

### How Password Forms Are Hidden

Instead of patching pretalx templates (which would break on updates), the plugin:

1. Reads `hide_password_form` configuration from `pretalx.cfg`
2. Uses Django signals to inject CSS into page `<head>` tags
3. CSS rules hide password-related form fields with `display: none !important`
4. Works on login, registration, organizer, and profile pages
5. No core pretalx files are modified

### Why This Approach?

✅ **Update-safe**: No template modifications, survives pretalx upgrades  
✅ **Reversible**: Disable plugin or set `hide_password_form = false` to restore password auth  
✅ **Standard**: Uses pretalx's official plugin system and signals  
✅ **Clean**: No monkey-patching or core code modifications

## Troubleshooting

### Plugin not working for new event

**Solution**: The plugin must be manually enabled per-event:
- Go to `/orga/event/{event-slug}/settings/plugins`
- Enable "OIDC Authentication"
- Click Save

This is by design - pretalx doesn't provide signals for auto-enabling plugins on event creation.

### Login redirects back to login page

- Check that `admin_users` or `superuser` includes your OIDC identifier (sub or email)
- Verify the OIDC callback URL in your provider matches: `https://your-domain.com/oidc/callback/`
- Check Docker logs: `docker compose logs -f pretalx`
- Ensure plugin is enabled for the event (see above)

### Password forms still visible

- Verify `hide_password_form = true` is set in `[oidc]` section of `pretalx.cfg`
- Ensure the plugin is enabled for the event at `/orga/event/{event-slug}/settings/plugins`
- Check browser console for CSS loading issues
- Clear browser cache and hard refresh (Ctrl+Shift+R / Cmd+Shift+R)

### CSRF errors on logout

Pretalx automatically handles this. If you still see CSRF errors:
- Ensure `url` in `[site]` section matches your actual domain (including https://)
- For HTTPS deployments, set `trust_x_forwarded_proto = true`
- Verify your reverse proxy sets the `X-Forwarded-Proto: https` header

### Invalid redirect URI errors

**Error**: `invalid_redirect_uri` - Expected `https://` but received `http://`

**Cause**: Pretalx is generating HTTP redirect URIs instead of HTTPS behind a reverse proxy.

**Solution**: Configure HTTPS detection:

1. **Set HTTPS URL** in `pretalx.cfg`:
   ```ini
   [site]
   url = https://your-domain.com
   ```

2. **Enable proxy trust**:
   ```ini
   trust_x_forwarded_proto = true
   trust_x_forwarded_for = true
   secure_proxy_ssl_header = true
   use_x_forwarded_host = true
   ```

3. **Force HTTPS redirects** (plugin-level):
   ```ini
   [oidc]
   force_https_redirect = true
   ```

4. **Configure reverse proxy** to send proper headers:
   - Caddy: Automatic
   - Nginx: `proxy_set_header X-Forwarded-Proto $scheme;`
   - Apache: `RequestHeader set X-Forwarded-Proto "https"`

5. **Restart pretalx**: `docker compose restart pretalx`

**Verify**: Check that OIDC init URL generates HTTPS callback:
```bash
curl -I https://your-domain.com/oidc/init/
# Location header should contain https://your-domain.com/oidc/callback/
```

### User not created on first login

- Check OIDC provider returns `email` claim in the ID token
- Verify client ID and secret are correct in `pretalx.cfg`
- Check logs for authentication errors: `docker compose logs pretalx | grep OIDC`

### Finding user's OIDC sub claim

Check Docker logs after a successful login:
```bash
docker compose logs pretalx | grep "sub="
```

Or use the Django shell:
```bash
docker compose exec pretalx python manage.py shell
>>> from pretalx.person.models import User
>>> user = User.objects.get(email="user@example.com")
>>> user.oidc_id  # This is the 'sub' claim
```

## Quick Reference

### Common Tasks

**Enable plugin for a new event:**
1. Create event in pretalx
2. Go to `/orga/event/{event-slug}/settings/plugins`
3. Enable "OIDC Authentication"
4. Save

**Add admin user:**
1. Edit `pretalx.cfg`: Add email to `admin_users`
2. Restart container: `docker compose restart pretalx`
3. User gets admin access on next OIDC login (automatic)

**Remove admin user:**
1. Edit `pretalx.cfg`: Remove email from `admin_users`  
2. Restart container: `docker compose restart pretalx`
3. User loses admin access on next OIDC login (automatic)

**Promote to superuser:**
1. Edit `pretalx.cfg`: Move email from `admin_users` to `superuser`
2. Restart container: `docker compose restart pretalx`
3. User gets superuser access on next OIDC login (automatic)

**Check user privileges:**
```bash
# Django shell
docker compose exec pretalx python manage.py shell
>>> from pretalx.person.models import User
>>> user = User.objects.get(email="user@example.com")
>>> print(f"Staff: {user.is_staff}, Superuser: {user.is_superuser}")
>>> from pretalx.event.models import Team
>>> admin_teams = Team.objects.filter(members=user, can_create_events=True)
>>> print(f"Admin teams: {admin_teams.count()}")
```

**View logs:**
```bash
# All services
docker compose logs -f

# Just pretalx
docker compose logs -f pretalx

# Search for OIDC-related logs
docker compose logs pretalx | grep OIDC
```

**View admin dashboard:**
- Regular admin: `https://your-domain.com/orga/`
- Django admin (superusers only): `https://your-domain.com/admin/`

**Check email functionality:**
- MailHog web UI: `http://localhost:8025` (or your configured mail domain)
- SMTP server: `mailhog:1025` (from containers)

**Restart services:**
```bash
# All services
docker compose restart

# Just pretalx
docker compose restart pretalx

# Rebuild and restart
docker compose up -d --build
```

### Configuration Quick Reference

```ini
[site]
url = https://your-domain.com              # Your actual domain
debug = false                              # true for development

# HTTPS proxy settings (required for production)
trust_x_forwarded_proto = true
trust_x_forwarded_for = true
secure_proxy_ssl_header = true
use_x_forwarded_host = true

[oidc]
op_discovery_endpoint = https://provider/.well-known/openid-configuration
rp_client_id = your-client-id
rp_client_secret = your-secret
provider_name = Your SSO Provider
hide_password_form = true                  # Hide password login
force_https_redirect = true                # Force HTTPS callback URLs
admin_users = admin@example.com            # Comma-separated
superuser = super@example.com              # Comma-separated

[mail]
from = noreply@your-domain.com
host = smtp.provider.com
port = 587
user = smtp-user
password = smtp-password
tls = true
```

## Development

### Modifying the Plugin

To modify the OIDC plugin:

1. Edit files in `pretalx-oidc-plugin/pretalx_oidc/`
2. **For rapid iteration** (no rebuild needed):
   ```bash
   # Copy updated file to running container
   docker cp pretalx-oidc-plugin/pretalx_oidc/signals.py pretalx-oidc:/pretalx-oidc/pretalx_oidc/signals.py
   # Django auto-reload will pick up changes
   ```
3. **For permanent changes**, rebuild:
   ```bash
   docker compose build pretalx
   docker compose up -d
   ```

### Enable Debug Logging

Edit `pretalx.cfg`:
```ini
[site]
debug = true
```

Then check logs:
```bash
docker compose logs -f pretalx
```

### Accessing Django Shell

```bash
docker compose exec pretalx python manage.py shell
```

### Rebuilding Static Files

```bash
docker compose exec pretalx python manage.py rebuild
```

### Running Migrations

```bash
docker compose exec pretalx python manage.py migrate
```

## CI/CD

This project includes GitHub Actions workflows for continuous integration:

### Docker Build & Test (`.github/workflows/docker-build.yml`)

Automatically runs on push and pull requests:

1. **Builds the Docker image** - Verifies the image builds successfully
2. **Tests plugin installation** - Ensures pretalx-oidc plugin is installed correctly
3. **Security scanning** - Uses Trivy to scan for vulnerabilities
4. **Integration tests** - Starts docker-compose stack and verifies services run
5. **Publishes to GHCR** - Pushes images to GitHub Container Registry (on main branch)

**Image tags published:**
- `ghcr.io/harrykodden/pretalx-oidc-deployment:latest` - Latest main branch
- `ghcr.io/harrykodden/pretalx-oidc-deployment:main` - Main branch builds
- `ghcr.io/harrykodden/pretalx-oidc-deployment:v*` - Version tags
- `ghcr.io/harrykodden/pretalx-oidc-deployment:sha-<commit>` - Specific commits

### Code Quality (`.github/workflows/lint.yml`)

Runs linting and code quality checks:

1. **Black** - Code formatting verification
2. **isort** - Import statement ordering
3. **flake8** - Python linting and style checks
4. **Config validation** - Validates INI configuration files

To run the same checks locally before pushing:

1. `python3 -m venv .venv-lint && source .venv-lint/bin/activate`
2. `python -m pip install --upgrade pip`
3. `pip install black isort flake8`
4. `black --check --diff pretalx-oidc-plugin/pretalx_oidc/`
5. `isort --check-only --diff --profile black pretalx-oidc-plugin/pretalx_oidc/`
6. `flake8 pretalx-oidc-plugin/pretalx_oidc/ --count --select=E9,F63,F7,F82 --show-source --statistics`
7. `flake8 pretalx-oidc-plugin/pretalx_oidc/ --count --exit-zero --max-complexity=10 --max-line-length=120 --statistics`
8. `python -c "import configparser; c = configparser.ConfigParser(); c.read('pretalx.cfg.example')"`
9. `deactivate`

### Using Pre-Built Images

Instead of building locally, you can use pre-built images from GHCR:

```yaml
# docker-compose.yml
services:
  pretalx:
    image: ghcr.io/harrykodden/pretalx-oidc-deployment:latest
    # ... rest of configuration
```

Or pull directly:
```bash
docker pull ghcr.io/harrykodden/pretalx-oidc-deployment:latest
```

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

The OIDC plugin (`pretalx-oidc-plugin/`) is provided as-is for use with pretalx.

[Pretalx](https://pretalx.com) itself is licensed under the Apache License 2.0.

## Contributing

Contributions are welcome! To contribute:

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test with a local deployment
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

Please ensure:
- Code follows pretalx plugin best practices
- No modifications to pretalx core files
- Changes use Django signals for integration
- Documentation is updated

## Support

For issues related to:

- **This OIDC plugin or deployment**: [Open an issue](https://github.com/HarryKodden/pretalx-oidc-deployment/issues) in this repository
- **Pretalx core functionality**: See [pretalx documentation](https://docs.pretalx.org)
- **OIDC provider configuration**: Consult your provider's documentation
  - [Keycloak](https://www.keycloak.org/documentation)
  - [Auth0](https://auth0.com/docs)
  - [Azure AD](https://docs.microsoft.com/azure/active-directory/)

## Acknowledgments

This project builds upon:

- **[pretalx](https://pretalx.com)** - Conference planning tool
- **[mozilla-django-oidc](https://github.com/mozilla/mozilla-django-oidc)** - Mozilla - OIDC authentication library for Django
- **[pretalx plugin system](https://docs.pretalx.org/developer/plugins/)** - Official plugin architecture

## Project Status

Currently deployed and tested with:
- Keycloak 24+
- PostgreSQL 14
- Python 3.10
- Pretalx v2025.2.0.dev0

Tested OIDC providers:
- ✅ Keycloak
- ✅ SURFconext

## Roadmap

Potential future enhancements:

- [ ] Automated tests for plugin
- [ ] Support for OIDC group-based role mapping
- [ ] Alternative to CSS-based form hiding (middleware or template tags)
- [ ] Documentation for additional OIDC providers
- [ ] Health check endpoints

Contributions for any of these are welcome!
