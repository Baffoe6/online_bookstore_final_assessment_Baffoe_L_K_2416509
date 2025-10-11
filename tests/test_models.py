"""Comprehensive test suite for models_refactored.py module.

This module contains 53 test cases covering:
- ValidationUtils (15 tests)
- Book (10 tests)
- CartItem (8 tests)
- Cart (12 tests)
- User (10 tests)
- Order (8 tests)
- PaymentGateway (8 tests)
- EmailService (5 tests)
"""

import pytest
from datetime import datetime
from models_refactored import (
    ValidationUtils,
    Book,
    CartItem,
    Cart,
    User,
    Order,
    PaymentGateway,
    EmailService,
)


# ============================================================================
# ValidationUtils Tests (15 tests)
# ============================================================================


class TestValidationUtils:
    """Test suite for ValidationUtils class."""

    def test_normalize_email_valid(self):
        """Test email normalization with valid email."""
        assert ValidationUtils.normalize_email("Test@Example.COM") == "test@example.com"

    def test_normalize_email_with_spaces(self):
        """Test email normalization with leading/trailing spaces."""
        assert ValidationUtils.normalize_email("  user@domain.com  ") == "user@domain.com"

    def test_normalize_email_empty_raises_error(self):
        """Test that empty email raises ValueError."""
        with pytest.raises(ValueError, match="Email address is required"):
            ValidationUtils.normalize_email("")

    def test_normalize_email_none_raises_error(self):
        """Test that None email raises ValueError."""
        with pytest.raises(ValueError, match="Email address is required"):
            ValidationUtils.normalize_email(None)

    def test_validate_email_valid(self):
        """Test email validation with valid email."""
        assert ValidationUtils.validate_email("user@example.com") is True

    def test_validate_email_invalid(self):
        """Test email validation with invalid email."""
        assert ValidationUtils.validate_email("invalid-email") is False
        assert ValidationUtils.validate_email("@example.com") is False
        assert ValidationUtils.validate_email("user@") is False

    def test_validate_quantity_string_to_int(self):
        """Test quantity validation converts string to int."""
        assert ValidationUtils.validate_quantity("5") == 5

    def test_validate_quantity_negative_raises_error(self):
        """Test that negative quantity raises ValueError."""
        with pytest.raises(ValueError, match="Quantity must be positive"):
            ValidationUtils.validate_quantity(-1)

    def test_validate_quantity_zero_with_allow_zero(self):
        """Test that zero quantity is allowed when allow_zero=True."""
        assert ValidationUtils.validate_quantity(0, allow_zero=True) == 0

    def test_validate_quantity_zero_without_allow_zero(self):
        """Test that zero quantity raises error when allow_zero=False."""
        with pytest.raises(ValueError, match="Quantity must be positive"):
            ValidationUtils.validate_quantity(0, allow_zero=False)

    def test_validate_quantity_float_raises_error(self):
        """Test that non-integer float raises ValueError."""
        with pytest.raises(ValueError, match="Quantity must be an integer"):
            ValidationUtils.validate_quantity(5.5)

    def test_normalize_discount_code_uppercase(self):
        """Test discount code normalization to uppercase."""
        assert ValidationUtils.normalize_discount_code("save10") == "SAVE10"

    def test_normalize_discount_code_with_spaces(self):
        """Test discount code normalization removes spaces."""
        assert ValidationUtils.normalize_discount_code("  WELCOME20  ") == "WELCOME20"

    def test_validate_card_number_valid(self):
        """Test card number validation with valid number."""
        assert ValidationUtils.validate_card_number("1234567890123456") is True

    def test_validate_card_number_with_spaces(self):
        """Test card number validation handles spaces."""
        assert ValidationUtils.validate_card_number("1234 5678 9012 3456") is True


# ============================================================================
# Book Tests (10 tests)
# ============================================================================


class TestBook:
    """Test suite for Book class."""

    def test_book_creation_valid(self):
        """Test creating a book with valid data."""
        book = Book(title="Test Book", author="Test Author", price=10.99)
        assert book.title == "Test Book"
        assert book.author == "Test Author"
        assert book.price == 10.99

    def test_book_empty_title_raises_error(self):
        """Test that empty title raises ValueError."""
        with pytest.raises(ValueError, match="Book title is required"):
            Book(title="")

    def test_book_negative_price_raises_error(self):
        """Test that negative price raises ValueError."""
        with pytest.raises(ValueError, match="Book price cannot be negative"):
            Book(title="Test Book", price=-5.0)

    def test_book_formatted_price(self):
        """Test formatted price property."""
        book = Book(title="Test Book", price=10.99)
        assert book.formatted_price == "$10.99"

    def test_book_to_dict(self):
        """Test book serialization to dictionary."""
        book = Book(title="Test", author="Author", category="Fiction", price=9.99)
        book_dict = book.to_dict()
        assert book_dict["title"] == "Test"
        assert book_dict["author"] == "Author"
        assert book_dict["price"] == 9.99

    def test_book_immutability(self):
        """Test that book is immutable (frozen dataclass)."""
        book = Book(title="Test Book", price=10.99)
        with pytest.raises(AttributeError):
            book.price = 15.99

    def test_book_strips_whitespace(self):
        """Test that book strips whitespace from strings."""
        book = Book(title="  Test Book  ", author="  Author  ")
        assert book.title == "Test Book"
        assert book.author == "Author"

    def test_book_backwards_compatibility_image(self):
        """Test backwards compatibility for image attribute."""
        book = Book(title="Test", image_url="/test.jpg")
        assert book.image == book.image_url

    def test_book_default_values(self):
        """Test book default values."""
        book = Book(title="Test Book")
        assert book.author == ""
        assert book.category == ""
        assert book.price == 0.0

    def test_book_description_field(self):
        """Test book description field."""
        book = Book(title="Test", description="A great book")
        assert book.description == "A great book"


# ============================================================================
# CartItem Tests (8 tests)
# ============================================================================


class TestCartItem:
    """Test suite for CartItem class."""

    @pytest.fixture
    def sample_book(self):
        """Fixture providing a sample book."""
        return Book(title="Test Book", price=10.00)

    def test_cart_item_creation(self, sample_book):
        """Test creating a cart item."""
        item = CartItem(sample_book, 2)
        assert item.book == sample_book
        assert item.quantity == 2

    def test_cart_item_get_total_price(self, sample_book):
        """Test cart item total price calculation."""
        item = CartItem(sample_book, 3)
        assert item.get_total_price() == 30.00

    def test_cart_item_get_formatted_total(self, sample_book):
        """Test cart item formatted total."""
        item = CartItem(sample_book, 2)
        assert item.get_formatted_total() == "$20.00"

    def test_cart_item_update_quantity(self, sample_book):
        """Test updating cart item quantity."""
        item = CartItem(sample_book, 1)
        item.update_quantity(5)
        assert item.quantity == 5

    def test_cart_item_invalid_quantity_raises_error(self, sample_book):
        """Test that invalid quantity raises ValueError."""
        with pytest.raises(ValueError):
            CartItem(sample_book, -1)

    def test_cart_item_to_dict(self, sample_book):
        """Test cart item serialization to dictionary."""
        item = CartItem(sample_book, 2)
        item_dict = item.to_dict()
        assert item_dict["quantity"] == 2
        assert item_dict["total_price"] == 20.00

    def test_cart_item_default_quantity(self, sample_book):
        """Test cart item default quantity is 1."""
        item = CartItem(sample_book)
        assert item.quantity == 1

    def test_cart_item_zero_quantity_raises_error(self, sample_book):
        """Test that zero quantity raises ValueError."""
        with pytest.raises(ValueError):
            CartItem(sample_book, 0)


# ============================================================================
# Cart Tests (12 tests)
# ============================================================================


class TestCart:
    """Test suite for Cart class."""

    @pytest.fixture
    def sample_book(self):
        """Fixture providing a sample book."""
        return Book(title="Test Book", price=15.00)

    @pytest.fixture
    def empty_cart(self):
        """Fixture providing an empty cart."""
        return Cart()

    def test_cart_initialization(self, empty_cart):
        """Test cart initialization."""
        assert empty_cart.is_empty() is True
        assert empty_cart.get_total_items() == 0

    def test_cart_add_book(self, empty_cart, sample_book):
        """Test adding a book to cart."""
        empty_cart.add_book(sample_book, 2)
        assert empty_cart.get_total_items() == 2
        assert empty_cart.is_empty() is False

    def test_cart_add_existing_book(self, empty_cart, sample_book):
        """Test adding existing book increases quantity."""
        empty_cart.add_book(sample_book, 1)
        empty_cart.add_book(sample_book, 2)
        assert empty_cart.get_total_items() == 3

    def test_cart_remove_book(self, empty_cart, sample_book):
        """Test removing a book from cart."""
        empty_cart.add_book(sample_book, 2)
        empty_cart.remove_book(sample_book.title)
        assert empty_cart.is_empty() is True

    def test_cart_update_quantity(self, empty_cart, sample_book):
        """Test updating cart item quantity."""
        empty_cart.add_book(sample_book, 2)
        empty_cart.update_quantity(sample_book.title, 5)
        assert empty_cart.get_total_items() == 5

    def test_cart_update_quantity_to_zero_removes_item(self, empty_cart, sample_book):
        """Test updating quantity to zero removes item."""
        empty_cart.add_book(sample_book, 2)
        empty_cart.update_quantity(sample_book.title, 0)
        assert empty_cart.is_empty() is True

    def test_cart_get_total_price(self, empty_cart, sample_book):
        """Test cart total price calculation."""
        empty_cart.add_book(sample_book, 3)
        assert empty_cart.get_total_price() == 45.00

    def test_cart_clear(self, empty_cart, sample_book):
        """Test clearing cart."""
        empty_cart.add_book(sample_book, 2)
        empty_cart.clear()
        assert empty_cart.is_empty() is True

    def test_cart_get_items(self, empty_cart, sample_book):
        """Test getting cart items list."""
        empty_cart.add_book(sample_book, 1)
        items = empty_cart.get_items()
        assert len(items) == 1
        assert items[0].book == sample_book

    def test_cart_get_formatted_total(self, empty_cart, sample_book):
        """Test cart formatted total."""
        empty_cart.add_book(sample_book, 2)
        assert empty_cart.get_formatted_total() == "$30.00"

    def test_cart_to_dict(self, empty_cart, sample_book):
        """Test cart serialization to dictionary."""
        empty_cart.add_book(sample_book, 2)
        cart_dict = empty_cart.to_dict()
        assert cart_dict["total_items"] == 2
        assert cart_dict["is_empty"] is False

    def test_cart_backwards_compatibility_clear_cart(self, empty_cart, sample_book):
        """Test backwards compatibility clear_cart method."""
        empty_cart.add_book(sample_book, 2)
        empty_cart.clear_cart()
        assert empty_cart.is_empty() is True


# ============================================================================
# User Tests (10 tests)
# ============================================================================


class TestUser:
    """Test suite for User class."""

    def test_user_creation_valid(self):
        """Test creating a user with valid data."""
        user = User("user@example.com", "password123", "John Doe")
        assert user.email == "user@example.com"
        assert user.name == "John Doe"

    def test_user_email_normalization(self):
        """Test user email is normalized."""
        user = User("USER@EXAMPLE.COM", "password123")
        assert user.email == "user@example.com"

    def test_user_password_too_short_raises_error(self):
        """Test that password shorter than 8 characters raises error."""
        with pytest.raises(ValueError, match="at least 8 characters"):
            User("user@example.com", "short")

    def test_user_empty_password_raises_error(self):
        """Test that empty password raises error."""
        with pytest.raises(ValueError, match="Password is required"):
            User("user@example.com", "")

    def test_user_verify_password_correct(self):
        """Test password verification with correct password."""
        user = User("user@example.com", "password123")
        assert user.verify_password("password123") is True

    def test_user_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        user = User("user@example.com", "password123")
        assert user.verify_password("wrongpassword") is False

    def test_user_change_password(self):
        """Test changing user password."""
        user = User("user@example.com", "oldpassword123")
        user.change_password("newpassword123")
        assert user.verify_password("newpassword123") is True

    def test_user_change_password_too_short_raises_error(self):
        """Test that changing to short password raises error."""
        user = User("user@example.com", "password123")
        with pytest.raises(ValueError, match="at least 8 characters"):
            user.change_password("short")

    def test_user_add_order(self):
        """Test adding order to user."""
        user = User("user@example.com", "password123")
        book = Book(title="Test", price=10.0)
        order = Order(
            order_id="TEST123",
            user_email=user.email,
            items=[CartItem(book, 1)],
            shipping_info={},
            payment_info={},
            total_amount=10.0,
        )
        user.add_order(order)
        assert len(user.orders) == 1

    def test_user_to_dict(self):
        """Test user serialization to dictionary."""
        user = User("user@example.com", "password123", "John Doe")
        user_dict = user.to_dict()
        assert user_dict["email"] == "user@example.com"
        assert user_dict["name"] == "John Doe"


# ============================================================================
# Order Tests (8 tests)
# ============================================================================


class TestOrder:
    """Test suite for Order class."""

    @pytest.fixture
    def sample_cart_items(self):
        """Fixture providing sample cart items."""
        book = Book(title="Test Book", price=20.00)
        return [CartItem(book, 2)]

    def test_order_creation_valid(self, sample_cart_items):
        """Test creating an order with valid data."""
        order = Order(
            order_id="TEST123",
            user_email="user@example.com",
            items=sample_cart_items,
            shipping_info={"address": "123 Test St"},
            payment_info={"method": "credit_card"},
            total_amount=40.0,
        )
        assert order.order_id == "TEST123"
        assert order.total_amount == 40.0

    def test_order_negative_total_raises_error(self, sample_cart_items):
        """Test that negative total raises ValueError."""
        with pytest.raises(ValueError, match="Order total cannot be negative"):
            Order(
                order_id="TEST123",
                user_email="user@example.com",
                items=sample_cart_items,
                shipping_info={},
                payment_info={},
                total_amount=-10.0,
            )

    def test_order_empty_items_raises_error(self):
        """Test that empty items list raises ValueError."""
        with pytest.raises(ValueError, match="Order must contain at least one item"):
            Order(
                order_id="TEST123",
                user_email="user@example.com",
                items=[],
                shipping_info={},
                payment_info={},
                total_amount=0.0,
            )

    def test_order_get_formatted_total(self, sample_cart_items):
        """Test order formatted total."""
        order = Order(
            order_id="TEST123",
            user_email="user@example.com",
            items=sample_cart_items,
            shipping_info={},
            payment_info={},
            total_amount=40.0,
        )
        assert order.get_formatted_total() == "$40.00"

    def test_order_get_item_count(self, sample_cart_items):
        """Test order item count."""
        order = Order(
            order_id="TEST123",
            user_email="user@example.com",
            items=sample_cart_items,
            shipping_info={},
            payment_info={},
            total_amount=40.0,
        )
        assert order.get_item_count() == 2

    def test_order_update_status(self, sample_cart_items):
        """Test updating order status."""
        order = Order(
            order_id="TEST123",
            user_email="user@example.com",
            items=sample_cart_items,
            shipping_info={},
            payment_info={},
            total_amount=40.0,
        )
        order.update_status("Shipped")
        assert order.status == "Shipped"

    def test_order_invalid_status_raises_error(self, sample_cart_items):
        """Test that invalid status raises ValueError."""
        order = Order(
            order_id="TEST123",
            user_email="user@example.com",
            items=sample_cart_items,
            shipping_info={},
            payment_info={},
            total_amount=40.0,
        )
        with pytest.raises(ValueError, match="Invalid status"):
            order.update_status("InvalidStatus")

    def test_order_to_dict(self, sample_cart_items):
        """Test order serialization to dictionary."""
        order = Order(
            order_id="TEST123",
            user_email="user@example.com",
            items=sample_cart_items,
            shipping_info={"address": "123 Test St"},
            payment_info={},
            total_amount=40.0,
        )
        order_dict = order.to_dict()
        assert order_dict["order_id"] == "TEST123"
        assert order_dict["total_amount"] == 40.0


# ============================================================================
# PaymentGateway Tests (8 tests)
# ============================================================================


class TestPaymentGateway:
    """Test suite for PaymentGateway class."""

    def test_process_payment_credit_card_success(self):
        """Test successful credit card payment processing."""
        payment_info = {
            "payment_method": "credit_card",
            "card_number": "4532123456789012",
            "expiry_date": "12/25",
            "cvv": "123",
        }
        result = PaymentGateway.process_payment(payment_info)
        assert result["success"] is True
        assert result["transaction_id"] is not None

    def test_process_payment_credit_card_invalid_card(self):
        """Test credit card payment with invalid card."""
        payment_info = {
            "payment_method": "credit_card",
            "card_number": "4532123456781111",
            "expiry_date": "12/25",
            "cvv": "123",
        }
        result = PaymentGateway.process_payment(payment_info)
        assert result["success"] is False

    def test_process_payment_credit_card_missing_info(self):
        """Test credit card payment with missing information."""
        payment_info = {
            "payment_method": "credit_card",
            "card_number": "",
            "expiry_date": "",
            "cvv": "",
        }
        result = PaymentGateway.process_payment(payment_info)
        assert result["success"] is False
        assert "Missing required" in result["message"]

    def test_process_payment_paypal_success(self):
        """Test successful PayPal payment processing."""
        payment_info = {
            "payment_method": "paypal",
            "paypal_email": "user@example.com",
        }
        result = PaymentGateway.process_payment(payment_info)
        assert result["success"] is True
        assert result["transaction_id"] is not None

    def test_process_payment_paypal_invalid_email(self):
        """Test PayPal payment with invalid email."""
        payment_info = {
            "payment_method": "paypal",
            "paypal_email": "invalid-email",
        }
        result = PaymentGateway.process_payment(payment_info)
        assert result["success"] is False

    def test_process_payment_paypal_missing_email(self):
        """Test PayPal payment with missing email."""
        payment_info = {
            "payment_method": "paypal",
            "paypal_email": "",
        }
        result = PaymentGateway.process_payment(payment_info)
        assert result["success"] is False

    def test_process_payment_invalid_method(self):
        """Test payment with invalid payment method."""
        payment_info = {"payment_method": "invalid_method"}
        result = PaymentGateway.process_payment(payment_info)
        assert result["success"] is False
        assert "Invalid payment method" in result["message"]

    def test_process_payment_credit_card_invalid_format(self):
        """Test credit card payment with invalid card format."""
        payment_info = {
            "payment_method": "credit_card",
            "card_number": "123",
            "expiry_date": "12/25",
            "cvv": "123",
        }
        result = PaymentGateway.process_payment(payment_info)
        assert result["success"] is False


# ============================================================================
# EmailService Tests (5 tests)
# ============================================================================


class TestEmailService:
    """Test suite for EmailService class."""

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
        """Test successful order confirmation email."""
        result = EmailService.send_order_confirmation("user@example.com", sample_order)
        assert result is True
        captured = capsys.readouterr()
        assert "EMAIL CONFIRMATION SENT" in captured.out

    def test_send_order_confirmation_invalid_email(self, sample_order, capsys):
        """Test order confirmation with invalid email."""
        result = EmailService.send_order_confirmation("invalid-email", sample_order)
        assert result is False
        captured = capsys.readouterr()
        assert "ERROR" in captured.out

    def test_send_order_confirmation_includes_order_id(self, sample_order, capsys):
        """Test that confirmation email includes order ID."""
        EmailService.send_order_confirmation("user@example.com", sample_order)
        captured = capsys.readouterr()
        assert "TEST123" in captured.out

    def test_send_order_confirmation_includes_items(self, sample_order, capsys):
        """Test that confirmation email includes order items."""
        EmailService.send_order_confirmation("user@example.com", sample_order)
        captured = capsys.readouterr()
        assert "Test Book" in captured.out

    def test_send_order_confirmation_includes_shipping(self, sample_order, capsys):
        """Test that confirmation email includes shipping info."""
        EmailService.send_order_confirmation("user@example.com", sample_order)
        captured = capsys.readouterr()
        assert "John Doe" in captured.out
        assert "123 Test St" in captured.out

