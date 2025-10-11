"""Comprehensive test suite for config.py module.

This module contains 7 test cases covering:
- Configuration classes (5 tests)
- ConfigManager (2 tests)
"""

import os
import pytest
from unittest.mock import patch
from config import (
    DatabaseConfig,
    SecurityConfig,
    PaymentConfig,
    EmailConfig,
    AppConfig,
    ConfigManager,
    BOOK_CATALOG,
    DISCOUNT_CODES,
    DEMO_USER,
)


# ============================================================================
# Configuration Classes Tests (5 tests)
# ============================================================================


class TestConfigurationClasses:
    """Test suite for configuration dataclasses."""

    def test_database_config_defaults(self):
        """Test DatabaseConfig default values."""
        config = DatabaseConfig()
        assert config.url == "sqlite:///bookstore.db"
        assert config.echo is False
        assert config.pool_size == 5
        assert config.max_overflow == 10

    def test_security_config_defaults(self):
        """Test SecurityConfig default values."""
        config = SecurityConfig()
        assert config.secret_key == "change-me-in-production"
        assert config.password_min_length == 8
        assert config.session_timeout == 3600
        assert config.bcrypt_rounds == 10

    def test_payment_config_defaults(self):
        """Test PaymentConfig default values."""
        config = PaymentConfig()
        assert config.test_mode is True
        assert config.success_rate == 0.95
        assert config.processing_delay == 0.1

    def test_email_config_defaults(self):
        """Test EmailConfig default values."""
        config = EmailConfig()
        assert config.enabled is True
        assert config.smtp_server == "localhost"
        assert config.smtp_port == 587
        assert config.use_tls is True
        assert config.from_email == "noreply@bookstore.com"

    def test_app_config_initialization(self):
        """Test AppConfig initialization with sub-configs."""
        config = AppConfig()
        assert config.debug is True
        assert config.host == "127.0.0.1"
        assert config.port == 5000
        assert isinstance(config.database, DatabaseConfig)
        assert isinstance(config.security, SecurityConfig)
        assert isinstance(config.payment, PaymentConfig)
        assert isinstance(config.email, EmailConfig)


# ============================================================================
# ConfigManager Tests (2 tests)
# ============================================================================


class TestConfigManager:
    """Test suite for ConfigManager class."""

    def test_load_config_with_defaults(self):
        """Test loading config with default values."""
        config = ConfigManager.load_config()
        assert isinstance(config, AppConfig)
        assert config.host == "127.0.0.1"
        assert config.port == 5000

    def test_load_config_with_environment_variables(self):
        """Test loading config with environment variables."""
        with patch.dict(
            os.environ,
            {
                "FLASK_DEBUG": "False",
                "FLASK_HOST": "0.0.0.0",
                "FLASK_PORT": "8000",
                "SECRET_KEY": "test-secret",
            },
        ):
            config = ConfigManager.load_config()
            assert config.debug is False
            assert config.host == "0.0.0.0"
            assert config.port == 8000
            assert config.security.secret_key == "test-secret"


# ============================================================================
# Catalog Configuration Tests (5 tests)
# ============================================================================


class TestCatalogConfiguration:
    """Test suite for catalog configuration data."""

    def test_book_catalog_structure(self):
        """Test BOOK_CATALOG has correct structure."""
        assert isinstance(BOOK_CATALOG, list)
        assert len(BOOK_CATALOG) > 0
        for book in BOOK_CATALOG:
            assert "title" in book
            assert "author" in book
            assert "category" in book
            assert "price" in book
            assert "image_url" in book

    def test_book_catalog_contains_expected_books(self):
        """Test BOOK_CATALOG contains expected books."""
        titles = [book["title"] for book in BOOK_CATALOG]
        assert "1984" in titles
        assert "The Great Gatsby" in titles
        assert "Moby Dick" in titles

    def test_discount_codes_structure(self):
        """Test DISCOUNT_CODES has correct structure."""
        assert isinstance(DISCOUNT_CODES, dict)
        for code, info in DISCOUNT_CODES.items():
            assert "discount_percent" in info
            assert "description" in info
            assert isinstance(info["discount_percent"], int)

    def test_discount_codes_contains_expected_codes(self):
        """Test DISCOUNT_CODES contains expected codes."""
        assert "SAVE10" in DISCOUNT_CODES
        assert "WELCOME20" in DISCOUNT_CODES
        assert "STUDENT15" in DISCOUNT_CODES

    def test_demo_user_configuration(self):
        """Test DEMO_USER has correct structure."""
        assert isinstance(DEMO_USER, dict)
        assert "email" in DEMO_USER
        assert "password" in DEMO_USER
        assert "name" in DEMO_USER
        assert "address" in DEMO_USER
        assert DEMO_USER["email"] == "demo@bookstore.com"

