"""Refactored domain models with enhanced type safety and validation.

This module provides improved versions of the original models with:
- Better type hints and validation
- Enhanced error handling
- Improved performance
- Security enhancements
- Comprehensive documentation
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Union
from decimal import Decimal

import bcrypt


__all__ = [
    "Book",
    "Cart",
    "CartItem", 
    "EmailService",
    "Order",
    "PaymentGateway",
    "User",
    "ValidationUtils",
]


class ValidationUtils:
    """Enhanced utility class for input validation and normalization."""

    _email_pattern = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    _card_number_pattern = re.compile(r"^\d{13,19}$")

    @staticmethod
    def normalize_email(email: str) -> str:
        """Normalize email addresses for case-insensitive comparisons.
        
        Args:
            email: Raw email input
            
        Returns:
            Normalized email address
            
        Raises:
            ValueError: If email is invalid or empty
        """
        if not email or not isinstance(email, str):
            raise ValueError("Email address is required")
        
        normalized = email.strip().lower()
        if not normalized:
            raise ValueError("Email address cannot be empty")
            
        return normalized

    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email format using pre-compiled regex.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if email format is valid, False otherwise
        """
        if not email or not isinstance(email, str):
            return False
        return cls._email_pattern.match(email.strip()) is not None

    @classmethod
    def validate_quantity(cls, quantity: Union[str, int, float], *, allow_zero: bool = False) -> int:
        """Validate and coerce quantity inputs with comprehensive error handling.
        
        Args:
            quantity: Input quantity (string, int, or float)
            allow_zero: Whether zero quantities are allowed
            
        Returns:
            Validated integer quantity
            
        Raises:
            ValueError: If quantity is invalid
        """
        if isinstance(quantity, str):
            stripped = quantity.strip()
            if not stripped:
                if allow_zero:
                    raise ValueError("Quantity cannot be empty")
                return 1
            try:
                quantity = int(stripped)
            except ValueError as exc:
                raise ValueError(f"Invalid quantity format: {quantity}") from exc
        elif isinstance(quantity, (int, float)):
            if isinstance(quantity, float):
                if not quantity.is_integer():
                    raise ValueError(f"Quantity must be an integer: {quantity}")
                quantity = int(quantity)
        else:
            raise ValueError(f"Unsupported quantity type: {type(quantity)!r}")

        if allow_zero and quantity == 0:
            return 0
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        return quantity

    @staticmethod
    def normalize_discount_code(code: Optional[str]) -> str:
        """Normalize discount codes for case-insensitive comparisons.
        
        Args:
            code: Raw discount code
            
        Returns:
            Normalized discount code (uppercase, trimmed)
        """
        return code.strip().upper() if code else ""

    @classmethod
    def validate_card_number(cls, card_number: str) -> bool:
        """Validate credit card number format.
        
        Args:
            card_number: Card number to validate
            
        Returns:
            True if card number format is valid
        """
        if not card_number:
            return False
        cleaned = card_number.replace(" ", "").replace("-", "")
        return cls._card_number_pattern.match(cleaned) is not None


@dataclass(frozen=True)
class Book:
    """Immutable book model with comprehensive validation."""

    title: str
    author: str = ""
    category: str = ""
    price: float = 0.0
    image_url: str = ""
    description: str = ""

    def __post_init__(self) -> None:
        """Validate and normalize book data after initialization."""
        # Validate required fields
        if not self.title or not self.title.strip():
            raise ValueError("Book title is required")
        
        # Normalize string fields
        object.__setattr__(self, 'title', self.title.strip())
        object.__setattr__(self, 'author', self.author.strip())
        object.__setattr__(self, 'category', self.category.strip())
        object.__setattr__(self, 'description', self.description.strip())
        
        # Validate price
        if self.price < 0:
            raise ValueError("Book price cannot be negative")
        object.__setattr__(self, 'price', float(self.price))
        
        # Backwards compatibility for templates/tests
        object.__setattr__(self, 'image', self.image_url)

    @property
    def formatted_price(self) -> str:
        """Return formatted price string."""
        return f"${self.price:.2f}"

    def to_dict(self) -> Dict[str, Union[str, float]]:
        """Convert book to dictionary representation."""
        return {
            "title": self.title,
            "author": self.author,
            "category": self.category,
            "price": self.price,
            "image_url": self.image_url,
            "description": self.description,
        }


class CartItem:
    """Enhanced cart item with validation and helper methods."""

    def __init__(self, book: Book, quantity: int = 1):
        """Initialize cart item with validation.
        
        Args:
            book: Book object
            quantity: Item quantity (default: 1)
            
        Raises:
            ValueError: If quantity is invalid
        """
        self.book = book
        self.quantity = ValidationUtils.validate_quantity(quantity)

    def get_total_price(self) -> float:
        """Calculate total price for this cart item."""
        return self.book.price * self.quantity

    def get_formatted_total(self) -> str:
        """Get formatted total price string."""
        return f"${self.get_total_price():.2f}"

    def update_quantity(self, quantity: int) -> None:
        """Update item quantity with validation.
        
        Args:
            quantity: New quantity
            
        Raises:
            ValueError: If quantity is invalid
        """
        self.quantity = ValidationUtils.validate_quantity(quantity)

    def to_dict(self) -> Dict[str, Union[str, int, float]]:
        """Convert cart item to dictionary."""
        return {
            "book": self.book.to_dict(),
            "quantity": self.quantity,
            "total_price": self.get_total_price(),
        }


class Cart:
    """Enhanced shopping cart with improved performance and validation."""

    def __init__(self) -> None:
        """Initialize empty cart."""
        self.items: Dict[str, CartItem] = {}

    def add_book(self, book: Book, quantity: Union[int, str] = 1) -> None:
        """Add book to cart with quantity validation.
        
        Args:
            book: Book to add
            quantity: Quantity to add (default: 1)
            
        Raises:
            ValueError: If quantity is invalid
        """
        normalized_quantity = ValidationUtils.validate_quantity(quantity, allow_zero=True)
        if normalized_quantity == 0:
            return  # Treat zero as no-op

        existing = self.items.get(book.title)
        if existing:
            existing.quantity += normalized_quantity
        else:
            self.items[book.title] = CartItem(book, normalized_quantity)

    def remove_book(self, book_title: str) -> None:
        """Remove book from cart.
        
        Args:
            book_title: Title of book to remove
        """
        self.items.pop(book_title, None)

    def update_quantity(self, book_title: str, quantity: Union[int, str]) -> None:
        """Update book quantity with validation.
        
        Args:
            book_title: Title of book to update
            quantity: New quantity
            
        Raises:
            ValueError: If quantity is invalid
        """
        if book_title not in self.items:
            return

        normalized_quantity = ValidationUtils.validate_quantity(quantity, allow_zero=True)
        if normalized_quantity == 0:
            del self.items[book_title]
        else:
            self.items[book_title].quantity = normalized_quantity

    def get_total_price(self) -> float:
        """Calculate total cart price efficiently (O(n) complexity)."""
        return sum(item.get_total_price() for item in self.items.values())

    def get_total_items(self) -> int:
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items.values())

    def clear(self) -> None:
        """Clear all items from cart."""
        self.items.clear()

    def get_items(self) -> List[CartItem]:
        """Get list of cart items."""
        return list(self.items.values())

    def is_empty(self) -> bool:
        """Check if cart is empty."""
        return not self.items

    def get_formatted_total(self) -> str:
        """Get formatted total price string."""
        return f"${self.get_total_price():.2f}"

    # Backwards compatibility methods
    def clear_cart(self) -> None:
        """Backwards compatibility method."""
        self.clear()

    def to_dict(self) -> Dict[str, Union[List[Dict], float, int]]:
        """Convert cart to dictionary representation."""
        return {
            "items": [item.to_dict() for item in self.items.values()],
            "total_price": self.get_total_price(),
            "total_items": self.get_total_items(),
            "is_empty": self.is_empty(),
        }


class User:
    """Enhanced user model with security improvements and validation."""

    def __init__(self, email: str, password: str, name: str = "", address: str = ""):
        """Initialize user with validation and password hashing.
        
        Args:
            email: User email address
            password: User password (will be hashed)
            name: User's full name
            address: User's address
            
        Raises:
            ValueError: If email or password is invalid
        """
        self.email = ValidationUtils.normalize_email(email)
        
        if not password:
            raise ValueError("Password is required")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
            
        self._password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        self.name = name.strip()
        self.address = address.strip()
        self.orders: List[Order] = []
        self.created_at: datetime = datetime.now()
        self.last_login: Optional[datetime] = None

    @property
    def password_hash(self) -> bytes:
        """Get password hash (read-only)."""
        return self._password_hash

    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash.
        
        Args:
            password: Password to verify
            
        Returns:
            True if password is correct
        """
        if not isinstance(password, str):
            return False
        return bcrypt.checkpw(password.encode("utf-8"), self._password_hash)

    def change_password(self, new_password: str) -> None:
        """Change user password with validation.
        
        Args:
            new_password: New password
            
        Raises:
            ValueError: If new password is invalid
        """
        if not new_password:
            raise ValueError("New password must not be empty")
        if len(new_password) < 8:
            raise ValueError("New password must be at least 8 characters long")
            
        self._password_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())

    def add_order(self, order: Order) -> None:
        """Add order to user's order history.
        
        Args:
            order: Order to add
        """
        self.orders.append(order)

    def get_order_history(self, *, sorted_by_date: bool = True) -> List[Order]:
        """Get user's order history.
        
        Args:
            sorted_by_date: Whether to sort orders by date (newest first)
            
        Returns:
            List of user's orders
        """
        if sorted_by_date and self.orders:
            # Create a copy to avoid modifying the original list
            sorted_orders = sorted(self.orders, key=lambda order: order.order_date, reverse=True)
            return sorted_orders
        return self.orders.copy()

    def update_last_login(self) -> None:
        """Update last login timestamp."""
        self.last_login = datetime.now()

    def to_dict(self) -> Dict[str, Union[str, List[Dict], Optional[str]]]:
        """Convert user to dictionary representation."""
        return {
            "email": self.email,
            "name": self.name,
            "address": self.address,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "order_count": len(self.orders),
        }


class Order:
    """Enhanced order model with comprehensive validation and backwards compatibility."""

    def __init__(self, *args, **kwargs):
        """Initialize order with flexible constructor for backwards compatibility."""
        if len(args) == 3 and not kwargs:
            # Legacy signature: items, total_amount, shipping_address
            items, total_amount, shipping_address = args
            order_id = str(uuid.uuid4())[:8].upper()
            user_email = ""
            shipping_info = {"address": shipping_address}
            payment_info = {}
        else:
            # New signature with keyword arguments
            order_id = kwargs.pop("order_id", None)
            user_email = kwargs.pop("user_email", None)
            items = kwargs.pop("items", None)
            shipping_info = kwargs.pop("shipping_info", None)
            payment_info = kwargs.pop("payment_info", None)
            total_amount = kwargs.pop("total_amount", None)

            # Handle positional arguments
            positional = list(args)
            if positional:
                order_id = positional.pop(0)
            if positional:
                user_email = positional.pop(0)
            if positional:
                items = positional.pop(0)
            if positional:
                shipping_info = positional.pop(0)
            if positional:
                payment_info = positional.pop(0)
            if positional:
                total_amount = positional.pop(0)

            # Set defaults and validate
            order_id = order_id or str(uuid.uuid4())[:8].upper()
            user_email = ValidationUtils.normalize_email(user_email or "") if user_email else ""
            items = list(items or [])
            shipping_info = shipping_info or {}
            payment_info = payment_info or {}
            total_amount = float(total_amount or 0.0)

        # Validate order data
        if total_amount < 0:
            raise ValueError("Order total cannot be negative")
        if not items:
            raise ValueError("Order must contain at least one item")

        self.order_id: str = order_id
        self.user_email: str = user_email
        self.items: List[CartItem] = items
        self.shipping_info: Dict[str, str] = shipping_info
        self.payment_info: Dict[str, str] = payment_info
        self.total_amount: float = total_amount
        self.order_date: datetime = datetime.now()
        self.status: str = "Confirmed"

    def get_formatted_total(self) -> str:
        """Get formatted total amount."""
        return f"${self.total_amount:.2f}"

    def get_item_count(self) -> int:
        """Get total number of items in order."""
        return sum(item.quantity for item in self.items)

    def update_status(self, new_status: str) -> None:
        """Update order status.
        
        Args:
            new_status: New status for the order
        """
        valid_statuses = ["Confirmed", "Processing", "Shipped", "Delivered", "Cancelled"]
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}")
        self.status = new_status

    def to_dict(self) -> Dict[str, Union[str, List[Dict], float]]:
        """Convert order to dictionary representation."""
        return {
            "order_id": self.order_id,
            "user_email": self.user_email,
            "items": [
                {
                    "title": item.book.title,
                    "quantity": item.quantity,
                    "price": item.book.price,
                    "total": item.get_total_price(),
                }
                for item in self.items
            ],
            "shipping_info": self.shipping_info,
            "payment_info": self.payment_info,
            "total_amount": self.total_amount,
            "order_date": self.order_date.strftime("%Y-%m-%d %H:%M:%S"),
            "status": self.status,
            "item_count": self.get_item_count(),
        }


class PaymentGateway:
    """Enhanced payment gateway with comprehensive validation."""

    @staticmethod
    def process_payment(payment_info: Dict[str, str]) -> Dict[str, Union[bool, str, Optional[str]]]:
        """Process payment with enhanced validation.
        
        Args:
            payment_info: Payment information dictionary
            
        Returns:
            Dictionary with success status, message, and transaction ID
        """
        payment_method = (payment_info.get("payment_method") or "").strip().lower()

        if payment_method == "credit_card":
            return PaymentGateway._process_credit_card(payment_info)
        elif payment_method == "paypal":
            return PaymentGateway._process_paypal(payment_info)
        else:
            return {
                "success": False,
                "message": "Payment failed: Invalid payment method",
                "transaction_id": None,
            }

    @staticmethod
    def _process_credit_card(payment_info: Dict[str, str]) -> Dict[str, Union[bool, str, Optional[str]]]:
        """Process credit card payment with validation."""
        card_number = (payment_info.get("card_number") or "").replace(" ", "")
        expiry_date = (payment_info.get("expiry_date") or "").strip()
        cvv = (payment_info.get("cvv") or "").strip()

        # Validate required fields
        if not all([card_number, expiry_date, cvv]):
            return {
                "success": False,
                "message": "Payment failed: Missing required credit card information",
                "transaction_id": None,
            }

        # Validate card number format
        if not ValidationUtils.validate_card_number(card_number):
            return {
                "success": False,
                "message": "Payment failed: Invalid card number format",
                "transaction_id": None,
            }

        # Mock validation: cards ending in '1111' fail
        if card_number.endswith("1111"):
            return {
                "success": False,
                "message": "Payment failed: Invalid card number",
                "transaction_id": None,
            }

        # Generate transaction ID
        transaction_id = f"TXN{uuid.uuid4().int % 1_000_000:06d}"
        return {
            "success": True,
            "message": "Payment processed successfully",
            "transaction_id": transaction_id,
        }

    @staticmethod
    def _process_paypal(payment_info: Dict[str, str]) -> Dict[str, Union[bool, str, Optional[str]]]:
        """Process PayPal payment with validation."""
        paypal_email = (payment_info.get("paypal_email") or "").strip()
        
        if not paypal_email:
            return {
                "success": False,
                "message": "Payment failed: PayPal email required",
                "transaction_id": None,
            }
            
        if not ValidationUtils.validate_email(paypal_email):
            return {
                "success": False,
                "message": "Payment failed: Invalid PayPal email format",
                "transaction_id": None,
            }

        # Generate transaction ID
        transaction_id = f"TXN{uuid.uuid4().int % 1_000_000:06d}"
        return {
            "success": True,
            "message": "Payment processed successfully",
            "transaction_id": transaction_id,
        }


class EmailService:
    """Enhanced email service with better error handling and formatting."""

    @staticmethod
    def send_order_confirmation(user_email: str, order: Order) -> bool:
        """Send order confirmation email with enhanced formatting.
        
        Args:
            user_email: Recipient email address
            order: Order object
            
        Returns:
            True if email was sent successfully
        """
        if not ValidationUtils.validate_email(user_email):
            print(f"ERROR: Invalid email format: {user_email}")
            return False

        try:
            print("\n" + "=" * 50)
            print("📧 EMAIL CONFIRMATION SENT")
            print("=" * 50)
            print(f"To: {user_email}")
            print(f"Subject: Order Confirmation - #{order.order_id}")
            print(f"Date: {order.order_date.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"\nOrder Summary:")
            print(f"Order ID: {order.order_id}")
            print(f"Total: {order.get_formatted_total()}")
            print(f"Items ({order.get_item_count()}):")
            
            for item in order.items:
                print(f"  • {item.book.title} x{item.quantity} @ {item.book.formatted_price}")
            
            if order.shipping_info:
                print(f"\nShipping to:")
                print(f"  {order.shipping_info.get('name', 'N/A')}")
                print(f"  {order.shipping_info.get('address', 'N/A')}")
                print(f"  {order.shipping_info.get('city', 'N/A')}, {order.shipping_info.get('zip_code', 'N/A')}")
            
            print("=" * 50 + "\n")
            return True
            
        except Exception as exc:
            print(f"ERROR sending email: {exc}")
            return False
