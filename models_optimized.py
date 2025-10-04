"""
Optimized Models - Bug fixes and performance improvements
This file contains the improved versions of the original models.py with fixes for all identified issues
"""
import bcrypt
import re
from datetime import datetime


class Book:
    """Book model - no changes needed, already well implemented"""
    def __init__(self, title, category, price, image):
        self.title = title
        self.category = category
        self.price = price
        self.image = image


class CartItem:
    """CartItem model - no changes needed, already well implemented"""
    def __init__(self, book, quantity=1):
        self.book = book
        self.quantity = quantity
    
    def get_total_price(self):
        return self.book.price * self.quantity


class Cart:
    """
    OPTIMIZED Cart class with bug fixes and performance improvements
    
    FIXES:
    1. update_quantity now properly removes items when quantity <= 0
    2. Optimized get_total_price to use efficient calculation O(n) instead of O(n*m)
    3. Added input validation for quantities
    """
    def __init__(self):
        self.items = {}

    def add_book(self, book, quantity=1):
        """Add book to cart with quantity validation"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
            
        if book.title in self.items:
            self.items[book.title].quantity += quantity
        else:
            self.items[book.title] = CartItem(book, quantity)

    def remove_book(self, book_title):
        """Remove book from cart"""
        if book_title in self.items:
            del self.items[book_title]

    def update_quantity(self, book_title, quantity):
        """
        FIXED: Update quantity with proper validation and removal of zero quantities
        """
        if not isinstance(quantity, int):
            raise ValueError("Quantity must be an integer")
            
        if book_title in self.items:
            if quantity <= 0:
                # FIX: Remove item when quantity is 0 or negative
                del self.items[book_title]
            else:
                self.items[book_title].quantity = quantity

    def get_total_price(self):
        """
        PERFORMANCE FIX: Optimized from O(n*m) to O(n) complexity
        Original used nested loop, now uses efficient calculation
        """
        # OLD INEFFICIENT CODE (commented out):
        # total = 0
        # for item in self.items.values():
        #     for i in range(item.quantity):  # Unnecessary nested loop
        #         total += item.book.price
        # return total
        
        # NEW EFFICIENT CODE:
        return sum(item.book.price * item.quantity for item in self.items.values())

    def get_total_items(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items.values())

    def clear(self):
        """Clear all items from cart"""
        self.items = {}

    def get_items(self):
        """Get list of cart items"""
        return list(self.items.values())

    def is_empty(self):
        """Check if cart is empty"""
        return len(self.items) == 0


class User:
    """
    OPTIMIZED User class with security fixes and performance improvements
    
    FIXES:
    1. Password hashing for security
    2. Email normalization (case-insensitive)
    3. Removed unused attributes to save memory
    4. Optimized order management
    """
    def __init__(self, email, password, name="", address=""):
        # FIX: Normalize email to lowercase for case-insensitive comparison
        self.email = email.lower().strip()
        
        # SECURITY FIX: Hash password instead of storing plain text
        self.password_hash = self._hash_password(password)
        
        self.name = name
        self.address = address
        self.orders = []
        
        # MEMORY OPTIMIZATION: Removed unused attributes
        # Removed: self.temp_data = []
        # Removed: self.cache = {}
    
    def _hash_password(self, password):
        """Hash password using bcrypt for security"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def change_password(self, new_password):
        """Change user password with proper hashing"""
        self.password_hash = self._hash_password(new_password)
    
    def add_order(self, order):
        """
        PERFORMANCE FIX: Optimized order management
        Only sort when needed instead of on every add
        """
        self.orders.append(order)
        # Don't sort here - sort only when getting order history
    
    def get_order_history(self, sorted_by_date=True):
        """
        PERFORMANCE FIX: Optimized order history retrieval
        Sort only when requested, return reference instead of copy
        """
        if sorted_by_date and self.orders:
            # Sort only when needed
            self.orders.sort(key=lambda x: x.order_date, reverse=True)
        
        # Return reference instead of creating new list
        return self.orders


class Order:
    """Order model - minimal changes, already well implemented"""
    def __init__(self, order_id, user_email, items, shipping_info, payment_info, total_amount):
        self.order_id = order_id
        self.user_email = user_email.lower()  # Normalize email
        self.items = items.copy()
        self.shipping_info = shipping_info
        self.payment_info = payment_info
        self.total_amount = total_amount
        self.order_date = datetime.now()
        self.status = "Confirmed"
    
    def to_dict(self):
        """Convert order to dictionary"""
        return {
            'order_id': self.order_id,
            'user_email': self.user_email,
            'items': [{'title': item.book.title, 'quantity': item.quantity, 'price': item.book.price} for item in self.items],
            'shipping_info': self.shipping_info,
            'total_amount': self.total_amount,
            'order_date': self.order_date.strftime('%Y-%m-%d %H:%M:%S'),
            'status': self.status
        }


class PaymentGateway:
    """
    FIXED PaymentGateway with proper validation
    """
    
    @staticmethod
    def process_payment(payment_info):
        """
        FIXED: Enhanced payment processing with proper validation
        """
        # INPUT VALIDATION FIXES
        payment_method = payment_info.get('payment_method', '')
        
        if payment_method == 'credit_card':
            # Validate credit card fields
            card_number = payment_info.get('card_number', '').strip()
            expiry_date = payment_info.get('expiry_date', '').strip()
            cvv = payment_info.get('cvv', '').strip()
            
            # FIX: Validate required fields
            if not card_number or not expiry_date or not cvv:
                return {
                    'success': False,
                    'message': 'Payment failed: Missing required credit card information',
                    'transaction_id': None
                }
            
            # FIX: Validate card number format (basic validation)
            if not re.match(r'^\d{13,19}$', card_number.replace(' ', '')):
                return {
                    'success': False,
                    'message': 'Payment failed: Invalid card number format',
                    'transaction_id': None
                }
            
            # Mock logic: cards ending in '1111' fail, others succeed
            if card_number.endswith('1111'):
                return {
                    'success': False,
                    'message': 'Payment failed: Invalid card number',
                    'transaction_id': None
                }
                
        elif payment_method == 'paypal':
            # FIX: Add PayPal validation
            paypal_email = payment_info.get('paypal_email', '').strip()
            if not paypal_email:
                return {
                    'success': False,
                    'message': 'Payment failed: PayPal email required',
                    'transaction_id': None
                }
            
            # Basic email validation for PayPal
            if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', paypal_email):
                return {
                    'success': False,
                    'message': 'Payment failed: Invalid PayPal email format',
                    'transaction_id': None
                }
        else:
            return {
                'success': False,
                'message': 'Payment failed: Invalid payment method',
                'transaction_id': None
            }
        
        # Generate transaction ID
        import random
        transaction_id = f"TXN{random.randint(100000, 999999)}"
        
        return {
            'success': True,
            'message': 'Payment processed successfully',
            'transaction_id': transaction_id
        }


class EmailService:
    """
    Enhanced EmailService with better error handling
    """
    
    @staticmethod
    def send_order_confirmation(user_email, order):
        """
        IMPROVED: Enhanced email service with validation
        """
        try:
            # Validate email format
            if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', user_email):
                print(f"ERROR: Invalid email format: {user_email}")
                return False
            
            # Mock email sending with better formatting
            print(f"\n{'='*50}")
            print(f"📧 EMAIL CONFIRMATION SENT")
            print(f"{'='*50}")
            print(f"To: {user_email}")
            print(f"Subject: Order Confirmation - #{order.order_id}")
            print(f"Date: {order.order_date.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"\nOrder Summary:")
            print(f"Order ID: {order.order_id}")
            print(f"Total: ${order.total_amount:.2f}")
            print(f"\nItems:")
            for item in order.items:
                print(f"  • {item.book.title} x{item.quantity} @ ${item.book.price:.2f}")
            
            if order.shipping_info:
                print(f"\nShipping to:")
                print(f"  {order.shipping_info.get('name', 'N/A')}")
                print(f"  {order.shipping_info.get('address', 'N/A')}")
                
            print(f"{'='*50}\n")
            return True
            
        except Exception as e:
            print(f"ERROR sending email: {e}")
            return False


# Utility functions for validation
class ValidationUtils:
    """Utility class for common validation functions"""
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not email or not isinstance(email, str):
            return False
        return re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email.strip()) is not None
    
    @staticmethod
    def validate_quantity(quantity_str):
        """Validate and convert quantity string to integer"""
        try:
            if not quantity_str or not quantity_str.strip():
                return 1  # Default quantity
            
            quantity = int(quantity_str.strip())
            if quantity < 0:
                raise ValueError("Quantity cannot be negative")
            return quantity
            
        except (ValueError, TypeError):
            raise ValueError(f"Invalid quantity: {quantity_str}")
    
    @staticmethod
    def normalize_discount_code(code):
        """Normalize discount code for case-insensitive comparison"""
        return code.strip().upper() if code else ""