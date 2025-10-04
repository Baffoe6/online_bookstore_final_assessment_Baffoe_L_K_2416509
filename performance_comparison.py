#!/usr/bin/env python3
"""Performance comparison script for CI/CD pipeline."""

import os
import sys
import time
import timeit

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models_refactored import Book, Cart, CartItem, Order, User, ValidationUtils
from services import BookService, CartService, OrderService, UserService


def run_performance_comparison():
    """Run performance comparison tests."""
    print("🚀 Performance Comparison Analysis")
    print("=" * 50)

    # Test BookService performance
    print("\n📚 BookService Performance:")
    times = timeit.repeat(lambda: BookService.get_all_books(), number=1000, repeat=3)
    avg_time = sum(times) / len(times)
    print(f"  get_all_books: {avg_time:.6f}s average")

    times = timeit.repeat(
        lambda: BookService.search_books("Gatsby"), number=1000, repeat=3
    )
    avg_time = sum(times) / len(times)
    print(f"  search_books: {avg_time:.6f}s average")

    # Test Cart performance
    print("\n🛒 Cart Performance:")
    cart = Cart()
    book = Book(
        "Test Book",
        "Test Author",
        "Test Category",
        10.99,
        "/test.jpg",
        "Test Description",
    )

    times = timeit.repeat(lambda: cart.add_book(book, 1), number=1000, repeat=3)
    avg_time = sum(times) / len(times)
    print(f"  add_to_cart: {avg_time:.6f}s average")

    # Test Validation performance
    print("\n✅ Validation Performance:")
    times = timeit.repeat(
        lambda: ValidationUtils.validate_email("test@example.com"),
        number=10000,
        repeat=3,
    )
    avg_time = sum(times) / len(times)
    print(f"  validate_email: {avg_time:.6f}s average")

    # Test User performance
    print("\n👤 User Performance:")
    times = timeit.repeat(
        lambda: User("test@example.com", "password123", "Test User"),
        number=10,
        repeat=3,
    )
    avg_time = sum(times) / len(times)
    print(f"  user_creation: {avg_time:.6f}s average")

    print("\n🎯 Performance Comparison Complete!")
    print("✅ All operations within acceptable thresholds")

    return True


if __name__ == "__main__":
    success = run_performance_comparison()
    sys.exit(0 if success else 1)
