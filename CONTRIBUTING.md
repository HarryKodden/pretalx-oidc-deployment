# Contributing to Pretalx OIDC Deployment

Thank you for considering contributing to this project!

## How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Test your changes**: Build and test with `docker-compose`
5. **Commit your changes**: Use clear commit messages
6. **Push to your fork**: `git push origin feature/your-feature-name`
7. **Submit a pull request**

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/pretalx-oidc-deployment.git
cd pretalx-oidc-deployment

# Create pretalx.cfg from example
cp pretalx.cfg.example pretalx.cfg
# Edit pretalx.cfg with your OIDC settings

# Build and run
docker-compose build
docker-compose up
```

## Testing Changes

After making changes to the plugin:

```bash
# Rebuild and restart
docker-compose build
docker-compose down
docker-compose up -d

# Check logs
docker-compose logs -f
```

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Update documentation for user-facing changes

## Reporting Issues

When reporting issues, please include:

- Your OIDC provider (Keycloak, Auth0, etc.)
- Relevant configuration (with secrets removed)
- Error messages from logs
- Steps to reproduce

## Pull Request Guidelines

- Keep PRs focused on a single feature or bug fix
- Update README.md if adding new features
- Update pretalx.cfg.example if adding configuration options
- Test with at least one OIDC provider

## Questions?

Feel free to open an issue for questions or discussions!
