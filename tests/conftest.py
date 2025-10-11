"""Pytest configuration and shared fixtures for test suite."""

import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(autouse=True)
def reset_app_state():
    """Reset application state before each test."""
    # This fixture runs before each test to ensure clean state
    yield
    # Cleanup after test if needed


@pytest.fixture
def sample_book_data():
    """Fixture providing sample book data for tests."""
    return {
        "title": "Test Book",
        "author": "Test Author",
        "category": "Test Category",
        "price": 19.99,
        "image_url": "/images/test.jpg",
        "description": "A test book description",
    }


@pytest.fixture
def sample_user_data():
    """Fixture providing sample user data for tests."""
    return {
        "email": "testuser@example.com",
        "password": "testpass123",
        "name": "Test User",
        "address": "123 Test Street, Test City, TC 12345",
    }


@pytest.fixture
def sample_payment_info():
    """Fixture providing sample payment information."""
    return {
        "payment_method": "credit_card",
        "card_number": "4532123456789012",
        "expiry_date": "12/25",
        "cvv": "123",
    }


@pytest.fixture
def sample_shipping_info():
    """Fixture providing sample shipping information."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "address": "123 Test Street",
        "city": "Test City",
        "zip_code": "12345",
    }

