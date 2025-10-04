"""
Performance Regression Testing Suite with Automated Benchmarking
Comprehensive performance monitoring with pass/fail criteria
"""
import time
import cProfile
import pstats
import io
import json
import sys
import os
from dataclasses import dataclass
from typing import Dict, List, Callable, Any, Optional
from contextlib import contextmanager
import tracemalloc
import psutil
from concurrent.futures import ThreadPoolExecutor
import threading

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import Book, Cart, CartItem, User, Order, PaymentGateway
from models_optimized import Cart as OptimizedCart, User as OptimizedUser, ValidationUtils


@dataclass
class PerformanceBenchmark:
    """Performance benchmark result"""
    test_name: str
    execution_time: float
    memory_usage: int
    cpu_usage: float
    operations_per_second: float
    passed: bool
    threshold: float
    improvement_factor: Optional[float] = None


class PerformanceTestSuite:
    """Comprehensive performance testing and regression detection"""
    
    def __init__(self):
        self.benchmarks: List[PerformanceBenchmark] = []
        self.thresholds = {
            'cart_total_calculation': 0.001,  # 1ms max
            'user_order_management': 0.005,   # 5ms max
            'book_search_operations': 0.002,  # 2ms max
            'memory_usage_cart_1000': 50,     # 50MB max
            'concurrent_operations': 0.1,      # 100ms max
        }
    
    @contextmanager
    def performance_monitor(self, test_name: str):
        """Context manager for performance monitoring"""
        # Start monitoring
        tracemalloc.start()
        process = psutil.Process()
        start_cpu = process.cpu_percent()
        start_time = time.perf_counter()
        
        try:
            yield
        finally:
            # Stop monitoring and collect metrics
            end_time = time.perf_counter()
            end_cpu = process.cpu_percent()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            execution_time = end_time - start_time
            memory_mb = peak / 1024 / 1024
            cpu_usage = max(end_cpu - start_cpu, 0)
            
            # Calculate operations per second (approximate)
            ops_per_sec = 1000 / execution_time if execution_time > 0 else 0
            
            # Check against threshold
            threshold = self.thresholds.get(test_name, float('inf'))
            passed = execution_time <= threshold
            
            benchmark = PerformanceBenchmark(
                test_name=test_name,
                execution_time=execution_time,
                memory_usage=int(memory_mb),
                cpu_usage=cpu_usage,
                operations_per_second=ops_per_sec,
                passed=passed,
                threshold=threshold
            )
            
            self.benchmarks.append(benchmark)
            
            # Print real-time results
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {test_name}: {execution_time:.6f}s (threshold: {threshold:.6f}s)")
    
    def test_cart_performance_optimized_vs_original(self):
        """Compare optimized vs original cart performance"""
        print("\n" + "="*60)
        print("CART PERFORMANCE COMPARISON")
        print("="*60)
        
        # Test data
        books = [Book(f"Book {i}", f"Author {i}", "Fiction", 10.99, f"book{i}.jpg") 
                for i in range(100)]
        
        # Original cart performance
        original_cart = Cart()
        for book in books:
            original_cart.add_book(book, 10)
        
        with self.performance_monitor('cart_original_1000_calls'):
            for _ in range(1000):
                total = original_cart.get_total_price()
        
        # Optimized cart performance
        optimized_cart = OptimizedCart()
        for book in books:
            optimized_cart.add_book(book, 10)
        
        with self.performance_monitor('cart_optimized_1000_calls'):
            for _ in range(1000):
                total = optimized_cart.get_total_price()
        
        # Calculate improvement factor
        original_time = self.benchmarks[-2].execution_time
        optimized_time = self.benchmarks[-1].execution_time
        improvement = original_time / optimized_time if optimized_time > 0 else 0
        
        self.benchmarks[-1].improvement_factor = improvement
        print(f"Performance improvement: {improvement:.2f}x faster")
    
    def test_user_management_performance(self):
        """Test user management performance with order history"""
        print("\n" + "="*60) 
        print("USER MANAGEMENT PERFORMANCE")
        print("="*60)
        
        # Original user performance
        original_user = User("test@example.com", "password", "Test User")
        orders = [Order([], 25.99, "123 Test St") for _ in range(100)]
        
        with self.performance_monitor('user_original_100_orders'):
            for order in orders:
                original_user.add_order(order)
        
        # Optimized user performance  
        optimized_user = OptimizedUser("test2@example.com", "password", "Test User 2")
        
        with self.performance_monitor('user_optimized_100_orders'):
            for order in orders:
                optimized_user.add_order(order)
        
        # Test order retrieval performance
        with self.performance_monitor('user_get_order_history'):
            history = optimized_user.get_order_history()
    
    def test_concurrent_cart_operations(self):
        """Test thread safety and performance under concurrent load"""
        print("\n" + "="*60)
        print("CONCURRENT OPERATIONS TEST")
        print("="*60)
        
        cart = OptimizedCart()
        book = Book("Test Book", "Test Author", "Fiction", 15.99, "test.jpg")
        
        def add_items():
            for _ in range(50):
                cart.add_book(book, 1)
        
        def calculate_total():
            for _ in range(100):
                total = cart.get_total_price()
        
        with self.performance_monitor('concurrent_cart_operations'):
            with ThreadPoolExecutor(max_workers=8) as executor:
                # Submit concurrent operations
                futures = []
                
                # Add item operations
                for _ in range(4):
                    futures.append(executor.submit(add_items))
                
                # Total calculation operations
                for _ in range(4):
                    futures.append(executor.submit(calculate_total))
                
                # Wait for completion
                for future in futures:
                    future.result()
    
    def test_memory_usage_optimization(self):
        """Test memory usage with large datasets"""
        print("\n" + "="*60)
        print("MEMORY USAGE OPTIMIZATION")
        print("="*60)
        
        with self.performance_monitor('memory_usage_cart_1000'):
            # Create 1000 carts with items
            carts = []
            books = [Book(f"Book {i}", f"Author {i}", "Fiction", 10.99, f"book{i}.jpg") 
                    for i in range(10)]
            
            for i in range(1000):
                cart = OptimizedCart()
                for book in books:
                    cart.add_book(book, 1)
                carts.append(cart)
    
    def test_validation_performance(self):
        """Test input validation performance"""
        print("\n" + "="*60)
        print("VALIDATION PERFORMANCE")
        print("="*60)
        
        emails = ["valid@example.com", "invalid-email", "test@domain.co.uk"] * 1000
        quantities = ["1", "5", "abc", "-1", "0"] * 1000
        
        with self.performance_monitor('email_validation_3000_calls'):
            for email in emails:
                ValidationUtils.validate_email(email)
        
        with self.performance_monitor('quantity_validation_3000_calls'):
            for qty in quantities:
                try:
                    ValidationUtils.validate_quantity(qty)
                except ValueError:
                    pass
    
    def test_payment_processing_performance(self):
        """Test payment processing performance"""
        print("\n" + "="*60)
        print("PAYMENT PROCESSING PERFORMANCE") 
        print("="*60)
        
        payment_data = {
            'payment_method': 'credit_card',
            'card_number': '4111111111111111',
            'expiry_date': '12/25',
            'cvv': '123'
        }
        
        with self.performance_monitor('payment_processing_1000_calls'):
            for _ in range(1000):
                result = PaymentGateway.process_payment(payment_data)
    
    def profile_code_hotspots(self):
        """Profile code to identify performance hotspots"""
        print("\n" + "="*60)
        print("CODE PROFILING - HOTSPOT ANALYSIS")
        print("="*60)
        
        # Create profiler
        profiler = cProfile.Profile()
        
        # Profile cart operations
        profiler.enable()
        
        cart = OptimizedCart()
        books = [Book(f"Book {i}", f"Author {i}", "Fiction", 10.99, f"book{i}.jpg") 
                for i in range(100)]
        
        for book in books:
            cart.add_book(book, 5)
        
        for _ in range(1000):
            total = cart.get_total_price()
            items = cart.get_total_items()
        
        profiler.disable()
        
        # Generate profile report
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s)
        ps.sort_stats('cumulative')
        ps.print_stats(20)  # Top 20 functions
        
        profile_output = s.getvalue()
        print("Top performance hotspots:")
        print(profile_output)
        
        return profile_output
    
    def run_regression_tests(self):
        """Run complete performance regression test suite"""
        print("🚀 Starting Performance Regression Test Suite")
        print("="*80)
        
        start_time = time.time()
        
        # Run all performance tests
        test_methods = [
            self.test_cart_performance_optimized_vs_original,
            self.test_user_management_performance,
            self.test_concurrent_cart_operations,
            self.test_memory_usage_optimization,
            self.test_validation_performance,
            self.test_payment_processing_performance,
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"❌ Test {test_method.__name__} failed: {e}")
                # Add failed benchmark
                self.benchmarks.append(PerformanceBenchmark(
                    test_name=test_method.__name__,
                    execution_time=float('inf'),
                    memory_usage=0,
                    cpu_usage=0,
                    operations_per_second=0,
                    passed=False,
                    threshold=0
                ))
        
        # Profile code hotspots
        try:
            self.profile_code_hotspots()
        except Exception as e:
            print(f"❌ Code profiling failed: {e}")
        
        total_time = time.time() - start_time
        
        # Generate comprehensive report
        self.generate_performance_report(total_time)
    
    def generate_performance_report(self, total_execution_time: float):
        """Generate comprehensive performance report"""
        print("\n" + "="*80)
        print("PERFORMANCE REGRESSION TEST RESULTS")
        print("="*80)
        
        passed_tests = [b for b in self.benchmarks if b.passed]
        failed_tests = [b for b in self.benchmarks if not b.passed]
        
        print(f"📊 Total Tests: {len(self.benchmarks)}")
        print(f"✅ Passed: {len(passed_tests)}")
        print(f"❌ Failed: {len(failed_tests)}")
        print(f"⏱️  Total Execution Time: {total_execution_time:.3f}s")
        
        print(f"\n{'Test Name':<40} {'Time (s)':<12} {'Threshold':<12} {'Status':<8}")
        print("-" * 80)
        
        for benchmark in self.benchmarks:
            status = "✅ PASS" if benchmark.passed else "❌ FAIL"
            time_str = f"{benchmark.execution_time:.6f}" if benchmark.execution_time != float('inf') else "ERROR"
            threshold_str = f"{benchmark.threshold:.6f}" if benchmark.threshold != float('inf') else "N/A"
            
            print(f"{benchmark.test_name:<40} {time_str:<12} {threshold_str:<12} {status:<8}")
            
            if benchmark.improvement_factor:
                print(f"{'  → Improvement Factor:':<40} {benchmark.improvement_factor:.2f}x")
        
        # Performance insights
        print(f"\n{'PERFORMANCE INSIGHTS'}")
        print("-" * 40)
        
        fastest_test = min(self.benchmarks, key=lambda x: x.execution_time if x.execution_time != float('inf') else float('inf'))
        if fastest_test.execution_time != float('inf'):
            print(f"🚀 Fastest Test: {fastest_test.test_name} ({fastest_test.execution_time:.6f}s)")
        
        total_ops = sum(b.operations_per_second for b in self.benchmarks if b.operations_per_second > 0)
        print(f"⚡ Total Operations/Second: {total_ops:,.0f}")
        
        max_memory = max(b.memory_usage for b in self.benchmarks)
        print(f"💾 Peak Memory Usage: {max_memory} MB")
        
        # Save results to JSON for CI/CD integration
        self.save_results_json()
        
        # Determine overall pass/fail
        overall_passed = len(failed_tests) == 0
        print(f"\n{'🎉 ALL PERFORMANCE TESTS PASSED' if overall_passed else '🚨 PERFORMANCE REGRESSION DETECTED'}")
        
        if not overall_passed:
            print("\nFailed tests details:")
            for test in failed_tests:
                print(f"  ❌ {test.test_name}: {test.execution_time:.6f}s > {test.threshold:.6f}s")
        
        return overall_passed
    
    def save_results_json(self):
        """Save performance results to JSON for CI/CD integration"""
        results = {
            'timestamp': time.time(),
            'total_tests': len(self.benchmarks),
            'passed_tests': len([b for b in self.benchmarks if b.passed]),
            'failed_tests': len([b for b in self.benchmarks if not b.passed]),
            'benchmarks': [
                {
                    'test_name': b.test_name,
                    'execution_time': b.execution_time,
                    'memory_usage': b.memory_usage,
                    'cpu_usage': b.cpu_usage,
                    'operations_per_second': b.operations_per_second,
                    'passed': b.passed,
                    'threshold': b.threshold,
                    'improvement_factor': b.improvement_factor
                }
                for b in self.benchmarks
            ]
        }
        
        with open('performance_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Results saved to performance_results.json")


def main():
    """Main performance testing entry point"""
    suite = PerformanceTestSuite()
    
    try:
        success = suite.run_regression_tests()
        exit_code = 0 if success else 1
    except Exception as e:
        print(f"💥 Performance test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit_code = 1
    
    print(f"\n🏁 Performance testing completed with exit code: {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()