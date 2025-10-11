# 🔧 CI/CD Setup & Configuration Guide

## Complete Setup Instructions for 6 Workflows

---

## 📋 Prerequisites

```
╔════════════════════════════════════════════════════════════╗
║                    PREREQUISITES                           ║
╠════════════════════════════════════════════════════════════╣
║                                                             ║
║  ✅ GitHub repository with Actions enabled                 ║
║  ✅ Docker Hub account (for deployment)                    ║
║  ✅ Repository admin access                                ║
║  ✅ Staging/Production servers (optional)                  ║
║                                                             ║
╚════════════════════════════════════════════════════════════╝
```

---

## 🚀 Step-by-Step Setup

### Step 1: Repository Setup (5 minutes)

```bash
# 1. Clone your repository
git clone https://github.com/your-username/online_bookstore.git
cd online_bookstore

# 2. Verify workflow files exist
ls -la .github/workflows/
# Should see: 8 .yml files

# 3. Verify test files exist
ls -la tests/
# Should see: 4 test files + conftest.py

# 4. Verify requirements files
cat requirements.txt
cat requirements-test.txt
```

---

### Step 2: GitHub Secrets Configuration (10 minutes)

Navigate to: **Settings → Secrets and variables → Actions**

#### Required Secrets

```yaml
# Docker Hub credentials (for deployment)
Name: DOCKER_USERNAME
Value: your-dockerhub-username

Name: DOCKER_PASSWORD
Value: your-dockerhub-password-or-token
```

#### Optional Secrets

```yaml
# Codecov (for private repos)
Name: CODECOV_TOKEN
Value: get-from-codecov.io

# SSH Deployment (if using SSH)
Name: SSH_PRIVATE_KEY
Value: your-ssh-private-key

Name: DEPLOY_HOST
Value: your-server-hostname

Name: DEPLOY_USER
Value: deployment-user

# Slack/Discord notifications (optional)
Name: SLACK_WEBHOOK_URL
Value: your-slack-webhook

Name: DISCORD_WEBHOOK_URL
Value: your-discord-webhook
```

**How to create Docker Hub token:**
```
1. Visit hub.docker.com
2. Account Settings → Security → New Access Token
3. Description: "GitHub Actions"
4. Access permissions: Read, Write, Delete
5. Generate and copy token
```

---

### Step 3: Environment Configuration (10 minutes)

Navigate to: **Settings → Environments**

#### Create Staging Environment

```yaml
Name: staging

Protection Rules:
  - No protection rules
  
Environment secrets (optional):
  - STAGING_URL: https://staging.bookstore.example.com
  - STAGING_API_KEY: your-staging-api-key

Deployment branches:
  - Selected branches
  - develop, main
```

#### Create Production Environment

```yaml
Name: production

Protection Rules:
  ✅ Required reviewers: 1 (or more)
  ✅ Wait timer: 5 minutes
  ✅ Deployment branches: main, tags

Environment secrets (optional):
  - PRODUCTION_URL: https://bookstore.example.com
  - PRODUCTION_API_KEY: your-production-api-key
  - NEW_RELIC_KEY: monitoring-key
```

---

### Step 4: Branch Protection Rules (10 minutes)

Navigate to: **Settings → Branches → Add rule**

#### Main Branch Protection

```yaml
Branch name pattern: main

Branch protection rules:

1. Protect matching branches:
   ✅ Require a pull request before merging
      - Required approvals: 1
      - Dismiss stale reviews: Yes
      - Require review from Code Owners: No
      - Restrict who can dismiss: No
   
   ✅ Require status checks to pass before merging
      - Require branches to be up to date: Yes
      - Status checks required:
        □ Test Suite (156 Tests) / test
        □ Coverage Analysis / coverage
        □ Code Quality - Linting & Type Checking / lint
        □ Security Vulnerability Scan / security-scan
        □ Performance Testing / performance (optional)
   
   ✅ Require conversation resolution before merging
   
   ✅ Do not allow bypassing the above settings
   
   ❌ Allow force pushes: No
   ❌ Allow deletions: No
```

#### Develop Branch Protection (Optional)

```yaml
Branch name pattern: develop

Simplified rules:
✅ Require pull request
✅ Require status checks (Tests only)
```

---

### Step 5: Actions Permissions (5 minutes)

Navigate to: **Settings → Actions → General**

```yaml
Actions permissions:
  ✅ Allow all actions and reusable workflows

Workflow permissions:
  ✅ Read and write permissions
  ✅ Allow GitHub Actions to create and approve pull requests

Fork pull request workflows:
  ✅ Require approval for first-time contributors
```

---

### Step 6: Enable CodeQL (5 minutes)

Navigate to: **Security → Code scanning → Set up**

```yaml
1. Click "Set up" for CodeQL
2. Use workflow: .github/workflows/5-security.yml (already has CodeQL)
3. CodeQL will scan on:
   - Push to main/develop
   - Pull requests
   - Weekly schedule
```

---

### Step 7: Setup Codecov (Optional - 10 minutes)

For private repositories:

```bash
# 1. Visit codecov.io
# 2. Sign in with GitHub
# 3. Add repository
# 4. Copy token
# 5. Add to GitHub Secrets as CODECOV_TOKEN
```

For public repositories:
- Codecov works automatically without token

---

### Step 8: Verify Setup (10 minutes)

```bash
# 1. Create test branch
git checkout -b test/ci-cd-verification
git commit --allow-empty -m "Test: Verify CI/CD workflows"
git push origin test/ci-cd-verification

# 2. Create Pull Request
gh pr create --title "Test CI/CD" --body "Testing all workflows"

# 3. Observe workflows in Actions tab
# You should see:
#   - Test Suite (156 Tests) - Running
#   - Coverage Analysis - Running
#   - Performance Testing - Running
#   - Code Quality - Running  
#   - Security Scanning - Running
#   - Continuous Integration - Running

# 4. Wait for completion (~15-20 minutes)

# 5. Check PR for:
#   - All status checks ✅
#   - Coverage comment
#   - Performance comment
#   - No security issues

# 6. Close test PR
gh pr close test/ci-cd-verification --delete-branch
```

---

## 🔧 Configuration Files

### Required Files in Repository

```
Repository Root:
├── .github/workflows/          # GitHub Actions workflows
│   ├── 1-tests.yml
│   ├── 2-coverage.yml
│   ├── 3-performance.yml
│   ├── 4-code-quality.yml
│   ├── 5-security.yml
│   ├── 6-deploy.yml
│   ├── continuous-integration.yml
│   └── continuous-deployment.yml
│
├── tests/                      # Test suite
│   ├── test_models.py
│   ├── test_services.py
│   ├── test_app.py
│   ├── test_config.py
│   └── conftest.py
│
├── performance_tests.py        # Performance benchmarks
├── requirements.txt            # Application dependencies
├── requirements-test.txt       # Test dependencies
├── pytest.ini                  # Pytest configuration
├── mypy.ini                    # MyPy configuration
├── .pylintrc                   # Pylint configuration
├── Dockerfile                  # Docker configuration
└── docker-compose.yml          # Docker Compose config
```

---

## 📊 Monitoring & Alerts

### GitHub Actions Dashboard

```
Actions Tab → Workflows

View:
├─ All workflows
├─ Workflow runs (history)
├─ Run details
├─ Job logs
├─ Artifacts
└─ Metrics

Filters:
├─ By workflow
├─ By event
├─ By status
└─ By branch
```

### Status Check Monitoring

```
Pull Request → Checks Tab

View:
├─ Required checks
├─ Optional checks
├─ Check details
├─ Re-run failed checks
└─ Summary of all workflows
```

### Security Monitoring

```
Security Tab → Code scanning alerts

View:
├─ CodeQL alerts
├─ Dependency alerts
├─ Secret scanning
└─ Security advisories
```

---

## 🎯 Troubleshooting

### Common Issues

#### Issue 1: Workflow not triggering

```yaml
# Check trigger configuration
on:
  push:
    branches: [ main ]  # ← Check branch name matches

# Verify:
git branch --show-current  # Current branch
git remote -v              # Remote configuration
```

#### Issue 2: Test failures

```bash
# Run tests locally first
pytest tests/ -v

# Check logs in GitHub Actions
# Actions → Select workflow → View logs

# Common fixes:
pip install -r requirements-test.txt
pytest --collect-only  # Verify test discovery
```

#### Issue 3: Docker build fails

```bash
# Test Docker build locally
docker build -t test-image .
docker run --rm test-image python -c "import app_refactored; print('OK')"

# Check Dockerfile syntax
# Verify requirements.txt
```

#### Issue 4: Secrets not working

```bash
# Verify secret names match exactly
# Case-sensitive: DOCKER_USERNAME ≠ docker_username

# Test secret access
# In workflow: echo "Secret configured: ${{ secrets.DOCKER_USERNAME != '' }}"
```

#### Issue 5: Deploy permission denied

```bash
# Check environment protection rules
# Ensure user is approved reviewer

# Verify deployment credentials
# Test SSH/Docker access manually
```

---

## 📈 Best Practices

### 1. Workflow Design

```yaml
✅ DO:
- Use clear, descriptive names
- Separate concerns (one workflow per purpose)
- Use matrix strategy for parallel execution
- Cache dependencies
- Upload artifacts for debugging

❌ DON'T:
- Put everything in one workflow
- Run unnecessary steps on every push
- Forget to clean up artifacts
- Hardcode secrets in workflows
```

### 2. Performance Optimization

```yaml
✅ DO:
- Cache pip dependencies
- Cache Docker layers
- Use conditional execution
- Parallelize independent jobs
- Use appropriate runner sizes

❌ DON'T:
- Install deps every time (use cache)
- Run all workflows on docs changes
- Use expensive operations without need
- Forget about Actions minute limits
```

### 3. Security

```yaml
✅ DO:
- Use GitHub Secrets for sensitive data
- Review dependency vulnerabilities weekly
- Enable CodeQL scanning
- Use environment protection for production
- Implement automatic rollback

❌ DON'T:
- Commit secrets to repository
- Skip security scans
- Deploy without smoke tests
- Allow public access to deployment logs
```

---

## 🎯 Workflow Customization

### Adding Slack Notifications

```yaml
# Add to any workflow
- name: Notify Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}
    text: 'Workflow ${{ github.workflow }} completed'
```

### Adding Email Notifications

```yaml
# Add to workflow
- name: Send email
  if: failure()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: 'CI/CD Failure: ${{ github.workflow }}'
    body: 'Workflow failed on ${{ github.ref }}'
    to: team@example.com
```

### Adding Custom Smoke Tests

```yaml
# In deploy workflow
- name: Custom smoke tests
  run: |
    # Wait for app to start
    sleep 10
    
    # Test endpoints
    curl -f https://staging.bookstore.example.com/ || exit 1
    curl -f https://staging.bookstore.example.com/api/books || exit 1
    
    # Test critical functionality
    pytest tests/smoke/ --url=https://staging.bookstore.example.com
```

---

## 🎉 Setup Complete!

```
╔════════════════════════════════════════════════════════════════════╗
║                     CI/CD SETUP CHECKLIST                           ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  ✅ Workflow files created (8 files)                               ║
║  ✅ GitHub Secrets configured                                      ║
║  ✅ Environments created (staging, production)                     ║
║  ✅ Branch protection enabled                                      ║
║  ✅ Actions permissions set                                        ║
║  ✅ CodeQL enabled                                                 ║
║  ✅ Codecov configured (optional)                                  ║
║  ✅ Setup verified                                                 ║
║                                                                     ║
║  Status: READY FOR PRODUCTION ⭐⭐⭐⭐⭐                           ║
║                                                                     ║
╚════════════════════════════════════════════════════════════════════╝
```

---

**Setup Guide**: Complete  
**Total Setup Time**: ~60 minutes  
**Status**: Production-ready

**🎉 CI/CD pipeline configured and ready to use!** 🚀

