# Pretalx OIDC Authentication Plugin

This plugin provides OpenID Connect (OIDC) authentication for pretalx.

## Installation

1. Install the plugin:
   ```bash
   cd /path/to/pretalx/src/pretalx-oidc
   pip install -e .
   ```

2. Add the authentication backend to your `pretalx.cfg`:
   ```ini
   [authentication]
   additional_auth_backends=pretalx_oidc.auth.PretalxOIDCBackend
   ```

3. Configure OIDC settings in your `pretalx.cfg`:
   ```ini
   [oidc]
   # OIDC Provider configuration
   rp_client_id=your-client-id
   rp_client_secret=your-client-secret
   op_authorization_endpoint=https://your-provider.com/authorize
   op_token_endpoint=https://your-provider.com/token
   op_user_endpoint=https://your-provider.com/userinfo
   op_jwks_endpoint=https://your-provider.com/jwks
   
   # Optional settings
   provider_name=YourProvider
   rp_sign_algo=RS256
   rp_scopes=openid email profile
   ```

4. Run migrations:
   ```bash
   python manage.py migrate pretalx_oidc
   ```

5. Restart pretalx

## Configuration

### Required Settings

- `rp_client_id`: Your OIDC client ID
- `rp_client_secret`: Your OIDC client secret
- `op_authorization_endpoint`: OIDC provider's authorization endpoint
- `op_token_endpoint`: OIDC provider's token endpoint
- `op_user_endpoint`: OIDC provider's userinfo endpoint

### Optional Settings

- `op_jwks_endpoint`: OIDC provider's JWKS endpoint (for token verification)
- `provider_name`: Display name for the OIDC provider (default: "oidc")
- `rp_sign_algo`: Signature algorithm (default: "RS256")
- `rp_scopes`: Space-separated list of scopes (default: "openid email profile")

### Example Configurations

#### Keycloak
```ini
[oidc]
rp_client_id=pretalx
rp_client_secret=your-secret
op_authorization_endpoint=https://keycloak.example.com/realms/master/protocol/openid-connect/auth
op_token_endpoint=https://keycloak.example.com/realms/master/protocol/openid-connect/token
op_user_endpoint=https://keycloak.example.com/realms/master/protocol/openid-connect/userinfo
op_jwks_endpoint=https://keycloak.example.com/realms/master/protocol/openid-connect/certs
provider_name=Keycloak
```

#### Azure AD
```ini
[oidc]
rp_client_id=your-app-id
rp_client_secret=your-secret
op_authorization_endpoint=https://login.microsoftonline.com/your-tenant-id/oauth2/v2.0/authorize
op_token_endpoint=https://login.microsoftonline.com/your-tenant-id/oauth2/v2.0/token
op_user_endpoint=https://graph.microsoft.com/oidc/userinfo
op_jwks_endpoint=https://login.microsoftonline.com/your-tenant-id/discovery/v2.0/keys
provider_name=Microsoft
```

## Features

- **Seamless Integration**: Adds "Sign in with OIDC" button to all login pages
- **Account Linking**: Automatically links OIDC accounts to existing pretalx accounts by email
- **User Creation**: Creates new users automatically from OIDC claims
- **Profile Sync**: Updates user names from OIDC provider
- **Secure**: Uses industry-standard OIDC protocol
- **Configurable**: Flexible configuration for different OIDC providers

## Usage

Once configured, users will see a "Sign in with OIDC" button on login pages. Clicking this will redirect them to your OIDC provider for authentication.

## Troubleshooting

### Login fails
- Check your client ID and secret
- Verify all endpoint URLs are correct
- Ensure your redirect URI is registered with your OIDC provider
  - The callback URL is: `https://your-pretalx.com/plugins/pretalx_oidc/oidc/callback/`

### Users not created
- Check that your OIDC provider returns an `email` claim
- Verify the `sub` claim is present (required for user identification)

### Name not updated
- Ensure your OIDC provider returns a `name` or `preferred_username` claim

## License

Apache License 2.0
