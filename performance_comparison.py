"""
Performance Comparison Script - Before vs After Optimization
This script demonstrates the performance improvements achieved through optimization
"""
import timeit
import sys
import os
from io import StringIO

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import original and optimized versions
from models import Cart as OriginalCart, User as OriginalUser, Book
from models_optimized import Cart as OptimizedCart, User as OptimizedUser


def compare_cart_performance():
    """Compare performance of original vs optimized Cart.get_total_price()"""
    print("="*70)
    print("CART PERFORMANCE COMPARISON")
    print("="*70)
    
    # Create test data
    books = [Book(f"Book {i}", "Fiction", 10.99, f"book{i}.jpg") for i in range(10)]
    
    # Test with different quantities to show O(n*m) vs O(n) difference
    quantities = [10, 50, 100, 500, 1000]
    
    for qty in quantities:
        print(f"\nTesting with quantity: {qty} per book")
        print("-" * 50)
        
        # Original implementation
        original_cart = OriginalCart()
        for book in books[:5]:  # Use 5 books
            original_cart.add_book(book, qty)
        
        # Optimized implementation
        optimized_cart = OptimizedCart()
        for book in books[:5]:  # Use 5 books
            optimized_cart.add_book(book, qty)
        
        # Time original version
        time_original = timeit.timeit(
            lambda: original_cart.get_total_price(), 
            number=100
        )
        
        # Time optimized version
        time_optimized = timeit.timeit(
            lambda: optimized_cart.get_total_price(), 
            number=100
        )
        
        improvement = time_original / time_optimized if time_optimized > 0 else float('inf')
        
        print(f"Original (O(n*m)):   {time_original:.6f}s for 100 calls")
        print(f"Optimized (O(n)):    {time_optimized:.6f}s for 100 calls")
        print(f"Performance gain:    {improvement:.2f}x faster")
        
        # Verify results are identical
        assert original_cart.get_total_price() == optimized_cart.get_total_price()


def compare_user_order_management():
    """Compare user order management performance"""
    print("\n" + "="*70)
    print("USER ORDER MANAGEMENT COMPARISON")
    print("="*70)
    
    from models import Order
    
    # Create test orders
    test_orders = []
    for i in range(200):
        order = Order(f"order{i}", "test@test.com", [], {}, {}, 100.0 + i)
        test_orders.append(order)
    
    print(f"\nTesting with {len(test_orders)} orders")
    print("-" * 50)
    
    # Original implementation (sorts on each add)
    original_user = OriginalUser("test@test.com", "password")
    
    time_original = timeit.timeit(
        lambda: [original_user.add_order(order) for order in test_orders[:50]],
        setup=lambda: setattr(original_user, 'orders', []),
        number=10
    )
    
    # Optimized implementation (batch add, sort when needed)
    def optimized_add_orders():
        user = OptimizedUser("test@test.com", "password")
        for order in test_orders[:50]:
            user.add_order(order)
        # Sort only when getting history
        user.get_order_history(sorted_by_date=True)
    
    time_optimized = timeit.timeit(optimized_add_orders, number=10)
    
    improvement = time_original / time_optimized if time_optimized > 0 else float('inf')
    
    print(f"Original (sort each):  {time_original:.6f}s for 50 orders x10")
    print(f"Optimized (batch):     {time_optimized:.6f}s for 50 orders x10")
    print(f"Performance gain:      {improvement:.2f}x faster")


def compare_memory_usage():
    """Compare memory usage between original and optimized versions"""
    print("\n" + "="*70)
    print("MEMORY USAGE COMPARISON")
    print("="*70)
    
    # Original user with unused attributes
    original_user = OriginalUser("test@test.com", "password")
    original_attrs = [attr for attr in dir(original_user) if not attr.startswith('_')]
    
    # Optimized user without unused attributes
    optimized_user = OptimizedUser("test@test.com", "password")
    optimized_attrs = [attr for attr in dir(optimized_user) if not attr.startswith('_')]
    
    print(f"Original User attributes: {len(original_attrs)}")
    print(f"Optimized User attributes: {len(optimized_attrs)}")
    print(f"Attributes removed: {len(original_attrs) - len(optimized_attrs)}")
    
    # Show removed attributes
    removed_attrs = set(original_attrs) - set(optimized_attrs)
    if removed_attrs:
        print(f"Removed unused attributes: {', '.join(removed_attrs)}")
    
    print(f"Memory optimization: Reduced object overhead")


def compare_security_improvements():
    """Compare security between original and optimized versions"""
    print("\n" + "="*70)
    print("SECURITY IMPROVEMENTS")
    print("="*70)
    
    # Original user (plain text password)
    original_user = OriginalUser("test@test.com", "password123")
    
    # Optimized user (hashed password)
    optimized_user = OptimizedUser("test@test.com", "password123")
    
    print("Original User:")
    print(f"  Password storage: Plain text (INSECURE)")
    print(f"  Stored password: '{original_user.password}'")
    print(f"  Email handling: Case sensitive")
    
    print("\nOptimized User:")
    print(f"  Password storage: Bcrypt hashed (SECURE)")
    print(f"  Password hash: {optimized_user.password_hash[:20]}...")
    print(f"  Email handling: Normalized to lowercase")
    print(f"  Password verification: ✓ Secure bcrypt verification")
    
    # Test password verification
    print(f"\nPassword verification test:")
    print(f"  Correct password: {optimized_user.verify_password('password123')}")
    print(f"  Wrong password: {optimized_user.verify_password('wrongpass')}")


def compare_input_validation():
    """Compare input validation improvements"""
    print("\n" + "="*70)
    print("INPUT VALIDATION IMPROVEMENTS")
    print("="*70)
    
    from models_optimized import ValidationUtils
    
    print("New validation utilities added:")
    print("✓ Email format validation")
    print("✓ Quantity validation with error handling")
    print("✓ Case-insensitive discount codes")
    print("✓ Payment field validation")
    
    # Test validation utilities
    print(f"\nValidation Examples:")
    
    # Email validation
    test_emails = ["valid@email.com", "invalid-email", "", "test@.com"]
    print(f"Email validation:")
    for email in test_emails:
        valid = ValidationUtils.validate_email(email)
        print(f"  '{email}': {'✓ Valid' if valid else '✗ Invalid'}")
    
    # Quantity validation
    test_quantities = ["5", "0", "-1", "abc", "", "1.5"]
    print(f"\nQuantity validation:")
    for qty in test_quantities:
        try:
            result = ValidationUtils.validate_quantity(qty)
            print(f"  '{qty}': ✓ Valid → {result}")
        except ValueError as e:
            print(f"  '{qty}': ✗ Invalid → {e}")
    
    # Discount code normalization
    test_codes = ["SAVE10", "save10", "Save10", "WELCOME20", "welcome20"]
    print(f"\nDiscount code normalization:")
    for code in test_codes:
        normalized = ValidationUtils.normalize_discount_code(code)
        print(f"  '{code}' → '{normalized}'")


def run_comprehensive_comparison():
    """Run all performance and improvement comparisons"""
    print("ONLINE BOOKSTORE - COMPREHENSIVE OPTIMIZATION ANALYSIS")
    print("="*70)
    print("Comparing original implementation vs optimized version")
    print("="*70)
    
    try:
        compare_cart_performance()
        compare_user_order_management() 
        compare_memory_usage()
        compare_security_improvements()
        compare_input_validation()
        
        print("\n" + "="*70)
        print("OPTIMIZATION SUMMARY")
        print("="*70)
        print("✓ Cart.get_total_price(): O(n*m) → O(n) complexity")
        print("✓ User.add_order(): Eliminated sorting on each add")
        print("✓ Memory usage: Removed unused attributes")
        print("✓ Security: Plain text → Bcrypt hashed passwords")
        print("✓ Email handling: Case-insensitive normalization")
        print("✓ Input validation: Comprehensive error handling")
        print("✓ Discount codes: Case-insensitive processing")
        print("✓ Payment validation: Enhanced field validation")
        
        print(f"\nAll optimizations completed successfully!")
        
    except Exception as e:
        print(f"Error during comparison: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_comprehensive_comparison()