"""Service layer for business logic separation."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from config import BOOK_CATALOG, DISCOUNT_CODES
from models_refactored import (Book, Cart, CartItem, Order, User,
                               ValidationUtils)


@dataclass
class ServiceResult:
    """Generic result container for service operations."""

    success: bool
    message: str
    data: Optional[object] = None
    error_code: Optional[str] = None


class BookService:
    """Service for book-related operations."""

    @staticmethod
    def get_all_books() -> List[Book]:
        """Get all available books."""
        return [
            Book(
                title=book_data["title"],
                author=book_data["author"],
                category=book_data["category"],
                price=book_data["price"],
                image_url=book_data["image_url"],
            )
            for book_data in BOOK_CATALOG
        ]

    @staticmethod
    def get_book_by_title(title: str) -> Optional[Book]:
        """Find a book by its title."""
        books = BookService.get_all_books()
        return next((book for book in books if book.title == title), None)

    @staticmethod
    def search_books(query: str) -> List[Book]:
        """Search books by title, author, or category."""
        books = BookService.get_all_books()
        query_lower = query.lower()
        return [
            book
            for book in books
            if (
                query_lower in book.title.lower()
                or query_lower in book.author.lower()
                or query_lower in book.category.lower()
            )
        ]


class CartService:
    """Service for cart-related operations."""

    @staticmethod
    def add_to_cart(cart: Cart, book_title: str, quantity: int) -> ServiceResult:
        """Add a book to the cart with validation."""
        try:
            validated_quantity = ValidationUtils.validate_quantity(quantity)
            book = BookService.get_book_by_title(book_title)

            if not book:
                return ServiceResult(
                    success=False,
                    message="Book not found!",
                    error_code="BOOK_NOT_FOUND",
                )

            cart.add_book(book, validated_quantity)
            return ServiceResult(
                success=True,
                message=f'Added {validated_quantity} "{book.title}" to cart!',
                data={"book": book, "quantity": validated_quantity},
            )

        except ValueError as e:
            return ServiceResult(
                success=False,
                message=f"Invalid quantity: {e}",
                error_code="INVALID_QUANTITY",
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"An error occurred: {e}",
                error_code="UNKNOWN_ERROR",
            )

    @staticmethod
    def update_cart_item(cart: Cart, book_title: str, quantity: int) -> ServiceResult:
        """Update cart item quantity with validation."""
        try:
            validated_quantity = ValidationUtils.validate_quantity(
                quantity, allow_zero=True
            )
            cart.update_quantity(book_title, validated_quantity)

            if validated_quantity <= 0:
                message = f'Removed "{book_title}" from cart!'
            else:
                message = f'Updated "{book_title}" quantity to {validated_quantity}!'

            return ServiceResult(
                success=True,
                message=message,
                data={"book_title": book_title, "quantity": validated_quantity},
            )

        except ValueError as e:
            return ServiceResult(
                success=False,
                message=f"Invalid quantity: {e}",
                error_code="INVALID_QUANTITY",
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"An error occurred: {e}",
                error_code="UNKNOWN_ERROR",
            )

    @staticmethod
    def remove_from_cart(cart: Cart, book_title: str) -> ServiceResult:
        """Remove a book from the cart."""
        cart.remove_book(book_title)
        return ServiceResult(success=True, message=f'Removed "{book_title}" from cart!')

    @staticmethod
    def clear_cart(cart: Cart) -> ServiceResult:
        """Clear all items from the cart."""
        cart.clear()
        return ServiceResult(success=True, message="Cart cleared!")


class UserService:
    """Service for user-related operations."""

    @staticmethod
    def register_user(
        email: str, password: str, name: str, address: str = ""
    ) -> ServiceResult:
        """Register a new user with validation."""
        try:
            normalized_email = ValidationUtils.normalize_email(email)

            if not ValidationUtils.validate_email(normalized_email):
                return ServiceResult(
                    success=False,
                    message="Please enter a valid email address",
                    error_code="INVALID_EMAIL",
                )

            if not password or not name:
                return ServiceResult(
                    success=False,
                    message="Please fill in all required fields",
                    error_code="MISSING_FIELDS",
                )

            # Check if user already exists (this would be a database check in production)
            # For now, we'll assume users dict is available globally
            from app_refactored import app  # This is a temporary solution

            users = app.users

            if normalized_email in users:
                return ServiceResult(
                    success=False,
                    message="An account with this email already exists",
                    error_code="EMAIL_EXISTS",
                )

            user = User(normalized_email, password, name, address)
            users[normalized_email] = user

            return ServiceResult(
                success=True,
                message="Account created successfully!",
                data={"user": user, "email": normalized_email},
            )

        except ValueError as e:
            return ServiceResult(
                success=False, message=str(e), error_code="VALIDATION_ERROR"
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Registration failed: {e}",
                error_code="UNKNOWN_ERROR",
            )

    @staticmethod
    def authenticate_user(email: str, password: str) -> ServiceResult:
        """Authenticate a user with email and password."""
        try:
            normalized_email = ValidationUtils.normalize_email(email)

            # This would be a database lookup in production
            from app_refactored import app  # This is a temporary solution

            users = app.users

            user = users.get(normalized_email)

            if user and user.verify_password(password):
                return ServiceResult(
                    success=True,
                    message="Authentication successful",
                    data={"user": user, "email": normalized_email},
                )
            else:
                return ServiceResult(
                    success=False,
                    message="Invalid email or password",
                    error_code="INVALID_CREDENTIALS",
                )

        except ValueError as e:
            return ServiceResult(
                success=False, message=str(e), error_code="VALIDATION_ERROR"
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Authentication failed: {e}",
                error_code="UNKNOWN_ERROR",
            )


class OrderService:
    """Service for order-related operations."""

    @staticmethod
    def calculate_discount(
        total_amount: float, discount_code: str
    ) -> Tuple[float, float, str]:
        """Calculate discount amount and return new total, discount amount, and message."""
        normalized_code = ValidationUtils.normalize_discount_code(discount_code)

        if not normalized_code:
            return total_amount, 0.0, ""

        if normalized_code not in DISCOUNT_CODES:
            return total_amount, 0.0, "Invalid discount code"

        discount_info = DISCOUNT_CODES[normalized_code]
        discount_percent = discount_info["discount_percent"]
        discount_amount = total_amount * (discount_percent / 100)
        new_total = total_amount - discount_amount

        message = (
            f"{discount_info['description']} applied! You saved ${discount_amount:.2f}"
        )

        return new_total, discount_amount, message

    @staticmethod
    def create_order(
        user_email: str,
        cart_items: List[CartItem],
        shipping_info: Dict[str, str],
        payment_info: Dict[str, str],
        total_amount: float,
    ) -> ServiceResult:
        """Create a new order."""
        try:
            order_id = str(uuid.uuid4())[:8].upper()

            order = Order(
                order_id=order_id,
                user_email=user_email,
                items=cart_items,
                shipping_info=shipping_info,
                payment_info=payment_info,
                total_amount=total_amount,
            )

            # Store order (this would be database storage in production)
            from app_refactored import app  # This is a temporary solution

            orders = app.orders
            orders[order_id] = order

            # Add order to user if logged in
            from app_refactored import app  # This is a temporary solution

            users = app.users
            user = users.get(user_email)
            if user:
                user.add_order(order)

            return ServiceResult(
                success=True,
                message="Order created successfully",
                data={"order": order, "order_id": order_id},
            )

        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Order creation failed: {e}",
                error_code="ORDER_CREATION_ERROR",
            )

    @staticmethod
    def get_order_by_id(order_id: str) -> Optional[Order]:
        """Get an order by its ID."""
        from app_refactored import app  # This is a temporary solution

        orders = app.orders
        return orders.get(order_id)


class PaymentService:
    """Service for payment-related operations."""

    @staticmethod
    def validate_payment_info(payment_info: Dict[str, str]) -> ServiceResult:
        """Validate payment information."""
        payment_method = payment_info.get("payment_method", "").strip()

        if payment_method == "credit_card":
            return PaymentService._validate_credit_card(payment_info)
        elif payment_method == "paypal":
            return PaymentService._validate_paypal(payment_info)
        else:
            return ServiceResult(
                success=False,
                message="Invalid payment method selected",
                error_code="INVALID_PAYMENT_METHOD",
            )

    @staticmethod
    def _validate_credit_card(payment_info: Dict[str, str]) -> ServiceResult:
        """Validate credit card information."""
        card_number = payment_info.get("card_number", "").strip()
        expiry_date = payment_info.get("expiry_date", "").strip()
        cvv = payment_info.get("cvv", "").strip()

        if not all([card_number, expiry_date, cvv]):
            return ServiceResult(
                success=False,
                message="Please fill in all credit card details",
                error_code="MISSING_CARD_DETAILS",
            )

        # Basic card number validation
        import re

        if not re.fullmatch(r"\d{13,19}", card_number.replace(" ", "")):
            return ServiceResult(
                success=False,
                message="Invalid card number format",
                error_code="INVALID_CARD_FORMAT",
            )

        return ServiceResult(success=True, message="Credit card validation passed")

    @staticmethod
    def _validate_paypal(payment_info: Dict[str, str]) -> ServiceResult:
        """Validate PayPal information."""
        paypal_email = payment_info.get("paypal_email", "").strip()

        if not paypal_email:
            return ServiceResult(
                success=False,
                message="PayPal email required",
                error_code="MISSING_PAYPAL_EMAIL",
            )

        if not ValidationUtils.validate_email(paypal_email):
            return ServiceResult(
                success=False,
                message="Invalid PayPal email format",
                error_code="INVALID_PAYPAL_EMAIL",
            )

        return ServiceResult(success=True, message="PayPal validation passed")


class EmailService:
    """Service for email-related operations."""

    @staticmethod
    def send_order_confirmation(user_email: str, order: Order) -> ServiceResult:
        """Send order confirmation email."""
        try:
            if not ValidationUtils.validate_email(user_email):
                return ServiceResult(
                    success=False,
                    message=f"Invalid email format: {user_email}",
                    error_code="INVALID_EMAIL",
                )

            # Mock email sending (in production, this would use a real email service)
            print("\n" + "=" * 50)
            print("📧 EMAIL CONFIRMATION SENT")
            print("=" * 50)
            print(f"To: {user_email}")
            print(f"Subject: Order Confirmation - #{order.order_id}")
            print(f"Date: {order.order_date.strftime('%Y-%m-%d %H:%M:%S')}")
            print("\nItems:")
            for item in order.items:
                print(
                    f"  • {item.book.title} x{item.quantity} @ ${item.book.price:.2f}"
                )
            print(f"\nTotal: ${order.total_amount:.2f}")
            if order.shipping_info:
                print("\nShipping to:")
                print(f"  {order.shipping_info.get('name', 'N/A')}")
                print(f"  {order.shipping_info.get('address', 'N/A')}")
            print("=" * 50 + "\n")

            return ServiceResult(
                success=True, message="Order confirmation email sent successfully"
            )

        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to send email: {e}",
                error_code="EMAIL_SEND_ERROR",
            )


# Global storage for testing purposes
# These are used by the test suite to mock data
users = {}
orders = {}
