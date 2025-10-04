"""Domain models and utilities for the Online Bookstore application.

This module consolidates all previously duplicated implementations and applies
the performance, security, and validation fixes that originally lived in the
``models_optimized`` module.  It is designed to be self-contained so that the
rest of the application (Flask routes, CLI tools, and tests) can import from a
single source of truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
import uuid
from typing import Dict, List, Optional

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
    """Utility helpers shared across models and views."""

    _email_pattern = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

    @staticmethod
    def normalize_email(email: str) -> str:
        """Normalize email addresses for case-insensitive comparisons."""
        if not email or not isinstance(email, str):
            raise ValueError("Email address is required")
        return email.strip().lower()

    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email format using a pre-compiled regex."""
        if not email or not isinstance(email, str):
            return False
        return cls._email_pattern.match(email.strip()) is not None

    @classmethod
    def validate_quantity(cls, quantity, *, allow_zero: bool = False) -> int:
        """Validate and coerce quantity inputs coming from forms or code."""
        if isinstance(quantity, str):
            stripped = quantity.strip()
            if not stripped:
                if allow_zero:
                    raise ValueError("Quantity cannot be empty")
                return 1
            try:
                quantity = int(stripped)
            except ValueError as exc:  # pragma: no cover - defensive
                raise ValueError(f"Invalid quantity: {quantity}") from exc
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
        """Normalize discount codes for case-insensitive comparisons."""
        return code.strip().upper() if code else ""


@dataclass
class Book:
    """Book model with optional author metadata."""

    title: str
    author: str = ""
    category: str = ""
    price: float = 0.0
    image_url: str = ""

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        self.author = self.author.strip()
        self.category = self.category.strip()
        self.price = float(self.price)
        # Backwards compatibility for templates/tests still expecting ``image``.
        self.image = self.image_url


class CartItem:
    """Represents a single line item in a cart."""

    def __init__(self, book: Book, quantity: int = 1):
        self.book = book
        self.quantity = ValidationUtils.validate_quantity(quantity)

    def get_total_price(self) -> float:
        return self.book.price * self.quantity


class Cart:
    """Shopping cart implementation with validation and helpers."""

    def __init__(self) -> None:
        self.items: Dict[str, CartItem] = {}

    def add_book(self, book: Book, quantity: int | str = 1) -> None:
        normalized_quantity = ValidationUtils.validate_quantity(quantity, allow_zero=True)
        if normalized_quantity == 0:
            return  # Treat zero as a no-op (used for validation flows)

        existing = self.items.get(book.title)
        if existing:
            existing.quantity += normalized_quantity
        else:
            self.items[book.title] = CartItem(book, normalized_quantity)

    def remove_book(self, book_title: str) -> None:
        self.items.pop(book_title, None)

    def update_quantity(self, book_title: str, quantity: int | str) -> None:
        if book_title not in self.items:
            return

        normalized_quantity = ValidationUtils.validate_quantity(quantity, allow_zero=True)
        if normalized_quantity == 0:
            del self.items[book_title]
        else:
            self.items[book_title].quantity = normalized_quantity

    def get_total_price(self) -> float:
        return sum(item.get_total_price() for item in self.items.values())

    def get_total_items(self) -> int:
        return sum(item.quantity for item in self.items.values())

    def clear(self) -> None:
        self.items.clear()

    # Backwards compatibility for older tests/fixtures
    def clear_cart(self) -> None:
        self.clear()

    def get_items(self) -> List[CartItem]:
        return list(self.items.values())

    def is_empty(self) -> bool:
        return not self.items


class User:
    """User account management class with hashed passwords."""

    def __init__(self, email: str, password: str, name: str = "", address: str = ""):
        self.email = ValidationUtils.normalize_email(email)
        if not password:
            raise ValueError("Password is required")
        self._password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        self.name = name.strip()
        self.address = address.strip()
        self.orders: List[Order] = []

    @property
    def password_hash(self) -> bytes:
        return self._password_hash

    def verify_password(self, password: str) -> bool:
        if not isinstance(password, str):
            return False
        return bcrypt.checkpw(password.encode("utf-8"), self._password_hash)

    def change_password(self, new_password: str) -> None:
        if not new_password:
            raise ValueError("New password must not be empty")
        self._password_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())

    def add_order(self, order: "Order") -> None:
        self.orders.append(order)

    def get_order_history(self, *, sorted_by_date: bool = True) -> List["Order"]:
        if sorted_by_date:
            self.orders.sort(key=lambda order: order.order_date, reverse=True)
        return self.orders


class Order:
    """Order management class with backwards-compatible constructor."""

    def __init__(self, *args, **kwargs):
        if len(args) == 3 and not kwargs:
            # Legacy signature: items, total_amount, shipping_address
            items, total_amount, shipping_address = args
            order_id = str(uuid.uuid4())[:8].upper()
            user_email = ""
            shipping_info = {"address": shipping_address}
            payment_info = {}
        else:
            order_id = kwargs.pop("order_id", None)
            user_email = kwargs.pop("user_email", None)
            items = kwargs.pop("items", None)
            shipping_info = kwargs.pop("shipping_info", None)
            payment_info = kwargs.pop("payment_info", None)
            total_amount = kwargs.pop("total_amount", None)

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

            order_id = order_id or str(uuid.uuid4())[:8].upper()
            user_email = ValidationUtils.normalize_email(user_email or "") if user_email else ""
            items = list(items or [])
            shipping_info = shipping_info or {}
            payment_info = payment_info or {}
            total_amount = float(total_amount or 0.0)

        self.order_id: str = order_id
        self.user_email: str = user_email
        self.items: List[CartItem] = list(items or [])
        self.shipping_info: Dict[str, str] = shipping_info or {}
        self.payment_info: Dict[str, str] = payment_info or {}
        self.total_amount: float = float(total_amount)
        self.order_date: datetime = datetime.now()
        self.status: str = "Confirmed"

    def to_dict(self) -> Dict[str, object]:
        return {
            "order_id": self.order_id,
            "user_email": self.user_email,
            "items": [
                {
                    "title": item.book.title,
                    "quantity": item.quantity,
                    "price": item.book.price,
                }
                for item in self.items
            ],
            "shipping_info": self.shipping_info,
            "total_amount": self.total_amount,
            "order_date": self.order_date.strftime("%Y-%m-%d %H:%M:%S"),
            "status": self.status,
        }


class PaymentGateway:
    """Mock payment gateway with validation improvements."""

    @staticmethod
    def process_payment(payment_info: Dict[str, str]) -> Dict[str, object]:
        payment_method = (payment_info.get("payment_method") or "").strip().lower()

        if payment_method == "credit_card":
            card_number = (payment_info.get("card_number") or "").replace(" ", "")
            expiry_date = (payment_info.get("expiry_date") or "").strip()
            cvv = (payment_info.get("cvv") or "").strip()

            if not card_number or not expiry_date or not cvv:
                return {
                    "success": False,
                    "message": "Payment failed: Missing required credit card information",
                    "transaction_id": None,
                }

            if not re.fullmatch(r"\d{13,19}", card_number):
                return {
                    "success": False,
                    "message": "Payment failed: Invalid card number format",
                    "transaction_id": None,
                }

            if card_number.endswith("1111"):
                return {
                    "success": False,
                    "message": "Payment failed: Invalid card number",
                    "transaction_id": None,
                }

        elif payment_method == "paypal":
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
        else:
            return {
                "success": False,
                "message": "Payment failed: Invalid payment method",
                "transaction_id": None,
            }

        transaction_id = f"TXN{uuid.uuid4().int % 1_000_000:06d}"
        return {
            "success": True,
            "message": "Payment processed successfully",
            "transaction_id": transaction_id,
        }


class EmailService:
    """Mock email service with basic validation."""

    @staticmethod
    def send_order_confirmation(user_email: str, order: Order) -> bool:
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
            print("\nItems:")
            for item in order.items:
                print(f"  • {item.book.title} x{item.quantity} @ ${item.book.price:.2f}")
            print(f"\nTotal: ${order.total_amount:.2f}")
            if order.shipping_info:
                print("\nShipping to:")
                print(f"  {order.shipping_info.get('name', 'N/A')}")
                print(f"  {order.shipping_info.get('address', 'N/A')}")
            print("=" * 50 + "\n")
            return True
        except Exception as exc:  # pragma: no cover - defensive
            print(f"ERROR sending email: {exc}")
            return False
