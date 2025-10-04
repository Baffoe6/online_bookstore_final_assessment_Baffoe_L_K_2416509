# 📚 Online Bookstore - Final Assessment

A modern, production-ready online bookstore application built with Flask, featuring comprehensive testing, CI/CD pipeline, and performance optimization.

## 🌟 Features

- **📖 Book Catalog**: Browse and search through a curated collection of books
- **🛒 Shopping Cart**: Add/remove items, update quantities
- **👤 User Management**: Registration, authentication, and account management
- **💳 Payment Processing**: Support for credit card and PayPal payments
- **📧 Order Management**: Order tracking and email confirmations
- **🔍 Search & Filter**: Advanced search by title, author, and category
- **🎨 Responsive Design**: Modern UI with mobile-friendly templates

## 🏗️ Architecture

### Clean Architecture Implementation
- **Service Layer**: Business logic separated from Flask routes
- **Model Layer**: Enhanced data models with validation
- **Configuration Management**: Centralized settings and environment variables
- **Type Safety**: Comprehensive type hints throughout the codebase

### Core Components
- `app_refactored.py` - Main Flask application with route handlers
- `models_refactored.py` - Data models with validation and business logic
- `services.py` - Service layer for business operations
- `config.py` - Centralized configuration management

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Baffoe6/online_bookstore_final_assessment_Baffoe_L_K_2416509.git
   cd online_bookstore_final_assessment_Baffoe_L_K_2416509
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app_refactored.py
   ```

4. **Access the application**
   - Open your browser to `http://localhost:5000`
   - Use demo credentials: `demo@bookstore.com` / `demo1234`

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_refactored_models.py -v
python -m pytest tests/test_refactored_services.py -v
python -m pytest tests/test_performance.py -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

### Test Coverage
- **111 comprehensive tests** covering all functionality
- **Unit tests** for models and services
- **Integration tests** for API endpoints
- **Performance tests** with `timeit` and `cProfile`
- **Edge case testing** for error conditions

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)
```bash
# Build and run all services
docker-compose up --build

# Run in background
docker-compose up -d

# Stop services
docker-compose down
```

### Using Docker directly
```bash
# Build the image
docker build -t online-bookstore .

# Run the container
docker run -p 5000:5000 online-bookstore
```

## 📊 Performance Analysis

The project includes comprehensive performance analysis tools:

```bash
# Run performance analysis
python performance_analysis.py

# Performance metrics include:
# - Book service operations (search, catalog loading)
# - User authentication and password hashing
# - Cart operations and order processing
# - Database operations and caching
```

### Performance Optimizations
- **Caching**: Book catalog caching for faster load times
- **Optimized Queries**: Efficient database operations
- **Password Security**: Configurable bcrypt rounds for security/performance balance
- **Service Layer**: Separated business logic for better maintainability

## 🔄 CI/CD Pipeline

### GitHub Actions Workflows
The project includes a comprehensive CI/CD pipeline with:

- **🧪 Test Pipeline**: Automated testing on every push/PR
- **🔒 Security Scanning**: Bandit and Safety vulnerability checks
- **📝 Code Quality**: Black, isort, MyPy, and Pylint checks
- **🚀 Deployment**: Automated deployment to staging/production
- **📢 Notifications**: Pipeline status notifications

### Local Development
```bash
# Run local CI simulation
python -m pytest tests/ -v --tb=short
black --check --diff .
isort --check-only --diff . --profile black
mypy app_refactored.py models_refactored.py
```

## 📁 Project Structure

```
📁 online-bookstore-final-assessment/
├── 🔧 Core Application
│   ├── app_refactored.py          # Main Flask application
│   ├── models_refactored.py       # Data models with validation
│   ├── services.py                # Business logic layer
│   └── config.py                  # Configuration management
├── 🧪 Testing
│   ├── tests/                     # Comprehensive test suite
│   │   ├── test_refactored_models.py
│   │   ├── test_refactored_services.py
│   │   └── test_performance.py
│   └── performance_analysis.py    # Performance profiling tools
├── 🐳 Containerization
│   ├── Dockerfile                 # Multi-stage Docker build
│   └── docker-compose.yml         # Multi-service orchestration
├── 🌐 Web Assets
│   ├── static/                    # CSS, images, JavaScript
│   └── templates/                 # HTML templates
├── 🔄 CI/CD
│   └── .github/workflows/         # GitHub Actions workflows
└── 📝 Configuration
    ├── requirements.txt           # Python dependencies
    ├── pyproject.toml            # Black/isort configuration
    ├── mypy.ini                  # Type checking configuration
    └── .gitignore                # Git ignore rules
```

## 🔧 Configuration

### Environment Variables
The application uses centralized configuration through `config.py`:

- **Database Configuration**: Connection settings and options
- **Security Settings**: Secret keys, password requirements, session timeout
- **Payment Configuration**: Gateway settings and validation rules
- **Email Configuration**: SMTP settings for notifications

### Demo User
For testing purposes, a demo user is automatically created:
- **Email**: `demo@bookstore.com`
- **Password**: `demo1234`

## 📚 API Documentation

### Main Endpoints
- `GET /` - Home page with book catalog
- `GET /cart` - Shopping cart view
- `POST /add_to_cart` - Add item to cart
- `POST /update_cart` - Update cart item quantity
- `GET /checkout` - Checkout page
- `POST /process_order` - Process order and payment
- `GET /login` - User login page
- `POST /login` - Authenticate user
- `GET /register` - User registration page
- `POST /register` - Create new user account

## 🛡️ Security Features

- **Password Hashing**: bcrypt with configurable rounds
- **Input Validation**: Comprehensive validation for all user inputs
- **SQL Injection Protection**: Parameterized queries and validation
- **XSS Protection**: Input sanitization and template escaping
- **CSRF Protection**: Flask-WTF integration
- **Session Management**: Secure session handling with timeout

## 📈 Performance Metrics

### Benchmarks
- **Book Catalog Loading**: < 0.05s average
- **Search Operations**: < 0.05s average
- **User Authentication**: < 10s for password verification
- **Cart Operations**: < 0.5s average
- **Order Processing**: < 0.5s average

### Optimization Techniques
- Service layer caching
- Efficient database queries
- Optimized password hashing
- Responsive UI components

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `python -m pytest tests/ -v`
5. Check code quality: `black . && isort .`
6. Commit your changes: `git commit -m "Add feature"`
7. Push to the branch: `git push origin feature-name`
8. Submit a pull request

### Code Standards
- **Python**: Follow PEP 8 style guidelines
- **Type Hints**: Use type annotations for all functions
- **Testing**: Maintain 100% test coverage
- **Documentation**: Document all public methods and classes

## 📝 License

This project is part of a final assessment for software testing and quality assurance.

## 🎯 Assignment Requirements Fulfilled

### ✅ Test Code with Automation
- **Comprehensive Test Coverage**: 111 tests covering all functionality
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Performance Tests**: Using `timeit` and `cProfile`
- **Edge Case Testing**: Error conditions and boundary testing

### ✅ CI/CD Pipeline
- **GitHub Actions**: Automated testing and deployment
- **Multi-stage Pipeline**: Test → Security → Quality → Deploy
- **Code Quality Gates**: Automated formatting and linting checks
- **Security Scanning**: Vulnerability detection and reporting

### ✅ Code Efficiency Improvements
- **Service Layer Architecture**: Separated business logic
- **Performance Optimization**: Caching and efficient queries
- **Type Safety**: Comprehensive type hints
- **Configuration Management**: Centralized settings

### ✅ Performance Analysis
- **timeit Integration**: Micro-benchmarking of critical operations
- **cProfile Integration**: Detailed performance profiling
- **Optimization Metrics**: Before/after performance comparisons
- **Threshold Monitoring**: Automated performance regression detection

## 🏆 Achievements

- **100% Test Coverage** with 111 comprehensive tests
- **Production-Ready CI/CD** pipeline with automated quality gates
- **Performance Optimized** with sub-second response times
- **Security Hardened** with comprehensive input validation
- **Docker Ready** with multi-stage containerization
- **Clean Architecture** with separated concerns and maintainable code

---

**Built with ❤️ for Software Testing Excellence**

For questions or support, please open an issue in the repository.
