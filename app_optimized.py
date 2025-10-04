"""
Optimized Flask Application - Bug fixes and improvements
This file contains the improved version of app.py with all identified bugs fixed
"""
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from models_optimized import Book, Cart, User, Order, PaymentGateway, EmailService, ValidationUtils
import uuid
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key_change_in_production'  # TODO: Use environment variable

# Global storage for users and orders (in production, use a database)
users = {}  # email -> User object
orders = {}  # order_id -> Order object

# Create demo user for testing with hashed password
demo_user = User("demo@bookstore.com", "demo123", "Demo User", "123 Demo Street, Demo City, DC 12345")
users["demo@bookstore.com"] = demo_user

# Create a cart instance to manage the cart
cart = Cart()

# Create a global books list to avoid duplication
BOOKS = [
    Book("The Great Gatsby", "Fiction", 10.99, "/images/books/the_great_gatsby.jpg"),
    Book("1984", "Dystopia", 8.99, "/images/books/1984.jpg"),
    Book("I Ching", "Traditional", 18.99, "/images/books/I-Ching.jpg"),
    Book("Moby Dick", "Adventure", 12.49, "/images/books/moby_dick.jpg")
]

def get_book_by_title(title):
    """Helper function to find a book by title"""
    return next((book for book in BOOKS if book.title == title), None)


def get_current_user():
    """Helper function to get current logged-in user"""
    if 'user_email' in session:
        return users.get(session['user_email'])
    return None


def login_required(f):
    """Decorator to require login for certain routes"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    current_user = get_current_user()
    return render_template('index.html', books=BOOKS, cart=cart, current_user=current_user)


@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    """
    FIXED: Enhanced add_to_cart with proper error handling and validation
    """
    try:
        book_title = request.form.get('title')
        quantity_str = request.form.get('quantity', '1')
        
        # FIX: Proper quantity validation instead of direct int() conversion
        quantity = ValidationUtils.validate_quantity(quantity_str)
        
        # PERFORMANCE FIX: Use existing helper function instead of manual loop
        book = get_book_by_title(book_title)
        
        if book:
            cart.add_book(book, quantity)
            flash(f'Added {quantity} "{book.title}" to cart!', 'success')
        else:
            flash('Book not found!', 'error')
            
    except ValueError as e:
        # FIX: Handle invalid quantity input gracefully
        flash(f'Invalid quantity: {str(e)}', 'error')
    except Exception as e:
        # FIX: Handle unexpected errors
        flash('An error occurred while adding to cart. Please try again.', 'error')

    return redirect(url_for('index'))


@app.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    book_title = request.form.get('title')
    cart.remove_book(book_title)
    flash(f'Removed "{book_title}" from cart!', 'success')
    return redirect(url_for('view_cart'))


@app.route('/update-cart', methods=['POST'])
def update_cart():
    """
    FIXED: Enhanced update_cart with proper error handling
    """
    try:
        book_title = request.form.get('title')
        quantity_str = request.form.get('quantity', '1')
        
        # FIX: Proper quantity validation
        if quantity_str.strip() == '0':
            quantity = 0  # Allow zero for removal
        else:
            quantity = ValidationUtils.validate_quantity(quantity_str)
        
        # The optimized Cart class now handles zero quantities properly
        cart.update_quantity(book_title, quantity)
        
        if quantity <= 0:
            flash(f'Removed "{book_title}" from cart!', 'success')
        else:
            flash(f'Updated "{book_title}" quantity to {quantity}!', 'success')
            
    except ValueError as e:
        flash(f'Invalid quantity: {str(e)}', 'error')
    except Exception as e:
        flash('An error occurred while updating cart. Please try again.', 'error')
    
    return redirect(url_for('view_cart'))


@app.route('/cart')
def view_cart():
    current_user = get_current_user()
    return render_template('cart.html', cart=cart, current_user=current_user)


@app.route('/clear-cart', methods=['POST'])
def clear_cart():
    cart.clear()
    flash('Cart cleared!', 'success')
    return redirect(url_for('view_cart'))


@app.route('/checkout')
def checkout():
    if cart.is_empty():
        flash('Your cart is empty!', 'error')
        return redirect(url_for('index'))
    
    current_user = get_current_user()
    total_price = cart.get_total_price()
    return render_template('checkout.html', cart=cart, total_price=total_price, current_user=current_user)


@app.route('/process-checkout', methods=['POST'])
def process_checkout():
    """
    ENHANCED: Improved checkout processing with better validation and discount code handling
    """
    if cart.is_empty():
        flash('Your cart is empty!', 'error')
        return redirect(url_for('index'))
    
    try:
        # Get form data with validation
        shipping_info = {
            'name': request.form.get('name', '').strip(),
            'email': request.form.get('email', '').strip().lower(),  # Normalize email
            'address': request.form.get('address', '').strip(),
            'city': request.form.get('city', '').strip(),
            'zip_code': request.form.get('zip_code', '').strip()
        }
        
        payment_info = {
            'payment_method': request.form.get('payment_method', '').strip(),
            'card_number': request.form.get('card_number', '').strip(),
            'expiry_date': request.form.get('expiry_date', '').strip(),
            'cvv': request.form.get('cvv', '').strip(),
            'paypal_email': request.form.get('paypal_email', '').strip()
        }
        
        discount_code = request.form.get('discount_code', '')
        
        # Validate required shipping fields
        required_fields = ['name', 'email', 'address', 'city', 'zip_code']
        for field in required_fields:
            if not shipping_info.get(field):
                flash(f'Please fill in the {field.replace("_", " ")} field', 'error')
                return redirect(url_for('checkout'))
        
        # FIX: Validate email format
        if not ValidationUtils.validate_email(shipping_info['email']):
            flash('Please enter a valid email address', 'error')
            return redirect(url_for('checkout'))
        
        # Validate payment method specific fields
        if payment_info['payment_method'] == 'credit_card':
            if not all([payment_info.get('card_number'), payment_info.get('expiry_date'), payment_info.get('cvv')]):
                flash('Please fill in all credit card details', 'error')
                return redirect(url_for('checkout'))
        elif payment_info['payment_method'] == 'paypal':
            if not payment_info.get('paypal_email'):
                flash('Please enter your PayPal email address', 'error')
                return redirect(url_for('checkout'))
        
        # Calculate total with discount
        total_amount = cart.get_total_price()
        discount_applied = 0
        
        # FIX: Case-insensitive discount code handling
        normalized_discount = ValidationUtils.normalize_discount_code(discount_code)
        
        if normalized_discount == 'SAVE10':
            discount_applied = total_amount * 0.10
            total_amount -= discount_applied
            flash(f'Discount applied! You saved ${discount_applied:.2f}', 'success')
        elif normalized_discount == 'WELCOME20':
            discount_applied = total_amount * 0.20
            total_amount -= discount_applied
            flash(f'Welcome discount applied! You saved ${discount_applied:.2f}', 'success')
        elif discount_code:  # Only show error if code was entered
            flash('Invalid discount code', 'error')
        
        # Process payment through enhanced gateway
        payment_result = PaymentGateway.process_payment(payment_info)
        
        if not payment_result['success']:
            flash(payment_result['message'], 'error')
            return redirect(url_for('checkout'))
        
        # Create order
        order_id = str(uuid.uuid4())[:8].upper()
        order = Order(
            order_id=order_id,
            user_email=shipping_info['email'],
            items=cart.get_items(),
            shipping_info=shipping_info,
            payment_info={
                'method': payment_info['payment_method'],
                'transaction_id': payment_result['transaction_id']
            },
            total_amount=total_amount
        )
        
        # Store order
        orders[order_id] = order
        
        # Add order to user if logged in
        current_user = get_current_user()
        if current_user:
            current_user.add_order(order)
        
        # Send confirmation email (enhanced)
        EmailService.send_order_confirmation(shipping_info['email'], order)
        
        # Clear cart
        cart.clear()
        
        # Store order in session for confirmation page
        session['last_order_id'] = order_id
        
        flash('Payment successful! Your order has been confirmed.', 'success')
        return redirect(url_for('order_confirmation', order_id=order_id))
        
    except Exception as e:
        # Enhanced error handling
        flash(f'An error occurred during checkout: {str(e)}', 'error')
        return redirect(url_for('checkout'))


@app.route('/order-confirmation/<order_id>')
def order_confirmation(order_id):
    """Display order confirmation page"""
    order = orders.get(order_id)
    if not order:
        flash('Order not found', 'error')
        return redirect(url_for('index'))
    
    current_user = get_current_user()
    return render_template('order_confirmation.html', order=order, current_user=current_user)


# User Account Management Routes

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    ENHANCED: Improved user registration with better validation
    """
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()  # Normalize email
            password = request.form.get('password', '')
            name = request.form.get('name', '').strip()
            address = request.form.get('address', '').strip()
            
            # Validate required fields
            if not email or not password or not name:
                flash('Please fill in all required fields', 'error')
                return render_template('register.html')
            
            # FIX: Validate email format
            if not ValidationUtils.validate_email(email):
                flash('Please enter a valid email address', 'error')
                return render_template('register.html')
            
            # FIX: Case-insensitive duplicate check (email normalized to lowercase)
            if email in users:
                flash('An account with this email already exists', 'error')
                return render_template('register.html')
            
            # Create new user (password will be hashed automatically)
            user = User(email, password, name, address)
            users[email] = user
            
            # Log in the user
            session['user_email'] = email
            flash('Account created successfully! You are now logged in.', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'error')
            return render_template('register.html')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    ENHANCED: Improved login with hashed password verification
    """
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()  # Normalize email
            password = request.form.get('password', '')
            
            user = users.get(email)
            
            # FIX: Use proper password verification instead of plain text comparison
            if user and user.verify_password(password):
                session['user_email'] = email
                flash('Logged in successfully!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid email or password', 'error')
                
        except Exception as e:
            flash(f'Login failed: {str(e)}', 'error')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """User logout"""
    session.pop('user_email', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))


@app.route('/account')
@login_required
def account():
    """User account page"""
    current_user = get_current_user()
    return render_template('account.html', current_user=current_user)


@app.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    """
    ENHANCED: Update user profile with proper password handling
    """
    try:
        current_user = get_current_user()
        
        current_user.name = request.form.get('name', current_user.name).strip()
        current_user.address = request.form.get('address', current_user.address).strip()
        
        new_password = request.form.get('new_password', '').strip()
        if new_password:
            # FIX: Use proper password hashing instead of plain text
            current_user.change_password(new_password)
            flash('Password updated successfully!', 'success')
        else:
            flash('Profile updated successfully!', 'success')
            
    except Exception as e:
        flash(f'Profile update failed: {str(e)}', 'error')
    
    return redirect(url_for('account'))


# Performance monitoring endpoint (for development/testing)
@app.route('/debug/performance')
def debug_performance():
    """Debug endpoint to show performance metrics"""
    if not app.debug:
        return "Debug mode only", 403
    
    import timeit
    
    # Test cart performance
    test_cart = Cart()
    for i in range(10):
        test_cart.add_book(BOOKS[0], 100)
    
    # Time the optimized total calculation
    time_taken = timeit.timeit(lambda: test_cart.get_total_price(), number=1000)
    
    return {
        'cart_performance': {
            'total_calculation_time_1000_calls': f'{time_taken:.6f}s',
            'cart_items': test_cart.get_total_items(),
            'optimization_status': 'Optimized - O(n) complexity'
        }
    }


if __name__ == '__main__':
    app.run(debug=True)