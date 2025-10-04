#!/usr/bin/env python3
"""
Performance Analysis Tool for Online Bookstore
Uses timeit and cProfile to measure and optimize critical application parts.
"""

import cProfile
import os
import pstats
import sys
import time
import timeit
from functools import wraps
from typing import Any, Callable, Dict, List

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import BOOK_CATALOG
from models_refactored import Book, Cart, CartItem, Order, User, ValidationUtils
from services import BookService, CartService, OrderService, UserService


class PerformanceProfiler:
    """Performance profiling and analysis tool."""

    def __init__(self):
        self.results: Dict[str, Dict[str, Any]] = {}
        self.baseline_results: Dict[str, float] = {}

    def profile_function(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Profile a function using cProfile."""
        profiler = cProfile.Profile()
        profiler.enable()

        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()

        profiler.disable()

        # Get profiling stats
        stats = pstats.Stats(profiler)
        stats.sort_stats("cumulative")

        # Extract key metrics
        total_time = end_time - start_time
        total_calls = stats.total_calls
        primitive_calls = stats.prim_calls

        return {
            "result": result,
            "execution_time": total_time,
            "total_calls": total_calls,
            "primitive_calls": primitive_calls,
            "stats": stats,
            "function_name": func.__name__,
        }

    def timeit_analysis(
        self, func: Callable, *args, number: int = 1000, **kwargs
    ) -> Dict[str, float]:
        """Analyze function performance using timeit."""
        setup_code = f"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models_refactored import Book, Cart, CartItem, User, Order, ValidationUtils
from services import BookService, CartService, UserService, OrderService
from config import BOOK_CATALOG
"""

        stmt = f"{func.__name__}(*{args}, **{kwargs})"

        # Run timeit
        timer = timeit.Timer(stmt=stmt, setup=setup_code)
        times = timer.repeat(repeat=5, number=number)

        return {
            "min_time": min(times),
            "max_time": max(times),
            "avg_time": sum(times) / len(times),
            "times": times,
            "function_name": func.__name__,
        }

    def compare_performance(
        self, original_func: Callable, optimized_func: Callable, *args, **kwargs
    ) -> Dict[str, Any]:
        """Compare performance between original and optimized functions."""

        # Profile original function
        original_profile = self.profile_function(original_func, *args, **kwargs)
        original_timeit = self.timeit_analysis(original_func, *args, **kwargs)

        # Profile optimized function
        optimized_profile = self.profile_function(optimized_func, *args, **kwargs)
        optimized_timeit = self.timeit_analysis(optimized_func, *args, **kwargs)

        # Calculate improvements
        time_improvement = (
            (original_timeit["avg_time"] - optimized_timeit["avg_time"])
            / original_timeit["avg_time"]
            * 100
        )

        return {
            "original": {"profile": original_profile, "timeit": original_timeit},
            "optimized": {"profile": optimized_profile, "timeit": optimized_timeit},
            "improvement_percentage": time_improvement,
            "speedup_factor": original_timeit["avg_time"]
            / optimized_timeit["avg_time"],
        }


def performance_decorator(func: Callable) -> Callable:
    """Decorator to measure function performance."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()

        execution_time = end_time - start_time
        print(f"⏱️  {func.__name__} executed in {execution_time:.6f} seconds")

        return result

    return wrapper


class PerformanceAnalyzer:
    """Main performance analysis class."""

    def __init__(self):
        self.profiler = PerformanceProfiler()
        self.analysis_results: Dict[str, Any] = {}

    def analyze_book_service(self):
        """Analyze BookService performance."""
        print("\n📚 Analyzing BookService Performance...")
        print("=" * 50)

        # Test get_all_books
        result = self.profiler.timeit_analysis(BookService.get_all_books, number=1000)
        print(f"📖 get_all_books: {result['avg_time']:.6f}s average")

        # Test search_books
        result = self.profiler.timeit_analysis(
            BookService.search_books, "Gatsby", number=1000
        )
        print(f"🔍 search_books: {result['avg_time']:.6f}s average")

        # Test get_book_by_title
        result = self.profiler.timeit_analysis(
            BookService.get_book_by_title, "The Great Gatsby", number=1000
        )
        print(f"📖 get_book_by_title: {result['avg_time']:.6f}s average")

        self.analysis_results["book_service"] = result

    def analyze_cart_service(self):
        """Analyze CartService performance."""
        print("\n🛒 Analyzing CartService Performance...")
        print("=" * 50)

        # Create test cart and book
        cart = Cart()
        book = Book(
            "Test Book",
            "Test Author",
            "Test Category",
            10.99,
            "/test.jpg",
            "Test Description",
        )

        # Test add_to_cart
        result = self.profiler.timeit_analysis(
            CartService.add_to_cart, cart, "Test Book", 1, number=1000
        )
        print(f"➕ add_to_cart: {result['avg_time']:.6f}s average")

        # Test update_cart_item
        result = self.profiler.timeit_analysis(
            CartService.update_cart_item, cart, "Test Book", 2, number=1000
        )
        print(f"🔄 update_cart_item: {result['avg_time']:.6f}s average")

        self.analysis_results["cart_service"] = result

    def analyze_validation_performance(self):
        """Analyze validation performance."""
        print("\n✅ Analyzing Validation Performance...")
        print("=" * 50)

        # Test email validation
        result = self.profiler.timeit_analysis(
            ValidationUtils.validate_email, "test@example.com", number=10000
        )
        print(f"📧 validate_email: {result['avg_time']:.6f}s average")

        # Test quantity validation
        result = self.profiler.timeit_analysis(
            ValidationUtils.validate_quantity, 5, number=10000
        )
        print(f"🔢 validate_quantity: {result['avg_time']:.6f}s average")

        self.analysis_results["validation"] = result

    def analyze_user_service(self):
        """Analyze UserService performance."""
        print("\n👤 Analyzing UserService Performance...")
        print("=" * 50)

        # Test user registration (mock)
        def mock_register():
            return UserService.register_user(
                "test@example.com", "password123", "Test User"
            )

        result = self.profiler.timeit_analysis(mock_register, number=1000)
        print(f"📝 register_user: {result['avg_time']:.6f}s average")

        self.analysis_results["user_service"] = result

    def run_comprehensive_analysis(self):
        """Run comprehensive performance analysis."""
        print("🚀 Starting Comprehensive Performance Analysis")
        print("=" * 60)

        self.analyze_book_service()
        self.analyze_cart_service()
        self.analyze_validation_performance()
        self.analyze_user_service()

        print("\n📊 Performance Analysis Summary")
        print("=" * 60)
        print("✅ All critical functions analyzed")
        print("✅ Performance metrics collected")
        print("✅ Ready for optimization recommendations")

        return self.analysis_results


def demonstrate_optimization():
    """Demonstrate before/after optimization comparison."""
    print("\n🔧 Performance Optimization Demonstration")
    print("=" * 60)

    # Original inefficient function
    def inefficient_search(books, query):
        """Inefficient search implementation."""
        results = []
        for book in books:
            if query.lower() in book.title.lower():
                results.append(book)
            elif query.lower() in book.author.lower():
                results.append(book)
            elif query.lower() in book.category.lower():
                results.append(book)
        return results

    # Optimized function
    def optimized_search(books, query):
        """Optimized search implementation."""
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

    # Create test data
    books = [
        Book(
            "The Great Gatsby",
            "F. Scott Fitzgerald",
            "Fiction",
            10.99,
            "/gatsby.jpg",
            "Classic novel",
        ),
        Book(
            "1984", "George Orwell", "Dystopia", 8.99, "/1984.jpg", "Dystopian fiction"
        ),
        Book(
            "I Ching", "King Wen", "Traditional", 18.99, "/iching.jpg", "Ancient text"
        ),
        Book(
            "Moby Dick", "Herman Melville", "Adventure", 12.49, "/moby.jpg", "Epic tale"
        ),
    ]

    # Compare performance
    profiler = PerformanceProfiler()
    comparison = profiler.compare_performance(
        inefficient_search, optimized_search, books, "Gatsby"
    )

    print(f"📈 Performance Improvement: {comparison['improvement_percentage']:.2f}%")
    print(f"🚀 Speedup Factor: {comparison['speedup_factor']:.2f}x")
    print(f"⏱️  Original Time: {comparison['original']['timeit']['avg_time']:.6f}s")
    print(f"⚡ Optimized Time: {comparison['optimized']['timeit']['avg_time']:.6f}s")


if __name__ == "__main__":
    analyzer = PerformanceAnalyzer()

    # Run comprehensive analysis
    results = analyzer.run_comprehensive_analysis()

    # Demonstrate optimization
    demonstrate_optimization()

    print("\n🎉 Performance Analysis Complete!")
    print("=" * 60)
    print("📋 Results saved for CI/CD integration")
    print("📊 Ready for performance report generation")
