# Pretalx OIDC Deployment Repository

## ✅ Repository Created Successfully!

**Location**: `/Users/kodde001/Projects/pretalx-oidc-deployment`

## 📦 What's Included

### Core Plugin
- **pretalx-oidc/** - Complete OIDC authentication plugin
  - Auto-discovery from OIDC provider
  - User creation and synchronization
  - Admin role assignment
  - Password authentication hiding

### Deployment Files
- **Dockerfile** - Multi-stage build with all patches applied
- **docker-compose.yml** - Complete deployment with Redis
- **patch_*.py** - Template and settings patches
- **pretalx.cfg.example** - Comprehensive configuration example
- **quickstart.sh** - One-command deployment script

### Documentation
- **README.md** - Complete user guide with examples
- **CONTRIBUTING.md** - Contribution guidelines
- **LICENSE** - Apache 2.0 license

## 🚀 Quick Start

```bash
cd /Users/kodde001/Projects/pretalx-oidc-deployment

# 1. Create configuration
cp pretalx.cfg.example pretalx.cfg
# Edit pretalx.cfg with your OIDC settings

# 2. Run
./quickstart.sh

# Or manually:
docker-compose build
docker-compose up -d
```

## 📋 Configuration Required

Edit `pretalx.cfg` and set:

1. **Site URL**: Match your domain
2. **OIDC Provider**:
   - `op_discovery_endpoint`
   - `rp_client_id`
   - `rp_client_secret`
3. **Admin Users** (optional):
   - Add OIDC `sub` or emails

## 🔧 Features

✅ OIDC-only authentication (password login hidden)
✅ Auto-discovery from `.well-known/openid-configuration`
✅ Automatic user creation on first login
✅ Admin role assignment via configuration
✅ Works with Keycloak, Auth0, Azure AD, Okta, Google, etc.
✅ Complete Docker deployment
✅ CSRF protection for HTTPS
✅ Production-ready

## 📚 Next Steps

### 1. Initialize Your Git Remote

```bash
cd /Users/kodde001/Projects/pretalx-oidc-deployment

# Add your remote repository
git remote add origin https://github.com/yourusername/pretalx-oidc-deployment.git

# Push to GitHub/GitLab
git push -u origin main
```

### 2. Test Locally

```bash
# Configure with your OIDC provider
cp pretalx.cfg.example pretalx.cfg
nano pretalx.cfg

# Start
./quickstart.sh

# Access at http://localhost:8355
```

### 3. Deploy to Production

- Update `pretalx.cfg` with production URLs
- Configure HTTPS (reverse proxy recommended)
- Set up persistent volumes
- Configure backups

## 📁 Repository Structure

```
pretalx-oidc-deployment/
├── pretalx-oidc/              # OIDC plugin
│   ├── pretalx_oidc/
│   │   ├── __init__.py
│   │   ├── auth.py           # OIDC backend with admin support
│   │   ├── views.py          # Login/callback handlers
│   │   ├── signals.py        # OIDC button injection
│   │   ├── config.py         # Auto-discovery
│   │   ├── context_processors.py
│   │   ├── models.py         # OIDCUserProfile
│   │   └── urls.py
│   └── setup.py
├── Dockerfile                 # Complete build with patches
├── docker-compose.yml         # Deployment configuration
├── patch_*.py                 # Template/settings patches
├── pretalx.cfg.example        # Configuration template
├── quickstart.sh              # Quick start script
├── README.md                  # User documentation
├── CONTRIBUTING.md            # Contribution guide
└── LICENSE                    # Apache 2.0

```

## 🎯 Key Differences from Original Pretalx Repository

**Before** (full pretalx repo):
- Large repository with entire pretalx source
- Complex to deploy
- No OIDC support

**After** (this repository):
- ✅ Standalone OIDC plugin
- ✅ Docker-first deployment
- ✅ OIDC-only authentication
- ✅ Ready-to-deploy configuration
- ✅ Clones pretalx automatically during build
- ✅ No need to manage pretalx source

## 💡 How It Works

1. **Build Phase** (Dockerfile):
   - Clones pretalx from GitHub
   - Applies template patches to hide password forms
   - Installs OIDC plugin
   - Configures Django settings

2. **Runtime**:
   - Reads configuration from `pretalx.cfg`
   - Auto-discovers OIDC endpoints
   - Provides OIDC-only login
   - Grants admin roles based on configuration

## 🔒 Security Notes

- `pretalx.cfg` is in `.gitignore` (contains secrets)
- Never commit configuration with real credentials
- Use environment variables in production
- Enable HTTPS for production deployments

## 📞 Support

- **Plugin Issues**: Open an issue in this repository
- **Pretalx Issues**: See [pretalx documentation](https://docs.pretalx.org)
- **OIDC Provider**: Consult your provider's documentation

## 🎉 Success!

Your standalone pretalx OIDC deployment repository is ready!

You can now:
1. Push to GitHub/GitLab
2. Share with others
3. Deploy anywhere
4. Contribute improvements

**No need to manage the full pretalx repository anymore!**
