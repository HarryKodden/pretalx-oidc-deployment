# CI/CD Setup Guide

This document explains the Continuous Integration and Continuous Deployment (CI/CD) setup for the pretalx-oidc-deployment project.

## Overview

The project uses **GitHub Actions** for CI/CD with two main workflows:

1. **Docker Build & Test** - Builds, tests, and publishes Docker images
2. **Lint & Code Quality** - Ensures code quality and formatting standards

## Workflows

### 1. Docker Build & Test (`.github/workflows/docker-build.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main`
- Version tags (`v*`)

**Jobs:**

#### Build and Test Job
1. **Checkout** - Clones the repository
2. **Docker Buildx** - Sets up advanced Docker build features
3. **Login to GHCR** - Authenticates with GitHub Container Registry (only on push, not PR)
4. **Extract Metadata** - Generates Docker image tags from Git refs
5. **Build Image** - Builds the Docker image with caching
6. **Test Build** - Verifies the image was created successfully
7. **Verify Plugin** - Confirms pretalx-oidc plugin is installed
8. **Security Scan** - Uses Trivy to scan for vulnerabilities
9. **Upload Scan Results** - Uploads security findings to GitHub Security tab
10. **Push to GHCR** - Publishes image to GitHub Container Registry (only on push)

#### Integration Test Job
1. **Create Test Config** - Generates a test configuration file
2. **Start Services** - Launches PostgreSQL, Redis, and MailHog
3. **Build Pretalx** - Builds and starts the pretalx container
4. **Health Checks** - Verifies all services are running
5. **Log Verification** - Checks for critical errors in logs
6. **Cleanup** - Tears down the test environment

**Published Images:**

Images are pushed to `ghcr.io/harrykodden/pretalx-oidc-deployment` with multiple tags:

- `latest` - Latest build from main branch
- `main` - All builds from main branch
- `develop` - Builds from develop branch
- `v1.2.3` - Semantic version tags
- `v1.2` - Major.minor version tags
- `main-sha-abc123` - Specific commit SHA

**Security Scanning:**

The workflow uses [Trivy](https://github.com/aquasecurity/trivy) to scan for:
- Known vulnerabilities (CVEs)
- Misconfigurations
- Exposed secrets
- License issues

Results are uploaded to GitHub's Security tab under "Code scanning alerts."

### 2. Lint & Code Quality (`.github/workflows/lint.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main`

**Checks:**

1. **Black** - Ensures Python code follows formatting standards
   - Line length: Default (88 characters)
   - Style: PEP 8 compliant

2. **isort** - Verifies import statement ordering
   - Groups: stdlib, third-party, first-party
   - Style: Black-compatible

3. **flake8** - Lints Python code
   - Critical: Syntax errors, undefined names (fails build)
   - Warnings: Style issues, complexity (informational)
   - Max line length: 120 characters
   - Max complexity: 10

4. **Config Validation** - Validates INI files
   - Ensures pretalx.cfg.example is valid

## Using Pre-Built Images

### Pull from GitHub Container Registry

Instead of building locally, use pre-built images:

```bash
# Pull latest
docker pull ghcr.io/harrykodden/pretalx-oidc-deployment:latest

# Pull specific version
docker pull ghcr.io/harrykodden/pretalx-oidc-deployment:v1.0.0

# Pull specific commit
docker pull ghcr.io/harrykodden/pretalx-oidc-deployment:main-sha-abc123
```

### Update docker-compose.yml

```yaml
services:
  pretalx:
    image: ghcr.io/harrykodden/pretalx-oidc-deployment:latest
    # Remove the 'build: .' line
    # ... rest of configuration
```

### Authentication

For private repositories, authenticate with GHCR:

```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

## Local Development

### Running Linters Locally

Install dependencies:
```bash
pip install black isort flake8
```

Run checks:
```bash
# Format check
black --check pretalx-oidc-plugin/pretalx_oidc/

# Auto-format
black pretalx-oidc-plugin/pretalx_oidc/

# Import ordering
isort --check-only pretalx-oidc-plugin/pretalx_oidc/
isort pretalx-oidc-plugin/pretalx_oidc/

# Linting
flake8 pretalx-oidc-plugin/pretalx_oidc/ --max-line-length=120
```

### Testing Docker Build Locally

```bash
# Build
docker build -t pretalx-oidc:test .

# Test plugin installation
docker run --rm pretalx-oidc:test pip list | grep pretalx-oidc

# Scan for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image pretalx-oidc:test
```

## Secrets and Configuration

### Required Secrets

The workflows use the following secrets (automatically provided by GitHub):

- `GITHUB_TOKEN` - Auto-generated for each workflow run
  - Used for: GHCR authentication, uploading scan results

### No Additional Secrets Needed

The CI workflows don't require any additional secrets because:
- They use GitHub's built-in `GITHUB_TOKEN`
- No external services are configured
- Test environment uses mock/example configurations

## Customization

### Adding Test Environments

To test against real OIDC providers, add secrets:

```yaml
- name: Test with real OIDC
  env:
    OIDC_CLIENT_ID: ${{ secrets.OIDC_TEST_CLIENT_ID }}
    OIDC_CLIENT_SECRET: ${{ secrets.OIDC_TEST_CLIENT_SECRET }}
```

### Changing Image Registry

To use Docker Hub instead of GHCR:

```yaml
env:
  REGISTRY: docker.io
  IMAGE_NAME: username/pretalx-oidc
```

Then add Docker Hub credentials as secrets.

### Deployment Workflows

To add automatic deployment (e.g., to production):

```yaml
deploy:
  needs: build-and-test
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/main'
  steps:
    - name: Deploy to production
      run: |
        # Your deployment commands
        ssh user@server "docker pull ghcr.io/.../pretalx-oidc:latest && docker-compose up -d"
```

## Monitoring

### Workflow Status

- **GitHub Actions Tab** - View all workflow runs
- **Branch Protection** - Require CI to pass before merging
- **Status Badges** - Show build status in README

### Security Alerts

- **Security Tab** - View Trivy scan results
- **Dependabot** - Automatic dependency updates
- **Code Scanning** - CVE and security issue tracking

## Best Practices

1. **Always run linters** before committing code
2. **Test Docker builds locally** before pushing
3. **Review security scan results** in the Security tab
4. **Use semantic versioning** for releases (v1.2.3)
5. **Pin image versions** in production deployments
6. **Monitor workflow runs** for failures

## Troubleshooting

### Build Failures

Check the Actions tab for detailed logs:
```
GitHub UI → Actions → Failed Workflow → Click on job → Expand failing step
```

### GHCR Authentication Issues

Ensure the repository has the correct permissions:
```
Settings → Actions → General → Workflow permissions → Read and write permissions
```

### Cache Issues

Clear Docker build cache:
```bash
docker builder prune --all
```

Or in workflows, add to build step:
```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
no-cache: true  # Disable cache
```

## Further Reading

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Trivy Security Scanner](https://github.com/aquasecurity/trivy)
- [Docker Build Best Practices](https://docs.docker.com/develop/dev-best-practices/)
