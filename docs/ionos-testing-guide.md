# IONOS Compatibility Testing Guide

## Overview

This guide provides comprehensive instructions for testing ai-zerolab/mcp-email-server compatibility with IONOS email servers.

## Prerequisites

### 1. IONOS Email Account
- Active IONOS email account
- IMAP/SMTP access enabled
- Account credentials (email and password)

### 2. Development Environment
```bash
# Clone the repository
git clone https://github.com/jane-alesi/satai-mcp-mail.git
cd satai-mcp-mail

# Switch to testing branch
git checkout feature/ionos-compatibility-testing

# Set up virtual environment
uv venv venv-ionos-test
source venv-ionos-test/bin/activate

# Install dependencies
uv pip install -e . --group dev
```

## Configuration

### 1. Environment Variables
Copy and customize the environment file:
```bash
cp .env.ionos-test .env.ionos-test.local
```

Edit `.env.ionos-test.local` with your IONOS credentials:
```bash
export IONOS_TEST_EMAIL="your-email@yourdomain.com"
export IONOS_TEST_PASSWORD="your-secure-password"
export IONOS_TEST_FULL_NAME="Your Name"
```

### 2. Configuration File
Copy and customize the configuration file:
```bash
cp config-ionos-test.toml config-ionos-test.local.toml
```

Update the email addresses and credentials in the configuration file.

### 3. Load Environment
```bash
source .env.ionos-test.local
```

## Running Tests

### Basic Connectivity Tests
```bash
# Run all IONOS compatibility tests
pytest tests/test_ionos_compatibility.py -v

# Run specific test categories
pytest tests/test_ionos_compatibility.py::TestIONOSCompatibility -v
pytest tests/test_ionos_compatibility.py::TestIONOSPerformance -v

# Run with detailed logging
pytest tests/test_ionos_compatibility.py -v -s --log-cli-level=DEBUG
```

### Individual Test Components

#### IMAP Connection Test
```bash
pytest tests/test_ionos_compatibility.py::TestIONOSCompatibility::test_imap_connection_basic -v
```

#### SMTP Connection Tests
```bash
# STARTTLS (Port 587)
pytest tests/test_ionos_compatibility.py::TestIONOSCompatibility::test_smtp_connection_starttls -v

# SSL (Port 465)
pytest tests/test_ionos_compatibility.py::TestIONOSCompatibility::test_smtp_connection_ssl -v
```

#### Folder Operations Test
```bash
pytest tests/test_ionos_compatibility.py::TestIONOSCompatibility::test_imap_folder_operations -v
```

#### Performance Tests
```bash
pytest tests/test_ionos_compatibility.py::TestIONOSPerformance::test_connection_latency -v
```

## IONOS Server Configuration

### IMAP Settings
- **Server**: imap.ionos.com
- **Port**: 993
- **Encryption**: SSL/TLS
- **Authentication**: Normal password

### SMTP Settings
- **Server**: smtp.ionos.com
- **Port**: 587 (STARTTLS) or 465 (SSL)
- **Encryption**: STARTTLS or SSL
- **Authentication**: Normal password

## Expected Test Results

### ✅ Successful Tests Should Show:
- IMAP connection establishment
- SMTP authentication (both STARTTLS and SSL)
- Folder listing and selection
- Email search operations
- Connection latency < 10 seconds

### ⚠️ Common Issues and Solutions

#### Authentication Failures
- Verify email address and password
- Check if IMAP/SMTP is enabled in IONOS settings
- Ensure using full email address as username

#### Connection Timeouts
- Check network connectivity
- Verify firewall settings
- Test from different network if needed

#### SSL/TLS Errors
- Update Python SSL certificates
- Check system time synchronization
- Verify IONOS server certificates

## Manual Testing

### Test IMAP Connection Manually
```python
import asyncio
from aioimaplib import IMAP4_SSL

async def test_imap():
    imap = IMAP4_SSL('imap.ionos.com', 993)
    await imap.wait_hello_from_server()
    await imap.login('your-email@domain.com', 'password')
    await imap.select('INBOX')
    messages = await imap.search('ALL')
    print(f"Found {len(messages)} messages")
    await imap.logout()

asyncio.run(test_imap())
```

### Test SMTP Connection Manually
```python
import asyncio
from aiosmtplib import SMTP

async def test_smtp():
    smtp = SMTP('smtp.ionos.com', 587, start_tls=True)
    await smtp.connect()
    await smtp.starttls()
    await smtp.login('your-email@domain.com', 'password')
    print("SMTP connection successful")
    await smtp.quit()

asyncio.run(test_smtp())
```

## Integration with MCP Server

### Test MCP Server with IONOS
```bash
# Start MCP server with IONOS config
MCP_EMAIL_SERVER_CONFIG_PATH="./config-ionos-test.local.toml" mcp-email-server stdio
```

### Test Tools via MCP Protocol
The following MCP tools should work with IONOS:
- `list_folders`: List email folders
- `read_email`: Read email content
- `send_email`: Send emails via SMTP
- `search_emails`: Search for emails

## Troubleshooting

### Debug Mode
Enable debug logging for detailed troubleshooting:
```bash
export MCP_EMAIL_SERVER_LOG_LEVEL="DEBUG"
pytest tests/test_ionos_compatibility.py -v -s --log-cli-level=DEBUG
```

### Network Diagnostics
```bash
# Test IMAP connectivity
telnet imap.ionos.com 993

# Test SMTP connectivity
telnet smtp.ionos.com 587
telnet smtp.ionos.com 465
```

### SSL Certificate Issues
```bash
# Check SSL certificate
openssl s_client -connect imap.ionos.com:993 -servername imap.ionos.com
openssl s_client -connect smtp.ionos.com:587 -starttls smtp -servername smtp.ionos.com
```

## Reporting Issues

When reporting issues, include:
1. Test output with debug logging
2. IONOS account type and region
3. Network environment details
4. Python and dependency versions
5. Operating system information

## Security Notes

- Never commit actual credentials to version control
- Use environment variables for sensitive data
- Consider using app-specific passwords if available
- Regularly rotate test credentials
- Test in isolated environment first

## Performance Benchmarks

Expected performance metrics:
- IMAP connection: < 3 seconds
- SMTP connection: < 2 seconds
- Message retrieval: 50-100 messages/second
- Email sending: 10-20 emails/second (respecting IONOS limits)

## Next Steps

After successful testing:
1. Document any IONOS-specific configurations
2. Create production configuration templates
3. Implement monitoring and alerting
4. Set up automated testing pipeline
5. Prepare deployment documentation