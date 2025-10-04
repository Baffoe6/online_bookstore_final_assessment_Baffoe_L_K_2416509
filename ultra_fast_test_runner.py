#!/usr/bin/env python3
"""
Ultra-Fast Test Runner with Performance Monitoring
Optimized test execution with comprehensive reporting
"""
import subprocess
import sys
import os
import time
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional
import argparse


class UltraFastTestRunner:
    """High-performance test runner with monitoring"""
    
    def __init__(self):
        self.start_time = time.time()
        self.results = {}
        self.performance_thresholds = {
            'unit_tests_max_time': 30,      # 30 seconds max
            'integration_tests_max_time': 60, # 60 seconds max
            'security_tests_max_time': 45,   # 45 seconds max
            'performance_tests_max_time': 120, # 2 minutes max
            'total_test_time': 300,          # 5 minutes total max
        }
    
    def run_command(self, cmd: List[str], category: str) -> Dict:
        """Run command with timing and error handling"""
        print(f"🚀 Starting {category}...")
        start = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.performance_thresholds.get(f'{category}_max_time', 300)
            )
            
            execution_time = time.time() - start
            
            return {
                'category': category,
                'success': result.returncode == 0,
                'execution_time': execution_time,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start
            print(f"⏰ {category} timed out after {execution_time:.2f}s")
            return {
                'category': category,
                'success': False,
                'execution_time': execution_time,
                'stdout': '',
                'stderr': f'Timeout after {execution_time:.2f}s',
                'returncode': -1
            }
        except Exception as e:
            execution_time = time.time() - start
            print(f"💥 {category} failed with error: {e}")
            return {
                'category': category,
                'success': False,
                'execution_time': execution_time,
                'stdout': '',
                'stderr': str(e),
                'returncode': -2
            }
    
    def run_unit_tests(self) -> Dict:
        """Run optimized unit tests"""
        cmd = [
            'python', '-m', 'pytest',
            'tests/test_models.py',
            '-v',
            '--tb=short',
            '--maxfail=5',
            '--cov=models',
            '--cov-report=xml:coverage-unit.xml',
            '--json-report',
            '--json-report-file=reports/unit-results.json',
            '-x'  # Stop on first failure
        ]
        return self.run_command(cmd, 'unit_tests')
    
    def run_integration_tests(self) -> Dict:
        """Run optimized integration tests"""
        cmd = [
            'python', '-m', 'pytest',
            'tests/test_app_integration.py',
            '-v',
            '--tb=short', 
            '--maxfail=3',
            '--cov=app',
            '--cov-report=xml:coverage-integration.xml',
            '--json-report',
            '--json-report-file=reports/integration-results.json',
            '-x'
        ]
        return self.run_command(cmd, 'integration_tests')
    
    def run_security_tests(self) -> Dict:
        """Run security and edge case tests"""
        cmd = [
            'python', '-m', 'pytest',
            'tests/test_edge_cases.py',
            'tests/test_advanced_edge_cases.py',
            '-v',
            '--tb=short',
            '--maxfail=2',
            '-m', 'security or edge_case',
            '--json-report',
            '--json-report-file=reports/security-results.json'
        ]
        return self.run_command(cmd, 'security_tests')
    
    def run_performance_tests(self) -> Dict:
        """Run performance regression tests"""
        cmd = [
            'python', '-m', 'pytest',
            'tests/test_optimized_suite.py',
            '-v',
            '--tb=short',
            '-m', 'performance',
            '--json-report',
            '--json-report-file=reports/performance-results.json'
        ]
        return self.run_command(cmd, 'performance_tests')
    
    def run_performance_regression_suite(self) -> Dict:
        """Run comprehensive performance regression suite"""
        cmd = ['python', 'performance_regression_suite.py']
        return self.run_command(cmd, 'performance_regression')
    
    def run_parallel_tests(self) -> Dict[str, Dict]:
        """Run tests in parallel for maximum speed"""
        print("⚡ Running tests in parallel for maximum performance...")
        
        # Create reports directory
        Path('reports').mkdir(exist_ok=True)
        
        # Define test suites
        test_suites = [
            self.run_unit_tests,
            self.run_integration_tests, 
            self.run_security_tests,
            self.run_performance_tests,
            self.run_performance_regression_suite,
        ]
        
        results = {}
        
        # Run tests in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all test suites
            future_to_suite = {
                executor.submit(suite): suite.__name__ 
                for suite in test_suites
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_suite):
                suite_name = future_to_suite[future]
                try:
                    result = future.result()
                    results[suite_name] = result
                    
                    status = "✅ PASS" if result['success'] else "❌ FAIL"
                    print(f"{status} {result['category']}: {result['execution_time']:.2f}s")
                    
                except Exception as e:
                    results[suite_name] = {
                        'category': suite_name,
                        'success': False,
                        'execution_time': 0,
                        'stdout': '',
                        'stderr': str(e),
                        'returncode': -3
                    }
                    print(f"💥 {suite_name} crashed: {e}")
        
        return results
    
    def generate_performance_report(self, results: Dict[str, Dict]) -> Dict:
        """Generate comprehensive performance report"""
        total_time = time.time() - self.start_time
        
        # Calculate metrics
        passed_tests = sum(1 for r in results.values() if r['success'])
        total_tests = len(results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Performance analysis
        test_times = {k: v['execution_time'] for k, v in results.items()}
        fastest_test = min(test_times.items(), key=lambda x: x[1]) if test_times else ("none", 0)
        slowest_test = max(test_times.items(), key=lambda x: x[1]) if test_times else ("none", 0)
        
        # Check performance thresholds
        performance_violations = []
        for test_name, result in results.items():
            category = result.get('category', test_name)
            threshold_key = f"{category}_max_time"
            threshold = self.performance_thresholds.get(threshold_key, float('inf'))
            
            if result['execution_time'] > threshold:
                performance_violations.append({
                    'test': test_name,
                    'time': result['execution_time'],
                    'threshold': threshold,
                    'violation': result['execution_time'] - threshold
                })
        
        # Generate report
        report = {
            'timestamp': time.time(),
            'total_execution_time': total_time,
            'test_results': results,
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': total_tests - passed_tests,
                'success_rate': success_rate,
                'fastest_test': fastest_test,
                'slowest_test': slowest_test,
                'performance_violations': performance_violations,
                'within_time_budget': total_time < self.performance_thresholds['total_test_time']
            }
        }
        
        return report
    
    def print_summary_report(self, report: Dict):
        """Print beautiful summary report"""
        print("\n" + "="*80)
        print("🎯 ULTRA-FAST TEST EXECUTION SUMMARY")
        print("="*80)
        
        summary = report['summary']
        
        # Overall status
        overall_success = (summary['failed_tests'] == 0 and 
                         summary['within_time_budget'] and
                         len(summary['performance_violations']) == 0)
        
        status_icon = "🎉" if overall_success else "⚠️"
        status_text = "ALL TESTS PASSED" if overall_success else "ISSUES DETECTED"
        
        print(f"{status_icon} {status_text}")
        print("-" * 80)
        
        # Test results
        print(f"📊 Test Results:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   ✅ Passed: {summary['passed_tests']}")
        print(f"   ❌ Failed: {summary['failed_tests']}")
        print(f"   📈 Success Rate: {summary['success_rate']:.1f}%")
        
        # Performance metrics
        print(f"\n⚡ Performance Metrics:")
        print(f"   Total Time: {report['total_execution_time']:.2f}s")
        print(f"   Time Budget: {self.performance_thresholds['total_test_time']}s")
        print(f"   Fastest Test: {summary['fastest_test'][0]} ({summary['fastest_test'][1]:.2f}s)")
        print(f"   Slowest Test: {summary['slowest_test'][0]} ({summary['slowest_test'][1]:.2f}s)")
        
        # Performance violations
        if summary['performance_violations']:
            print(f"\n🚨 Performance Violations ({len(summary['performance_violations'])}):")
            for violation in summary['performance_violations']:
                print(f"   ⏰ {violation['test']}: {violation['time']:.2f}s > {violation['threshold']:.2f}s (+{violation['violation']:.2f}s)")
        
        # Detailed results
        print(f"\n📋 Detailed Results:")
        for test_name, result in report['test_results'].items():
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {result['category']}: {result['execution_time']:.2f}s")
            
            if not result['success'] and result['stderr']:
                error_preview = result['stderr'][:100] + "..." if len(result['stderr']) > 100 else result['stderr']
                print(f"      Error: {error_preview}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if summary['performance_violations']:
            print("   • Optimize slow tests identified above")
            print("   • Consider parallel execution for slow test suites")
        
        if summary['failed_tests'] > 0:
            print("   • Review and fix failing tests")
            print("   • Check test environment setup")
        
        if overall_success:
            print("   • All systems performing optimally! 🚀")
            print("   • Test suite meets performance standards")
            print("   • Ready for deployment")
        
        print("="*80)
    
    def save_reports(self, report: Dict):
        """Save comprehensive reports"""
        # Save JSON report
        with open('test-execution-report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save CI/CD friendly format
        ci_report = {
            'success': report['summary']['failed_tests'] == 0,
            'total_time': report['total_execution_time'],
            'within_budget': report['summary']['within_time_budget'],
            'performance_violations': len(report['summary']['performance_violations']),
            'tests_passed': report['summary']['passed_tests'],
            'tests_failed': report['summary']['failed_tests']
        }
        
        with open('ci-report.json', 'w') as f:
            json.dump(ci_report, f, indent=2)
        
        print(f"📄 Reports saved: test-execution-report.json, ci-report.json")
    
    def run(self, args) -> int:
        """Main execution function"""
        print("🔥 Ultra-Fast Test Runner Starting...")
        print(f"⚙️  Performance Budget: {self.performance_thresholds['total_test_time']}s")
        
        # Run tests
        if args.sequential:
            print("📝 Running tests sequentially...")
            results = {}
            for suite_func in [self.run_unit_tests, self.run_integration_tests, 
                             self.run_security_tests, self.run_performance_tests]:
                result = suite_func()
                results[suite_func.__name__] = result
                if not result['success'] and args.fail_fast:
                    break
        else:
            results = self.run_parallel_tests()
        
        # Generate and display report
        report = self.generate_performance_report(results)
        self.print_summary_report(report)
        self.save_reports(report)
        
        # Determine exit code
        success = (report['summary']['failed_tests'] == 0 and 
                  report['summary']['within_time_budget'])
        
        exit_code = 0 if success else 1
        print(f"\n🏁 Exiting with code: {exit_code}")
        
        return exit_code


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description='Ultra-Fast Test Runner')
    parser.add_argument('--sequential', action='store_true', 
                       help='Run tests sequentially instead of parallel')
    parser.add_argument('--fail-fast', action='store_true',
                       help='Stop on first test failure (sequential mode only)')
    
    args = parser.parse_args()
    
    runner = UltraFastTestRunner()
    exit_code = runner.run(args)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()