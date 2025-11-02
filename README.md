# Pretalx with OIDC Authentication

A complete deployment setup for [pretalx](https://pretalx.com) with OpenID Connect (OIDC) authentication support. This repository provides a Docker-based deployment that enables OIDC-only authentication, hiding traditional password-based login.

## Features

✨ **OIDC Authentication**
- Single Sign-On (SSO) via OpenID Connect
- Auto-discovery from OIDC provider's `.well-known/openid-configuration`
- Automatic user creation on first login
- User profile synchronization

🔒 **Security**
- OIDC-only mode (password authentication hidden)
- Admin role assignment via OIDC claims
- CSRF protection for HTTPS deployments

🎨 **User Experience**
- Clean login page with only OIDC button
- Password change sections hidden throughout the application
- Seamless integration with pretalx UI

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
docker-compose build
docker-compose up -d
```

### 4. Access pretalx

Open your browser to the URL configured in `pretalx.cfg` (default: http://localhost:8355)

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

# Admin users (comma-separated list of OIDC 'sub' or email)
admin_users = user-sub-claim-id, admin@example.com
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

### Admin Users

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

To find a user's `sub` claim, check the OIDC token or logs after first login.

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

This deployment includes:

1. **pretalx-oidc plugin** - Custom OIDC authentication backend
2. **Template patches** - Hide password forms throughout the UI
3. **Settings patches** - CSRF and OIDC configuration
4. **Docker setup** - Complete containerized deployment

### Plugin Components

- `pretalx_oidc/auth.py` - OIDC authentication backend with admin role support
- `pretalx_oidc/views.py` - Custom OIDC login/callback handlers
- `pretalx_oidc/signals.py` - Add OIDC button to login page
- `pretalx_oidc/context_processors.py` - Template context for hiding password forms
- `pretalx_oidc/config.py` - OIDC auto-discovery and Django settings configuration

## Troubleshooting

### Login redirects back to login page

- Check that `admin_users` includes your OIDC identifier
- Verify the OIDC callback URL is correctly configured
- Check Docker logs: `docker-compose logs -f`

### CSRF errors on logout

- Ensure `url` in `[site]` matches your actual domain
- For HTTPS, set `trust_x_forwarded_proto = true`

### User not created

- Check OIDC provider returns `email` claim
- Verify `hide_password_form = true` is set
- Check logs for authentication errors

### Finding user's sub claim

Check Docker logs after login:
```bash
docker-compose logs | grep "sub="
```

## Development

To modify the plugin:

1. Edit files in `pretalx-oidc/pretalx_oidc/`
2. Rebuild: `docker-compose build`
3. Restart: `docker-compose restart`

Enable debug logging:
```ini
[site]
debug = true
```

## License

This OIDC plugin is provided as-is for use with pretalx. See LICENSE file.

Pretalx itself is licensed under the Apache License 2.0.

## Contributing

Contributions welcome! Please:

1. Fork this repository
2. Create a feature branch
3. Submit a pull request

## Support

For issues related to:
- **OIDC plugin**: Open an issue in this repository
- **Pretalx core**: See [pretalx documentation](https://docs.pretalx.org)
- **OIDC providers**: Consult your provider's documentation

## Credits

- [pretalx](https://pretalx.com) - Conference planning tool
- [mozilla-django-oidc](https://github.com/mozilla/mozilla-django-oidc) - OIDC library
