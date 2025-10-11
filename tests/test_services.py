"""Comprehensive test suite for services.py module.

This module contains 33 test cases covering:
- BookService (8 tests)
- CartService (8 tests)
- UserService (8 tests)
- OrderService (6 tests)
- PaymentService (6 tests)
- EmailService (5 tests)
"""

import pytest
from unittest.mock import patch, MagicMock
from models_refactored import Book, Cart, CartItem, User, Order
from services import (
    BookService,
    CartService,
    UserService,
    OrderService,
    PaymentService,
    EmailService,
    ServiceResult,
)


# ============================================================================
# BookService Tests (8 tests)
# ============================================================================


class TestBookService:
    """Test suite for BookService class."""

    def test_get_all_books_returns_list(self):
        """Test that get_all_books returns a list of books."""
        books = BookService.get_all_books()
        assert isinstance(books, list)
        assert len(books) > 0

    def test_get_all_books_caching(self):
        """Test that books are cached after first call."""
        books1 = BookService.get_all_books()
        books2 = BookService.get_all_books()
        assert books1 is books2  # Same object reference

    def test_get_all_books_returns_book_objects(self):
        """Test that all returned items are Book objects."""
        books = BookService.get_all_books()
        assert all(isinstance(book, Book) for book in books)

    def test_get_book_by_title_found(self):
        """Test finding a book by title."""
        book = BookService.get_book_by_title("1984")
        assert book is not None
        assert book.title == "1984"

    def test_get_book_by_title_not_found(self):
        """Test searching for non-existent book."""
        book = BookService.get_book_by_title("Nonexistent Book")
        assert book is None

    def test_search_books_by_title(self):
        """Test searching books by title."""
        results = BookService.search_books("1984")
        assert len(results) > 0
        assert any("1984" in book.title for book in results)

    def test_search_books_by_author(self):
        """Test searching books by author."""
        results = BookService.search_books("Orwell")
        assert len(results) > 0
        assert any("Orwell" in book.author for book in results)

    def test_search_books_case_insensitive(self):
        """Test that search is case-insensitive."""
        results1 = BookService.search_books("gatsby")
        results2 = BookService.search_books("GATSBY")
        assert len(results1) == len(results2)


# ============================================================================
# CartService Tests (8 tests)
# ============================================================================


class TestCartService:
    """Test suite for CartService class."""

    @pytest.fixture
    def empty_cart(self):
        """Fixture providing an empty cart."""
        return Cart()

    def test_add_to_cart_success(self, empty_cart):
        """Test successfully adding a book to cart."""
        result = CartService.add_to_cart(empty_cart, "1984", 2)
        assert result.success is True
        assert "Added 2" in result.message
        assert empty_cart.get_total_items() == 2

    def test_add_to_cart_book_not_found(self, empty_cart):
        """Test adding non-existent book to cart."""
        result = CartService.add_to_cart(empty_cart, "Nonexistent Book", 1)
        assert result.success is False
        assert result.error_code == "BOOK_NOT_FOUND"

    def test_add_to_cart_invalid_quantity(self, empty_cart):
        """Test adding book with invalid quantity."""
        result = CartService.add_to_cart(empty_cart, "1984", -1)
        assert result.success is False
        assert result.error_code == "INVALID_QUANTITY"

    def test_update_cart_item_success(self, empty_cart):
        """Test successfully updating cart item quantity."""
        CartService.add_to_cart(empty_cart, "1984", 1)
        result = CartService.update_cart_item(empty_cart, "1984", 5)
        assert result.success is True
        assert "Updated" in result.message

    def test_update_cart_item_to_zero(self, empty_cart):
        """Test updating cart item quantity to zero removes it."""
        CartService.add_to_cart(empty_cart, "1984", 1)
        result = CartService.update_cart_item(empty_cart, "1984", 0)
        assert result.success is True
        assert "Removed" in result.message
        assert empty_cart.is_empty() is True

    def test_remove_from_cart_success(self, empty_cart):
        """Test successfully removing item from cart."""
        CartService.add_to_cart(empty_cart, "1984", 1)
        result = CartService.remove_from_cart(empty_cart, "1984")
        assert result.success is True
        assert empty_cart.is_empty() is True

    def test_clear_cart_success(self, empty_cart):
        """Test successfully clearing cart."""
        CartService.add_to_cart(empty_cart, "1984", 1)
        result = CartService.clear_cart(empty_cart)
        assert result.success is True
        assert empty_cart.is_empty() is True

    def test_cart_service_result_data(self, empty_cart):
        """Test that service result includes data."""
        result = CartService.add_to_cart(empty_cart, "1984", 2)
        assert result.data is not None
        assert "book" in result.data
        assert "quantity" in result.data


# ============================================================================
# UserService Tests (8 tests)
# ============================================================================


class TestUserService:
    """Test suite for UserService class."""

    def test_register_user_success(self):
        """Test successful user registration."""
        with patch("app_refactored.app") as mock_app:
            mock_app.users = {}
            result = UserService.register_user(
                "test@example.com", "password123", "Test User", "123 Test St"
            )
            assert result.success is True
            assert result.data["email"] == "test@example.com"

    def test_register_user_invalid_email(self):
        """Test registration with invalid email."""
        with patch("app_refactored.app") as mock_app:
            mock_app.users = {}
            result = UserService.register_user("invalid-email", "password123", "Test")
            assert result.success is False
            assert result.error_code == "INVALID_EMAIL"

    def test_register_user_missing_fields(self):
        """Test registration with missing required fields."""
        with patch("app_refactored.app") as mock_app:
            mock_app.users = {}
            result = UserService.register_user("test@example.com", "", "")
            assert result.success is False
            assert result.error_code == "MISSING_FIELDS"

    def test_register_user_duplicate_email(self):
        """Test registration with existing email."""
        with patch("app_refactored.app") as mock_app:
            mock_app.users = {}
            UserService.register_user("test@example.com", "password123", "Test User")
            result = UserService.register_user(
                "test@example.com", "password456", "Another User"
            )
            assert result.success is False
            assert result.error_code == "EMAIL_EXISTS"

    def test_authenticate_user_success(self):
        """Test successful user authentication."""
        with patch("app_refactored.app") as mock_app:
            mock_app.users = {}
            UserService.register_user("test@example.com", "password123", "Test User")
            result = UserService.authenticate_user("test@example.com", "password123")
            assert result.success is True

    def test_authenticate_user_invalid_credentials(self):
        """Test authentication with invalid credentials."""
        with patch("app_refactored.app") as mock_app:
            mock_app.users = {}
            UserService.register_user("test@example.com", "password123", "Test User")
            result = UserService.authenticate_user("test@example.com", "wrongpassword")
            assert result.success is False
            assert result.error_code == "INVALID_CREDENTIALS"

    def test_authenticate_user_nonexistent(self):
        """Test authentication with nonexistent user."""
        with patch("app_refactored.app") as mock_app:
            mock_app.users = {}
            result = UserService.authenticate_user(
                "nonexistent@example.com", "password123"
            )
            assert result.success is False

    def test_register_user_email_normalization(self):
        """Test that registration normalizes email."""
        with patch("app_refactored.app") as mock_app:
            mock_app.users = {}
            result = UserService.register_user(
                "TEST@EXAMPLE.COM", "password123", "Test User"
            )
            assert result.success is True
            assert result.data["email"] == "test@example.com"


# ============================================================================
# OrderService Tests (6 tests)
# ============================================================================


class TestOrderService:
    """Test suite for OrderService class."""

    def test_calculate_discount_valid_code(self):
        """Test discount calculation with valid code."""
        total, discount, message = OrderService.calculate_discount(100.0, "SAVE10")
        assert total == 90.0
        assert discount == 10.0
        assert "applied" in message

    def test_calculate_discount_invalid_code(self):
        """Test discount calculation with invalid code."""
        total, discount, message = OrderService.calculate_discount(100.0, "INVALID")
        assert total == 100.0
        assert discount == 0.0
        assert "Invalid" in message

    def test_calculate_discount_empty_code(self):
        """Test discount calculation with empty code."""
        total, discount, message = OrderService.calculate_discount(100.0, "")
        assert total == 100.0
        assert discount == 0.0
        assert message == ""

    def test_create_order_success(self):
        """Test successful order creation."""
        with patch("app_refactored.app") as mock_app:
            mock_app.orders = {}
            mock_app.users = {}
            book = Book(title="Test Book", price=10.0)
            items = [CartItem(book, 1)]
            result = OrderService.create_order(
                "test@example.com",
                items,
                {"name": "Test", "address": "123 Test St"},
                {"method": "credit_card"},
                10.0,
            )
            assert result.success is True
            assert "order_id" in result.data

    def test_get_order_by_id_found(self):
        """Test getting order by ID when it exists."""
        with patch("app_refactored.app") as mock_app:
            book = Book(title="Test", price=10.0)
            order = Order(
                order_id="TEST123",
                user_email="test@example.com",
                items=[CartItem(book, 1)],
                shipping_info={},
                payment_info={},
                total_amount=10.0,
            )
            mock_app.orders = {"TEST123": order}
            result = OrderService.get_order_by_id("TEST123")
            assert result is not None
            assert result.order_id == "TEST123"

    def test_get_order_by_id_not_found(self):
        """Test getting order by ID when it doesn't exist."""
        with patch("app_refactored.app") as mock_app:
            mock_app.orders = {}
            result = OrderService.get_order_by_id("NONEXISTENT")
            assert result is None


# ============================================================================
# PaymentService Tests (6 tests)
# ============================================================================


class TestPaymentService:
    """Test suite for PaymentService class."""

    def test_validate_payment_info_credit_card_valid(self):
        """Test validating valid credit card payment info."""
        payment_info = {
            "payment_method": "credit_card",
            "card_number": "4532123456789012",
            "expiry_date": "12/25",
            "cvv": "123",
        }
        result = PaymentService.validate_payment_info(payment_info)
        assert result.success is True

    def test_validate_payment_info_credit_card_missing_fields(self):
        """Test validating credit card with missing fields."""
        payment_info = {
            "payment_method": "credit_card",
            "card_number": "",
            "expiry_date": "",
            "cvv": "",
        }
        result = PaymentService.validate_payment_info(payment_info)
        assert result.success is False
        assert result.error_code == "MISSING_CARD_DETAILS"

    def test_validate_payment_info_credit_card_invalid_format(self):
        """Test validating credit card with invalid format."""
        payment_info = {
            "payment_method": "credit_card",
            "card_number": "123",
            "expiry_date": "12/25",
            "cvv": "123",
        }
        result = PaymentService.validate_payment_info(payment_info)
        assert result.success is False
        assert result.error_code == "INVALID_CARD_FORMAT"

    def test_validate_payment_info_paypal_valid(self):
        """Test validating valid PayPal payment info."""
        payment_info = {
            "payment_method": "paypal",
            "paypal_email": "user@example.com",
        }
        result = PaymentService.validate_payment_info(payment_info)
        assert result.success is True

    def test_validate_payment_info_paypal_invalid_email(self):
        """Test validating PayPal with invalid email."""
        payment_info = {"payment_method": "paypal", "paypal_email": "invalid-email"}
        result = PaymentService.validate_payment_info(payment_info)
        assert result.success is False
        assert result.error_code == "INVALID_PAYPAL_EMAIL"

    def test_validate_payment_info_invalid_method(self):
        """Test validating with invalid payment method."""
        payment_info = {"payment_method": "invalid_method"}
        result = PaymentService.validate_payment_info(payment_info)
        assert result.success is False
        assert result.error_code == "INVALID_PAYMENT_METHOD"


# ============================================================================
# EmailService Tests (5 tests)
# ============================================================================


class TestEmailServiceService:
    """Test suite for EmailService in services.py."""

    @pytest.fixture
    def sample_order(self):
        """Fixture providing a sample order."""
        book = Book(title="Test Book", price=10.00)
        return Order(
            order_id="TEST123",
            user_email="user@example.com",
            items=[CartItem(book, 1)],
            shipping_info={"name": "John Doe", "address": "123 Test St"},
            payment_info={},
            total_amount=10.0,
        )

    def test_send_order_confirmation_success(self, sample_order, capsys):
        """Test successful email sending."""
        result = EmailService.send_order_confirmation("user@example.com", sample_order)
        assert result.success is True
        captured = capsys.readouterr()
        assert "EMAIL CONFIRMATION SENT" in captured.out

    def test_send_order_confirmation_invalid_email(self, sample_order):
        """Test email sending with invalid email."""
        result = EmailService.send_order_confirmation("invalid-email", sample_order)
        assert result.success is False
        assert result.error_code == "INVALID_EMAIL"

    def test_send_order_confirmation_includes_order_details(
        self, sample_order, capsys
    ):
        """Test that email includes order details."""
        EmailService.send_order_confirmation("user@example.com", sample_order)
        captured = capsys.readouterr()
        assert "TEST123" in captured.out
        assert "Test Book" in captured.out

    def test_send_order_confirmation_service_result(self, sample_order):
        """Test that email service returns ServiceResult."""
        result = EmailService.send_order_confirmation("user@example.com", sample_order)
        assert isinstance(result, ServiceResult)

    def test_send_order_confirmation_includes_shipping(self, sample_order, capsys):
        """Test that email includes shipping information."""
        EmailService.send_order_confirmation("user@example.com", sample_order)
        captured = capsys.readouterr()
        assert "John Doe" in captured.out


# ============================================================================
# ServiceResult Tests (2 tests)
# ============================================================================


class TestServiceResult:
    """Test suite for ServiceResult class."""

    def test_service_result_creation(self):
        """Test creating a ServiceResult."""
        result = ServiceResult(
            success=True, message="Success", data={"key": "value"}, error_code=None
        )
        assert result.success is True
        assert result.message == "Success"
        assert result.data == {"key": "value"}

    def test_service_result_default_values(self):
        """Test ServiceResult default values."""
        result = ServiceResult(success=False, message="Failed")
        assert result.data is None
        assert result.error_code is None

