#!/usr/bin/env python3
"""
IONOS Compatibility Test Suite for ai-zerolab/mcp-email-server
satware® AI - Technical Validation
"""

import asyncio
import os
import pytest
from pathlib import Path
import logging
from typing import Optional
import tomllib

# Configure logging for detailed testing
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Test configuration
IONOS_CONFIG = {
    "imap_host": "imap.ionos.com",
    "imap_port": 993,
    "smtp_host": "smtp.ionos.com", 
    "smtp_port": 587,
    "smtp_ssl_port": 465
}

class TestIONOSCompatibility:
    """Comprehensive IONOS compatibility test suite."""
    
    @pytest.fixture
    def ionos_credentials(self):
        """Load IONOS test credentials from environment."""
        email = os.getenv("IONOS_TEST_EMAIL")
        password = os.getenv("IONOS_TEST_PASSWORD")
        
        if not email or not password:
            pytest.skip("IONOS test credentials not configured")
        
        return {
            "email": email,
            "password": password,
            "full_name": os.getenv("IONOS_TEST_FULL_NAME", "Test User")
        }
    
    @pytest.fixture
    def ionos_config(self):
        """Load IONOS configuration from config file."""
        config_path = os.getenv("MCP_EMAIL_SERVER_CONFIG_PATH", "./config-ionos-test.toml")
        
        if not os.path.exists(config_path):
            pytest.skip(f"IONOS config file not found: {config_path}")
        
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
        
        # Find IONOS test account
        ionos_account = None
        for email_config in config.get("emails", []):
            if email_config.get("account_name") == "ionos_test_account":
                ionos_account = email_config
                break
        
        if not ionos_account:
            pytest.skip("IONOS test account not found in config")
        
        return ionos_account
    
    @pytest.mark.asyncio
    async def test_imap_connection_basic(self, ionos_credentials):
        """Test basic IMAP connection to IONOS server."""
        logger.info("Testing basic IMAP connection to IONOS...")
        
        try:
            from aioimaplib import IMAP4_SSL
            
            # Test IMAP connection
            imap = IMAP4_SSL(
                host=IONOS_CONFIG["imap_host"],
                port=IONOS_CONFIG["imap_port"]
            )
            await imap.wait_hello_from_server()
            
            # Test authentication
            await imap.login(
                ionos_credentials["email"],
                ionos_credentials["password"]
            )
            
            # Test basic operations
            await imap.select('INBOX')
            messages = await imap.search('ALL')
            
            logger.info(f"✅ IMAP Test Successful: Connected to {IONOS_CONFIG['imap_host']}")
            logger.info(f"📧 Found {len(messages)} messages in INBOX")
            
            await imap.logout()
            assert True
            
        except Exception as e:
            logger.error(f"❌ IMAP Test Failed: {e}")
            pytest.fail(f"IMAP connection failed: {e}")
    
    @pytest.mark.asyncio
    async def test_smtp_connection_starttls(self, ionos_credentials):
        """Test SMTP connection with STARTTLS to IONOS server."""
        logger.info("Testing SMTP connection with STARTTLS to IONOS...")
        
        try:
            from aiosmtplib import SMTP
            
            # Test SMTP connection with STARTTLS
            smtp = SMTP(
                hostname=IONOS_CONFIG["smtp_host"],
                port=IONOS_CONFIG["smtp_port"],
                use_tls=False,
                start_tls=True
            )
            
            await smtp.connect()
            await smtp.starttls()
            
            # Test authentication
            await smtp.login(
                ionos_credentials["email"],
                ionos_credentials["password"]
            )
            
            logger.info(f"✅ SMTP STARTTLS Test Successful: Connected to {IONOS_CONFIG['smtp_host']}:587")
            
            await smtp.quit()
            assert True
            
        except Exception as e:
            logger.error(f"❌ SMTP STARTTLS Test Failed: {e}")
            pytest.fail(f"SMTP STARTTLS connection failed: {e}")
    
    @pytest.mark.asyncio
    async def test_smtp_connection_ssl(self, ionos_credentials):
        """Test SMTP connection with SSL to IONOS server."""
        logger.info("Testing SMTP connection with SSL to IONOS...")
        
        try:
            from aiosmtplib import SMTP
            
            # Test SMTP connection with SSL
            smtp = SMTP(
                hostname=IONOS_CONFIG["smtp_host"],
                port=IONOS_CONFIG["smtp_ssl_port"],
                use_tls=True,
                start_tls=False
            )
            
            await smtp.connect()
            
            # Test authentication
            await smtp.login(
                ionos_credentials["email"],
                ionos_credentials["password"]
            )
            
            logger.info(f"✅ SMTP SSL Test Successful: Connected to {IONOS_CONFIG['smtp_host']}:465")
            
            await smtp.quit()
            assert True
            
        except Exception as e:
            logger.error(f"❌ SMTP SSL Test Failed: {e}")
            pytest.fail(f"SMTP SSL connection failed: {e}")
    
    @pytest.mark.asyncio
    async def test_imap_folder_operations(self, ionos_credentials):
        """Test IMAP folder operations."""
        logger.info("Testing IMAP folder operations...")
        
        try:
            from aioimaplib import IMAP4_SSL
            
            imap = IMAP4_SSL(
                host=IONOS_CONFIG["imap_host"],
                port=IONOS_CONFIG["imap_port"]
            )
            await imap.wait_hello_from_server()
            await imap.login(ionos_credentials["email"], ionos_credentials["password"])
            
            # Test folder listing
            folders = await imap.list()
            logger.info(f"📁 Available folders: {len(folders)}")
            
            # Test selecting different folders
            common_folders = ['INBOX', 'Sent', 'Drafts', 'Trash']
            for folder in common_folders:
                try:
                    await imap.select(folder)
                    logger.info(f"✅ Successfully selected folder: {folder}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not select folder {folder}: {e}")
            
            await imap.logout()
            assert True
            
        except Exception as e:
            logger.error(f"❌ Folder operations test failed: {e}")
            pytest.fail(f"IMAP folder operations failed: {e}")
    
    @pytest.mark.asyncio
    async def test_email_search_operations(self, ionos_credentials):
        """Test email search operations."""
        logger.info("Testing email search operations...")
        
        try:
            from aioimaplib import IMAP4_SSL
            
            imap = IMAP4_SSL(
                host=IONOS_CONFIG["imap_host"],
                port=IONOS_CONFIG["imap_port"]
            )
            await imap.wait_hello_from_server()
            await imap.login(ionos_credentials["email"], ionos_credentials["password"])
            await imap.select('INBOX')
            
            # Test different search criteria
            search_tests = [
                ('ALL', 'All messages'),
                ('UNSEEN', 'Unread messages'),
                ('RECENT', 'Recent messages'),
                ('FROM "test"', 'Messages from test'),
            ]
            
            for search_criteria, description in search_tests:
                try:
                    messages = await imap.search(search_criteria)
                    logger.info(f"🔍 {description}: {len(messages)} found")
                except Exception as e:
                    logger.warning(f"⚠️ Search '{search_criteria}' failed: {e}")
            
            await imap.logout()
            assert True
            
        except Exception as e:
            logger.error(f"❌ Email search test failed: {e}")
            pytest.fail(f"Email search operations failed: {e}")

# Performance and load testing
class TestIONOSPerformance:
    """Performance testing for IONOS operations."""
    
    @pytest.mark.asyncio
    async def test_connection_latency(self, ionos_credentials):
        """Measure connection establishment time."""
        import time
        
        latencies = []
        for i in range(3):  # Test 3 connections
            start_time = time.time()
            
            try:
                from aioimaplib import IMAP4_SSL
                imap = IMAP4_SSL(
                    host=IONOS_CONFIG["imap_host"],
                    port=IONOS_CONFIG["imap_port"]
                )
                await imap.wait_hello_from_server()
                await imap.login(ionos_credentials["email"], ionos_credentials["password"])
                await imap.logout()
                
                end_time = time.time()
                latency = end_time - start_time
                latencies.append(latency)
                logger.info(f"Connection {i+1} latency: {latency:.2f}s")
                
            except Exception as e:
                logger.error(f"Connection {i+1} failed: {e}")
        
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            logger.info(f"Average connection latency: {avg_latency:.2f}s")
            assert avg_latency < 10.0  # Should connect within 10 seconds
        else:
            pytest.fail("All connection attempts failed")

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])