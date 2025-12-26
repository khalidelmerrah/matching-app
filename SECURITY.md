# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

Please report vulnerabilities privately via email to security@example.com (replace with actual).

**Do NOT report security vulnerabilities via public GitHub issues.**

## Secret Management
- **NO SECRETS IN CODE**: Never commit API keys, passwords, or tokens.
- Use `.env` files for local development (gitignored).
- Use GitHub Secrets or a secret manager for production/CI.
- **Scanning**: We recommend enabling GitHub Secret Scanning on the repository.
- **Pre-commit hooks**: Consider using `detect-secrets` or similar tools pre-commit.

