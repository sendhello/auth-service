# Security Policy

## Supported Versions

We actively support security updates for the following versions of the Auth Service:

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

The RooRoute Auth Service team takes security vulnerabilities seriously. We appreciate your efforts to responsibly disclose your findings.

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities by emailing:
- **Primary Contact**: [bazhenov.in@gmail.com](mailto:bazhenov.in@gmail.com)
- **Subject**: `[SECURITY] Auth Service Vulnerability Report`

### What to Include

When reporting a vulnerability, please include the following information:
- **Description**: A clear description of the vulnerability
- **Impact**: The potential impact and severity of the issue
- **Steps to Reproduce**: Detailed steps to reproduce the vulnerability
- **Proof of Concept**: If applicable, include a proof of concept
- **Suggested Fix**: If you have suggestions for how to fix the issue
- **Environment**: Version information and environment details

### Response Timeline

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
- **Initial Assessment**: We will provide an initial assessment within 5 business days
- **Status Updates**: We will keep you informed of our progress throughout the investigation
- **Resolution**: We aim to resolve critical vulnerabilities within 30 days

### Security Best Practices

When using the Auth Service, we recommend following these security best practices:

#### Environment Configuration
- Use strong, unique secrets for `AUTHJWT_SECRET_KEY`
- Never commit secrets to version control
- Use environment-specific configuration files
- Enable HTTPS in production environments
- Regularly rotate JWT secrets and API keys

#### Database Security
- Use dedicated database users with minimal privileges
- Enable database connection encryption
- Regularly update PostgreSQL and Redis versions
- Monitor database access logs

#### Rate Limiting
- Configure appropriate rate limits based on your use case
- Monitor for suspicious activity patterns
- Implement progressive delays for repeated failed attempts

#### OAuth Security
- Use HTTPS-only redirect URIs for OAuth flows
- Validate OAuth state parameters
- Regularly review OAuth application permissions

#### Token Management
- Use short-lived access tokens (default: 15 minutes)
- Implement proper token revocation
- Monitor for token replay attacks
- Store refresh tokens securely

#### Infrastructure Security
- Keep Docker images updated
- Use non-root users in containers
- Enable container security scanning
- Implement proper network segmentation

### Known Security Considerations

- **JWT Tokens**: Tokens are stateless by design. Ensure proper token expiration and rotation
- **Rate Limiting**: Default rate limit is 20 requests/minute. Adjust based on your needs
- **Password Storage**: Uses Argon2 for secure password hashing
- **Session Management**: Redis-based session storage with proper expiration
- **OAuth Integration**: Google OAuth is implemented with proper state validation

### Security Features

The Auth Service includes several built-in security features:
- **Argon2 Password Hashing**: Industry-standard password hashing
- **JWT Token Blacklisting**: Ability to revoke tokens before expiration
- **Rate Limiting**: Configurable request throttling
- **Login History Tracking**: Audit trail for authentication events
- **Multi-Factor Authentication Ready**: Architecture supports MFA implementation
- **Secure Headers**: Proper security headers in responses
- **Input Validation**: Comprehensive input validation using Pydantic

### Responsible Disclosure

We follow responsible disclosure practices:
- We will work with you to understand and resolve the issue
- We will not take legal action against researchers who follow this policy
- We will credit researchers who report valid vulnerabilities (unless they prefer to remain anonymous)
- We may publish security advisories after issues are resolved

### Bug Bounty

Currently, we do not have a formal bug bounty program, but we greatly appreciate security researchers who help us improve the security of our service.

## Contact

For non-security related issues, please use GitHub issues or contact the maintainer through standard channels.

For urgent security matters outside of vulnerability reports, you can also reach out via:
- GitHub: [@sendhello](https://github.com/sendhello)
- Email: [bazhenov.in@gmail.com](mailto:bazhenov.in@gmail.com)

---

*Last updated: August 2025*