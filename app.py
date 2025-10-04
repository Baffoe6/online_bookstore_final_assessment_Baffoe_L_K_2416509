"""Flask application entry point for the Online Bookstore."""
from __future__ import annotations

import uuid
from functools import wraps
from typing import Dict

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

from models import Book, Cart, EmailService, Order, PaymentGateway, User, ValidationUtils

app = Flask(__name__)
app.secret_key = "change-me"  # In production load from configuration

# In-memory storage (replace with persistent storage in production)
users: Dict[str, User] = {}
orders: Dict[str, Order] = {}
cart: Cart = Cart()

# Catalog definition
BOOKS = [
    Book(
        "The Great Gatsby",
        author="F. Scott Fitzgerald",
        category="Fiction",
        price=10.99,
        image_url="/images/books/the_great_gatsby.jpg",
    ),
    Book(
        "1984",
        author="George Orwell",
        category="Dystopia",
        price=8.99,
        image_url="/images/books/1984.jpg",
    ),
    Book(
        "I Ching",
        author="King Wen of Zhou",
        category="Traditional",
        price=18.99,
        image_url="/images/books/I-Ching.jpg",
    ),
    Book(
        "Moby Dick",
        author="Herman Melville",
        category="Adventure",
        price=12.49,
        image_url="/images/books/moby_dick.jpg",
    ),
]


def _seed_demo_user() -> None:
    """Ensure the demo account exists for integration tests."""
    email = "demo@bookstore.com"
    if email not in users:
        users[email] = User(
            email,
            "demo123",
            "Demo User",
            "123 Demo Street, Demo City, DC 12345",
        )


_seed_demo_user()


def get_book_by_title(title: str) -> Book | None:
    return next((book for book in BOOKS if book.title == title), None)


def get_current_user() -> User | None:
    email = session.get("user_email")
    if not email:
        return None
    return users.get(email)


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_email" not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return wrapper


@app.route("/")
def index():
    return render_template("index.html", books=BOOKS, cart=cart, current_user=get_current_user())


@app.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    book_title = request.form.get("title") or request.form.get("book_title")
    quantity_raw = request.form.get("quantity", "1")

    try:
        quantity = ValidationUtils.validate_quantity(quantity_raw)
    except ValueError as exc:
        flash(f"Invalid quantity: {exc}", "error")
        return redirect(url_for("index"))

    book = get_book_by_title(book_title)
    if not book:
        flash("Book not found!", "error")
        return redirect(url_for("index"))

    cart.add_book(book, quantity)
    flash(f'Added {quantity} "{book.title}" to cart!', "success")
    return redirect(url_for("index"))


@app.route("/remove-from-cart", methods=["POST"])
def remove_from_cart():
    book_title = request.form.get("title", "")
    cart.remove_book(book_title)
    flash(f'Removed "{book_title}" from cart!', "success")
    return redirect(url_for("view_cart"))


@app.route("/update-cart", methods=["POST"])
def update_cart():
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

    cart.update_quantity(book_title, quantity)
    if quantity <= 0:
        flash(f'Removed "{book_title}" from cart!', "success")
    else:
        flash(f'Updated "{book_title}" quantity to {quantity}!', "success")
    return redirect(url_for("view_cart"))


@app.route("/cart")
def view_cart():
    return render_template("cart.html", cart=cart, current_user=get_current_user())


@app.route("/clear-cart", methods=["POST"])
def clear_cart():
    cart.clear()
    flash("Cart cleared!", "success")
    return redirect(url_for("view_cart"))


@app.route("/checkout")
def checkout():
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
    return {
        "name": request.form.get("name", "").strip(),
        "email": request.form.get("email", "").strip(),
        "address": request.form.get("address", "").strip(),
        "city": request.form.get("city", "").strip(),
        "zip_code": request.form.get("zip_code", "").strip(),
    }


def _collect_payment_info() -> Dict[str, str]:
    return {
        "payment_method": request.form.get("payment_method", "").strip(),
        "card_number": request.form.get("card_number", "").strip(),
        "expiry_date": request.form.get("expiry_date", "").strip(),
        "cvv": request.form.get("cvv", "").strip(),
        "paypal_email": request.form.get("paypal_email", "").strip(),
    }


@app.route("/process-checkout", methods=["POST"])
def process_checkout():
    if cart.is_empty():
        flash("Your cart is empty!", "error")
        return redirect(url_for("index"))

    shipping_info = _collect_shipping_info()
    payment_info = _collect_payment_info()
    discount_code = ValidationUtils.normalize_discount_code(request.form.get("discount_code"))

    for field in ["name", "email", "address", "city", "zip_code"]:
        if not shipping_info.get(field):
            flash(f"Please fill in the {field.replace('_', ' ')} field", "error")
            return redirect(url_for("checkout"))

    if not ValidationUtils.validate_email(shipping_info["email"]):
        flash("Please enter a valid email address", "error")
        return redirect(url_for("checkout"))

    method = payment_info.get("payment_method")
    if method == "credit_card":
        if not all(
            [payment_info.get("card_number"), payment_info.get("expiry_date"), payment_info.get("cvv")]
        ):
            flash("Please fill in all credit card details", "error")
            return redirect(url_for("checkout"))
    elif method == "paypal":
        if not payment_info.get("paypal_email"):
            flash("Please enter your PayPal email address", "error")
            return redirect(url_for("checkout"))
    else:
        flash("Invalid payment method selected", "error")
        return redirect(url_for("checkout"))

    total_amount = cart.get_total_price()
    if discount_code == "SAVE10":
        total_amount *= 0.90
        flash("Discount applied! You saved 10%", "success")
    elif discount_code == "WELCOME20":
        total_amount *= 0.80
        flash("Welcome discount applied! You saved 20%", "success")
    elif discount_code:
        flash("Invalid discount code", "error")

    payment_result = PaymentGateway.process_payment(payment_info)
    if not payment_result["success"]:
        flash(payment_result["message"], "error")
        return redirect(url_for("checkout"))

    order_id = str(uuid.uuid4())[:8].upper()
    order = Order(
        order_id,
        shipping_info["email"],
        cart.get_items(),
        shipping_info,
        {"method": method, "transaction_id": payment_result["transaction_id"]},
        total_amount,
    )

    orders[order_id] = order
    current_user = get_current_user()
    if current_user:
        current_user.add_order(order)

    EmailService.send_order_confirmation(shipping_info["email"], order)
    cart.clear()
    session["last_order_id"] = order_id
    flash("Payment successful! Your order has been confirmed.", "success")
    return redirect(url_for("order_confirmation", order_id=order_id))


@app.route("/order-confirmation/<order_id>")
def order_confirmation(order_id: str):
    order = orders.get(order_id)
    if not order:
        flash("Order not found", "error")
        return redirect(url_for("index"))
    return render_template("order_confirmation.html", order=order, current_user=get_current_user())


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            email = ValidationUtils.normalize_email(request.form.get("email", ""))
        except ValueError as exc:
            flash(str(exc), "error")
            return render_template("register.html")

        password = request.form.get("password", "")
        name = request.form.get("name", "").strip()
        address = request.form.get("address", "").strip()

        if not password or not name:
            flash("Please fill in all required fields", "error")
            return render_template("register.html")

        if email in users:
            flash("An account with this email already exists", "error")
            return render_template("register.html")

        user = User(email, password, name, address)
        users[email] = user
        session["user_email"] = email
        flash("Account created successfully! You are now logged in.", "success")
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email_raw = request.form.get("email", "")
        password = request.form.get("password", "")

        try:
            email = ValidationUtils.normalize_email(email_raw)
        except ValueError:
            flash("Please enter a valid email address", "error")
            return render_template("login.html")

        user = users.get(email)
        if user and user.verify_password(password):
            session["user_email"] = email
            flash("Logged in successfully!", "success")
            return redirect(url_for("index"))

        flash("Invalid email or password", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_email", None)
    flash("Logged out successfully!", "success")
    return redirect(url_for("index"))


@app.route("/account")
@login_required
def account():
    return render_template("account.html", current_user=get_current_user())


@app.route("/update-profile", methods=["POST"])
@login_required
def update_profile():
    current_user = get_current_user()
    current_user.name = request.form.get("name", current_user.name).strip()
    current_user.address = request.form.get("address", current_user.address).strip()

    new_password = request.form.get("new_password", "").strip()
    if new_password:
        current_user.change_password(new_password)
        flash("Password updated successfully!", "success")
    else:
        flash("Profile updated successfully!", "success")
    return redirect(url_for("account"))


@app.route("/api/books")
def get_books_api():
    return jsonify(
        [
            {
                "title": book.title,
                "author": book.author,
                "category": book.category,
                "price": book.price,
                "image_url": book.image_url,
            }
            for book in BOOKS
        ]
    )


@app.route("/debug/performance")
def debug_performance():
    metrics_cart = Cart()
    for _ in range(10):
        metrics_cart.add_book(BOOKS[0], 100)

    sample_total = metrics_cart.get_total_price()
    return {
        "cart_items": metrics_cart.get_total_items(),
        "sample_total": sample_total,
        "optimization_status": "Optimized - O(n) complexity",
    }


if __name__ == "__main__":
    app.run(debug=True)
