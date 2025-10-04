"""Configuration management for the Online Bookstore application."""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class DatabaseConfig:
    """Database configuration settings."""

    url: str = "sqlite:///bookstore.db"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10


@dataclass
class SecurityConfig:
    """Security-related configuration."""

    secret_key: str = "change-me-in-production"
    password_min_length: int = 8
    session_timeout: int = 3600  # 1 hour
    bcrypt_rounds: int = 10  # Reduced for better performance while maintaining security


@dataclass
class PaymentConfig:
    """Payment gateway configuration."""

    test_mode: bool = True
    success_rate: float = 0.95
    processing_delay: float = 0.1  # seconds


@dataclass
class EmailConfig:
    """Email service configuration."""

    enabled: bool = True
    smtp_server: str = "localhost"
    smtp_port: int = 587
    use_tls: bool = True
    from_email: str = "noreply@bookstore.com"


@dataclass
class AppConfig:
    """Main application configuration."""

    debug: bool = True
    host: str = "127.0.0.1"
    port: int = 5000
    database: DatabaseConfig = None
    security: SecurityConfig = None
    payment: PaymentConfig = None
    email: EmailConfig = None

    def __post_init__(self):
        if self.database is None:
            self.database = DatabaseConfig()
        if self.security is None:
            self.security = SecurityConfig()
        if self.payment is None:
            self.payment = PaymentConfig()
        if self.email is None:
            self.email = EmailConfig()


class ConfigManager:
    """Manages application configuration with environment variable support."""

    @staticmethod
    def load_config() -> AppConfig:
        """Load configuration from environment variables and defaults."""
        return AppConfig(
            debug=os.getenv("FLASK_DEBUG", "True").lower() == "true",
            host=os.getenv("FLASK_HOST", "127.0.0.1"),
            port=int(os.getenv("FLASK_PORT", "5000")),
            database=DatabaseConfig(
                url=os.getenv("DATABASE_URL", "sqlite:///bookstore.db"),
                echo=os.getenv("DATABASE_ECHO", "False").lower() == "true",
                pool_size=int(os.getenv("DATABASE_POOL_SIZE", "5")),
                max_overflow=int(os.getenv("DATABASE_MAX_OVERFLOW", "10")),
            ),
            security=SecurityConfig(
                secret_key=os.getenv("SECRET_KEY", "change-me-in-production"),
                password_min_length=int(os.getenv("PASSWORD_MIN_LENGTH", "8")),
                session_timeout=int(os.getenv("SESSION_TIMEOUT", "3600")),
                bcrypt_rounds=int(os.getenv("BCRYPT_ROUNDS", "12")),
            ),
            payment=PaymentConfig(
                test_mode=os.getenv("PAYMENT_TEST_MODE", "True").lower() == "true",
                success_rate=float(os.getenv("PAYMENT_SUCCESS_RATE", "0.95")),
                processing_delay=float(os.getenv("PAYMENT_PROCESSING_DELAY", "0.1")),
            ),
            email=EmailConfig(
                enabled=os.getenv("EMAIL_ENABLED", "True").lower() == "true",
                smtp_server=os.getenv("SMTP_SERVER", "localhost"),
                smtp_port=int(os.getenv("SMTP_PORT", "587")),
                use_tls=os.getenv("SMTP_USE_TLS", "True").lower() == "true",
                from_email=os.getenv("FROM_EMAIL", "noreply@bookstore.com"),
            ),
        )


# Default book catalog configuration
BOOK_CATALOG = [
    {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "category": "Fiction",
        "price": 10.99,
        "image_url": "/images/books/the_great_gatsby.jpg",
        "description": "A classic American novel about the Jazz Age.",
    },
    {
        "title": "1984",
        "author": "George Orwell",
        "category": "Dystopia",
        "price": 8.99,
        "image_url": "/images/books/1984.jpg",
        "description": "A dystopian social science fiction novel.",
    },
    {
        "title": "I Ching",
        "author": "King Wen of Zhou",
        "category": "Traditional",
        "price": 18.99,
        "image_url": "/images/books/I-Ching.jpg",
        "description": "An ancient Chinese divination text.",
    },
    {
        "title": "Moby Dick",
        "author": "Herman Melville",
        "category": "Adventure",
        "price": 12.49,
        "image_url": "/images/books/moby_dick.jpg",
        "description": "An epic tale of Captain Ahab's quest for revenge.",
    },
]

# Discount codes configuration
DISCOUNT_CODES = {
    "SAVE10": {"discount_percent": 10, "description": "10% off your order"},
    "WELCOME20": {"discount_percent": 20, "description": "20% welcome discount"},
    "STUDENT15": {"discount_percent": 15, "description": "15% student discount"},
}

# Demo user configuration
DEMO_USER = {
    "email": "demo@bookstore.com",
    "password": "demo1234",
    "name": "Demo User",
    "address": "123 Demo Street, Demo City, DC 12345",
}
