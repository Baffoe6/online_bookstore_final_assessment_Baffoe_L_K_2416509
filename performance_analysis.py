"""
Performance Analysis Script for Online Bookstore
This script identifies performance bottlenecks and inefficiencies in the codebase
"""
import timeit
import cProfile
import pstats
from io import StringIO
from models import Book, Cart, User, Order

def analyze_cart_performance():
    """Analyze performance issues in Cart class"""
    print("="*50)
    print("PERFORMANCE ANALYSIS: Cart Operations")
    print("="*50)
    
    # Create test data
    books = [
        Book(f"Book {i}", "Fiction", 10.99, f"book{i}.jpg") 
        for i in range(100)
    ]
    
    cart = Cart()
    
    # Add books to cart with high quantities to expose inefficiency
    for i, book in enumerate(books[:10]):
        cart.add_book(book, 100 + i * 10)  # High quantities to expose O(n*m) issue
    
    # Test the inefficient get_total_price method
    print("\n1. Testing Cart.get_total_price() inefficiency:")
    print("   Current implementation uses nested loops O(n*m)")
    
    def test_inefficient_total():
        return cart.get_total_price()
    
    # Time the inefficient version
    time_inefficient = timeit.timeit(test_inefficient_total, number=1000)
    print(f"   Time for 1000 calls (inefficient): {time_inefficient:.6f} seconds")
    
    # Test efficient version
    def efficient_total_price(cart):
        """Efficient version of get_total_price"""
        return sum(item.book.price * item.quantity for item in cart.items.values())
    
    def test_efficient_total():
        return efficient_total_price(cart)
    
    time_efficient = timeit.timeit(test_efficient_total, number=1000)
    print(f"   Time for 1000 calls (efficient):   {time_efficient:.6f} seconds")
    print(f"   Performance improvement: {time_inefficient/time_efficient:.2f}x faster")
    
    return time_inefficient, time_efficient

def analyze_user_order_management():
    """Analyze inefficiencies in User order management"""
    print("\n2. Testing User.add_order() inefficiency:")
    print("   Current implementation sorts on every add O(n log n)")
    
    user = User("test@test.com", "password")
    
    # Create test orders
    orders = []
    for i in range(100):
        order = Order(f"order{i}", "test@test.com", [], {}, {}, 100.0)
        orders.append(order)
    
    # Test inefficient version (current implementation)
    def test_inefficient_add_orders():
        user_test = User("test@test.com", "password")
        for order in orders:
            user_test.add_order(order)
    
    time_inefficient = timeit.timeit(test_inefficient_add_orders, number=10)
    print(f"   Time for adding 100 orders x10 (inefficient): {time_inefficient:.6f} seconds")
    
    # Test efficient version
    def efficient_add_order(user, order):
        """Efficient version - just append, sort when needed"""
        user.orders.append(order)
    
    def test_efficient_add_orders():
        user_test = User("test@test.com", "password")
        for order in orders:
            efficient_add_order(user_test, order)
        # Sort only when needed (e.g., when getting order history)
        user_test.orders.sort(key=lambda x: x.order_date)
    
    time_efficient = timeit.timeit(test_efficient_add_orders, number=10)
    print(f"   Time for adding 100 orders x10 (efficient):   {time_efficient:.6f} seconds")
    print(f"   Performance improvement: {time_inefficient/time_efficient:.2f}x faster")
    
    return time_inefficient, time_efficient

def profile_cart_operations():
    """Profile cart operations using cProfile"""
    print("\n3. Profiling Cart operations with cProfile:")
    
    # Create profiler
    profiler = cProfile.Profile()
    
    # Create test data
    books = [Book(f"Book {i}", "Fiction", 10.99, f"book{i}.jpg") for i in range(50)]
    cart = Cart()
    
    # Profile cart operations
    profiler.enable()
    
    # Add books
    for book in books:
        cart.add_book(book, 50)  # High quantity to expose inefficiency
    
    # Calculate total multiple times
    for _ in range(100):
        cart.get_total_price()
    
    profiler.disable()
    
    # Get stats
    s = StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats()
    
    print("   Profile results (top 10 functions by cumulative time):")
    print("   " + "="*60)
    
    # Parse and display relevant stats
    lines = s.getvalue().split('\n')
    for i, line in enumerate(lines):
        if 'get_total_price' in line or 'function calls' in line:
            print(f"   {line}")
        if i > 20:  # Show only first 20 lines of detailed stats
            break

def analyze_memory_usage():
    """Analyze unnecessary memory usage"""
    print("\n4. Memory Usage Analysis:")
    print("   Identified unnecessary attributes in User class:")
    
    user = User("test@test.com", "password")
    
    # Show unused attributes
    print(f"   - temp_data (unused): {len(user.temp_data)} items")
    print(f"   - cache (unused): {len(user.cache)} items")
    print("   Recommendation: Remove unused attributes to save memory")

def main():
    """Run complete performance analysis"""
    print("ONLINE BOOKSTORE - PERFORMANCE ANALYSIS")
    print("="*60)
    print("Identifying bottlenecks and inefficiencies...")
    
    # Analyze different components
    cart_times = analyze_cart_performance()
    user_times = analyze_user_order_management()
    profile_cart_operations()
    analyze_memory_usage()
    
    # Summary
    print("\n" + "="*50)
    print("PERFORMANCE ANALYSIS SUMMARY")
    print("="*50)
    print(f"1. Cart.get_total_price() improvement: {cart_times[0]/cart_times[1]:.2f}x faster")
    print(f"2. User.add_order() improvement: {user_times[0]/user_times[1]:.2f}x faster")
    print("3. Memory usage can be reduced by removing unused attributes")
    print("4. Consider using more efficient data structures and algorithms")
    
    print("\nRecommendations:")
    print("- Fix nested loop in Cart.get_total_price()")
    print("- Avoid sorting on every order add in User.add_order()")
    print("- Remove unused instance variables")
    print("- Use list comprehensions and built-in functions")

if __name__ == "__main__":
    main()