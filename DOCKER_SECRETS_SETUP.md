# 🔐 Docker Secrets Setup Guide

## ⚠️ IMPORTANT: Security Notice

**DO NOT commit Docker credentials to your repository!**

Your workflows are already configured to use GitHub Secrets. You just need to add them via the GitHub web interface.

---

## 🔑 Your DockerHub Credentials

```
Username: baffoe6
Token: [YOUR_DOCKER_TOKEN_HERE]
```

**Note:** Use the Docker token you generated from DockerHub (starts with `dckr_pat_`)

---

## 📋 Step-by-Step Instructions

### Step 1: Go to Your Repository Settings

1. Open your repository in a web browser:
   ```
   https://github.com/Baffoe6/online_bookstore_final_assessment_Baffoe_L_K_2416509
   ```

2. Click on **"Settings"** tab (top right)

---

### Step 2: Navigate to Secrets

1. In the left sidebar, find **"Secrets and variables"**
2. Click **"Actions"**
3. You'll see the **"Secrets"** page

---

### Step 3: Add DOCKER_USERNAME Secret

1. Click the **"New repository secret"** button
2. In the **"Name"** field, enter exactly:
   ```
   DOCKER_USERNAME
   ```
3. In the **"Secret"** field, enter:
   ```
   baffoe6
   ```
4. Click **"Add secret"**

---

### Step 4: Add DOCKER_PASSWORD Secret

1. Click the **"New repository secret"** button again
2. In the **"Name"** field, enter exactly:
   ```
   DOCKER_PASSWORD
   ```
3. In the **"Secret"** field, enter your Docker token:
   ```
   [YOUR_DOCKER_TOKEN_HERE]
   ```
   
   **Note:** Paste your actual Docker token (starts with `dckr_pat_`)
4. Click **"Add secret"**

---

## ✅ Verification

After adding both secrets, you should see:

```
Repository secrets
├── DOCKER_USERNAME    (created just now)
└── DOCKER_PASSWORD    (created just now)
```

**Note:** You won't be able to view the secret values again after saving them (for security), but you can update them if needed.

---

## 🔄 What Happens Next

Once you add these secrets:

1. **Workflows will automatically use them**
   - No code changes needed!
   - Workflows already reference `${{ secrets.DOCKER_USERNAME }}` and `${{ secrets.DOCKER_PASSWORD }}`

2. **Docker login will succeed**
   - The login step in your deployment workflows will authenticate
   - Images can be pushed to DockerHub

3. **Workflows will re-run**
   - You can manually re-run failed workflows
   - Or push a new commit to trigger them

---

## 📍 Where Secrets Are Used

### In `.github/workflows/6-deploy.yml`:
```yaml
- name: Log in to Docker Hub
  if: github.event_name != 'pull_request'
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKER_USERNAME }}  ← Uses your secret
    password: ${{ secrets.DOCKER_PASSWORD }}  ← Uses your secret
```

### In `.github/workflows/continuous-deployment.yml`:
```yaml
- name: Log in to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKER_USERNAME }}  ← Uses your secret
    password: ${{ secrets.DOCKER_PASSWORD }}  ← Uses your secret
```

---

## 🎯 Quick Reference

| Secret Name | Value | Purpose |
|-------------|-------|---------|
| `DOCKER_USERNAME` | `baffoe6` | Your DockerHub username |
| `DOCKER_PASSWORD` | `[YOUR_DOCKER_TOKEN]` | Your DockerHub access token (starts with `dckr_pat_`) |

---

## 🔒 Security Best Practices

✅ **DO:**
- Store credentials as GitHub Secrets
- Use Docker access tokens (not passwords)
- Rotate tokens periodically
- Use secrets in workflows via `${{ secrets.NAME }}`

❌ **DON'T:**
- Commit credentials to repository files
- Share tokens publicly
- Use your DockerHub password directly (use tokens instead)
- Hardcode credentials in workflow files

---

## 🚀 After Adding Secrets

### Option 1: Re-run Failed Workflows

1. Go to your Actions tab:
   ```
   https://github.com/Baffoe6/online_bookstore_final_assessment_Baffoe_L_K_2416509/actions
   ```

2. Find the failed workflow run
3. Click on it
4. Click **"Re-run all jobs"** button (top right)

### Option 2: Push a New Commit

Any new push to `main` will trigger the workflows automatically.

---

## 📊 Expected Results

After adding secrets and re-running:

```
✅ Workflow: 6. Deploy
   ├── Build & Package         → PASS
   ├── Build Docker Image       → PASS (Docker login successful!)
   │   └── Log in to Docker Hub → ✅ Authenticated
   │   └── Build and push       → ✅ Image pushed to DockerHub
   └── Deploy to Staging        → PASS

✅ Workflow: Continuous Deployment
   ├── Pre-Deployment Checks    → PASS
   ├── Build & Push Docker      → PASS (Docker login successful!)
   │   └── Log in to Docker Hub → ✅ Authenticated
   │   └── Build and push       → ✅ Image pushed
   ├── Deploy to Staging        → PASS
   └── Post-Deploy Verification → PASS
```

---

## 🆘 Troubleshooting

### If workflows still fail after adding secrets:

1. **Verify secret names are EXACT:**
   - `DOCKER_USERNAME` (not `DOCKERHUB_USERNAME`)
   - `DOCKER_PASSWORD` (not `DOCKERHUB_TOKEN` or `DOCKERHUB_PASSWORD`)

2. **Check token validity:**
   - Log in to DockerHub
   - Go to Account Settings → Security → Access Tokens
   - Verify your token is active

3. **Re-run workflows:**
   - Secrets are loaded when workflows start
   - You must re-run after adding secrets

4. **Check workflow logs:**
   - Look for "Log in to Docker Hub" step
   - It should show "Login Succeeded"

---

## 📸 Visual Guide

### Finding Secrets Page:
```
GitHub Repository
└── Settings (top tab)
    └── Secrets and variables (left sidebar)
        └── Actions
            └── Repository secrets
                └── New repository secret (button)
```

### Adding a Secret:
```
New secret form:
┌─────────────────────────────────────┐
│ Name *                              │
│ ┌─────────────────────────────────┐ │
│ │ DOCKER_USERNAME                 │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Secret *                            │
│ ┌─────────────────────────────────┐ │
│ │ baffoe6                         │ │
│ └─────────────────────────────────┘ │
│                                     │
│            [Add secret]             │
└─────────────────────────────────────┘
```

---

## ✅ Checklist

Before re-running workflows, verify:

- [ ] Navigated to repository Settings
- [ ] Opened Secrets and variables → Actions
- [ ] Added `DOCKER_USERNAME` secret with value: `baffoe6`
- [ ] Added `DOCKER_PASSWORD` secret with your Docker token
- [ ] Both secrets visible in "Repository secrets" list
- [ ] Ready to re-run workflows or push new commit

---

## 🎉 Once Complete

After adding secrets and re-running:

```
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║         Docker Authentication Will Work! ✅                   ║
║                                                                ║
║  ✅ Docker login: Authenticated                               ║
║  ✅ Docker build: Image built                                 ║
║  ✅ Docker push: Image pushed to DockerHub                    ║
║  ✅ Deployment: Ready to deploy                               ║
║                                                                ║
║  Your CI/CD pipeline will be fully operational! 🚀           ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

---

**Setup Date:** Saturday, October 11, 2025  
**Repository:** Baffoe6/online_bookstore_final_assessment_Baffoe_L_K_2416509  
**Required Secrets:** 2 (DOCKER_USERNAME, DOCKER_PASSWORD)  
**Security:** ✅ Credentials stored securely as GitHub Secrets

**🔐 Your Docker credentials will be secure and your workflows will authenticate successfully!** 🚀

