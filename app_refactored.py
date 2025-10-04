"""Refactored Flask application with improved architecture and separation of concerns.

This module provides a clean, maintainable Flask application with:
- Service layer integration
- Centralized configuration
- Enhanced error handling
- Better type safety
- Improved documentation
"""

from __future__ import annotations

import uuid
from functools import wraps
from typing import Dict, Optional

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from config import DEMO_USER, ConfigManager
from models_refactored import (
    Book,
    Cart,
    EmailService,
    Order,
    PaymentGateway,
    User,
    ValidationUtils,
)
from services import BookService, CartService
from services import EmailService as EmailServiceService
from services import OrderService, PaymentService, UserService


def create_app() -> Flask:
    """Application factory pattern for creating Flask app."""
    app = Flask(__name__)

    # Load configuration
    config = ConfigManager.load_config()
    app.config.update(
        {
            "SECRET_KEY": config.security.secret_key,
            "DEBUG": config.debug,
        }
    )

    # Initialize global storage (in production, use database)
    users: Dict[str, User] = {}
    orders: Dict[str, Order] = {}
    cart: Cart = Cart()

    # Make storage available to services (temporary solution)
    app.users = users
    app.orders = orders
    app.cart = cart

    # Seed demo user
    _seed_demo_user(users)

    # Register routes
    _register_routes(app, users, orders, cart)

    return app


def _seed_demo_user(users: Dict[str, User]) -> None:
    """Ensure the demo account exists for integration tests."""
    email = DEMO_USER["email"]
    if email not in users:
        users[email] = User(
            DEMO_USER["email"],
            DEMO_USER["password"],
            DEMO_USER["name"],
            DEMO_USER["address"],
        )


def _register_routes(
    app: Flask, users: Dict[str, User], orders: Dict[str, Order], cart: Cart
) -> None:
    """Register all application routes."""

    def get_current_user() -> Optional[User]:
        """Get current logged-in user."""
        email = session.get("user_email")
        if not email:
            return None
        return users.get(email)

    def login_required(func):
        """Decorator to require login for certain routes."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            if "user_email" not in session:
                flash("Please log in to access this page.", "error")
                return redirect(url_for("login"))
            return func(*args, **kwargs)

        return wrapper

    @app.route("/")
    def index():
        """Home page with book catalog."""
        books = BookService.get_all_books()
        return render_template(
            "index.html", books=books, cart=cart, current_user=get_current_user()
        )

    @app.route("/add-to-cart", methods=["POST"])
    def add_to_cart():
        """Add book to cart with enhanced error handling."""
        book_title = request.form.get("title") or request.form.get("book_title")
        quantity_raw = request.form.get("quantity", "1")

        try:
            quantity = ValidationUtils.validate_quantity(quantity_raw)
        except ValueError as exc:
            flash(f"Invalid quantity: {exc}", "error")
            return redirect(url_for("index"))

        result = CartService.add_to_cart(cart, book_title, quantity)

        if result.success:
            flash(result.message, "success")
        else:
            flash(result.message, "error")

        return redirect(url_for("index"))

    @app.route("/remove-from-cart", methods=["POST"])
    def remove_from_cart():
        """Remove book from cart."""
        book_title = request.form.get("title", "")
        result = CartService.remove_from_cart(cart, book_title)
        flash(result.message, "success")
        return redirect(url_for("view_cart"))

    @app.route("/update-cart", methods=["POST"])
    def update_cart():
        """Update cart item quantity with enhanced validation."""
        book_title = request.form.get("title")
        quantity_raw = request.form.get("quantity", "1")

        try:
            quantity = (
                0
                if quantity_raw.strip() == "0"
                else ValidationUtils.validate_quantity(quantity_raw, allow_zero=True)
            )
        except (AttributeError, ValueError) as exc:
            flash(f"Invalid quantity: {exc}", "error")
            return redirect(url_for("view_cart"))

        result = CartService.update_cart_item(cart, book_title, quantity)
        flash(result.message, "success")
        return redirect(url_for("view_cart"))

    @app.route("/cart")
    def view_cart():
        """View shopping cart."""
        return render_template("cart.html", cart=cart, current_user=get_current_user())

    @app.route("/clear-cart", methods=["POST"])
    def clear_cart():
        """Clear all items from cart."""
        result = CartService.clear_cart(cart)
        flash(result.message, "success")
        return redirect(url_for("view_cart"))

    @app.route("/checkout")
    def checkout():
        """Checkout page."""
        if cart.is_empty():
            flash("Your cart is empty!", "error")
            return redirect(url_for("index"))

        return render_template(
            "checkout.html",
            cart=cart,
            total_price=cart.get_total_price(),
            current_user=get_current_user(),
        )

    def _collect_shipping_info() -> Dict[str, str]:
        """Collect and validate shipping information."""
        return {
            "name": request.form.get("name", "").strip(),
            "email": request.form.get("email", "").strip(),
            "address": request.form.get("address", "").strip(),
            "city": request.form.get("city", "").strip(),
            "zip_code": request.form.get("zip_code", "").strip(),
        }

    def _collect_payment_info() -> Dict[str, str]:
        """Collect and validate payment information."""
        return {
            "payment_method": request.form.get("payment_method", "").strip(),
            "card_number": request.form.get("card_number", "").strip(),
            "expiry_date": request.form.get("expiry_date", "").strip(),
            "cvv": request.form.get("cvv", "").strip(),
            "paypal_email": request.form.get("paypal_email", "").strip(),
        }

    @app.route("/process-checkout", methods=["POST"])
    def process_checkout():
        """Process checkout with enhanced validation and error handling."""
        if cart.is_empty():
            flash("Your cart is empty!", "error")
            return redirect(url_for("index"))

        shipping_info = _collect_shipping_info()
        payment_info = _collect_payment_info()
        discount_code = ValidationUtils.normalize_discount_code(
            request.form.get("discount_code")
        )

        # Validate shipping information
        required_fields = ["name", "email", "address", "city", "zip_code"]
        for field in required_fields:
            if not shipping_info.get(field):
                flash(f"Please fill in the {field.replace('_', ' ')} field", "error")
                return redirect(url_for("checkout"))

        if not ValidationUtils.validate_email(shipping_info["email"]):
            flash("Please enter a valid email address", "error")
            return redirect(url_for("checkout"))

        # Validate payment information
        payment_validation = PaymentService.validate_payment_info(payment_info)
        if not payment_validation.success:
            flash(payment_validation.message, "error")
            return redirect(url_for("checkout"))

        # Calculate total with discount
        total_amount = cart.get_total_price()
        if discount_code:
            new_total, discount_amount, discount_message = (
                OrderService.calculate_discount(total_amount, discount_code)
            )
            if discount_message:
                if "Invalid" in discount_message:
                    flash(discount_message, "error")
                else:
                    flash(discount_message, "success")
                    total_amount = new_total

        # Process payment
        payment_result = PaymentGateway.process_payment(payment_info)
        if not payment_result["success"]:
            flash(payment_result["message"], "error")
            return redirect(url_for("checkout"))

        # Create order
        order_result = OrderService.create_order(
            shipping_info["email"],
            cart.get_items(),
            shipping_info,
            {
                "method": payment_info["payment_method"],
                "transaction_id": payment_result["transaction_id"],
            },
            total_amount,
        )

        if not order_result.success:
            flash(order_result.message, "error")
            return redirect(url_for("checkout"))

        order = order_result.data["order"]
        order_id = order_result.data["order_id"]

        # Send confirmation email
        email_result = EmailServiceService.send_order_confirmation(
            shipping_info["email"], order
        )
        if not email_result.success:
            # Don't fail the order for email issues, just log
            print(f"Email sending failed: {email_result.message}")

        # Clear cart and redirect
        cart.clear()
        session["last_order_id"] = order_id
        flash("Payment successful! Your order has been confirmed.", "success")
        return redirect(url_for("order_confirmation", order_id=order_id))

    @app.route("/order-confirmation/<order_id>")
    def order_confirmation(order_id: str):
        """Order confirmation page."""
        order = OrderService.get_order_by_id(order_id)
        if not order:
            flash("Order not found", "error")
            return redirect(url_for("index"))
        return render_template(
            "order_confirmation.html", order=order, current_user=get_current_user()
        )

    @app.route("/register", methods=["GET", "POST"])
    def register():
        """User registration with enhanced validation."""
        if request.method == "POST":
            email = request.form.get("email", "")
            password = request.form.get("password", "")
            name = request.form.get("name", "").strip()
            address = request.form.get("address", "").strip()

            result = UserService.register_user(email, password, name, address)

            if result.success:
                session["user_email"] = result.data["email"]
                flash("Account created successfully! You are now logged in.", "success")
                return redirect(url_for("index"))
            else:
                flash(result.message, "error")

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """User login with enhanced validation."""
        if request.method == "POST":
            email_raw = request.form.get("email", "")
            password = request.form.get("password", "")

            result = UserService.authenticate_user(email_raw, password)

            if result.success:
                session["user_email"] = result.data["email"]
                flash("Logged in successfully!", "success")
                return redirect(url_for("index"))
            else:
                flash(result.message, "error")

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        """User logout."""
        session.pop("user_email", None)
        flash("Logged out successfully!", "success")
        return redirect(url_for("index"))

    @app.route("/account")
    @login_required
    def account():
        """User account page."""
        return render_template("account.html", current_user=get_current_user())

    @app.route("/update-profile", methods=["POST"])
    @login_required
    def update_profile():
        """Update user profile with enhanced validation."""
        current_user = get_current_user()
        if not current_user:
            flash("User not found", "error")
            return redirect(url_for("account"))

        try:
            current_user.name = request.form.get("name", current_user.name).strip()
            current_user.address = request.form.get(
                "address", current_user.address
            ).strip()

            new_password = request.form.get("new_password", "").strip()
            if new_password:
                current_user.change_password(new_password)
                flash("Password updated successfully!", "success")
            else:
                flash("Profile updated successfully!", "success")
        except ValueError as e:
            flash(f"Profile update failed: {e}", "error")

        return redirect(url_for("account"))

    @app.route("/api/books")
    def get_books_api():
        """API endpoint for books."""
        books = BookService.get_all_books()
        return jsonify([book.to_dict() for book in books])

    @app.route("/api/search")
    def search_books_api():
        """API endpoint for book search."""
        query = request.args.get("q", "")
        if not query:
            return jsonify([])

        books = BookService.search_books(query)
        return jsonify([book.to_dict() for book in books])

    @app.route("/debug/performance")
    def debug_performance():
        """Debug endpoint for performance metrics."""
        if not app.debug:
            return "Debug mode only", 403

        metrics_cart = Cart()
        books = BookService.get_all_books()
        for _ in range(10):
            metrics_cart.add_book(books[0], 100)

        sample_total = metrics_cart.get_total_price()
        return {
            "cart_items": metrics_cart.get_total_items(),
            "sample_total": sample_total,
            "optimization_status": "Optimized - O(n) complexity",
        }

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return render_template("500.html"), 500


# Create the application instance
app = create_app()


if __name__ == "__main__":
    config = ConfigManager.load_config()
    app.run(debug=config.debug, host=config.host, port=config.port)
