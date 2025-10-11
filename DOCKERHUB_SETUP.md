# 🐳 DockerHub Repository Setup

## ✅ Issues Fixed

1. **Dockerfile Casing** ✅
   - Changed all `FROM ... as` to `FROM ... AS` (uppercase)
   - Fixed lines 3, 27, 87, 119

2. **Docker Image Name** ✅
   - Changed from `bookstore/online-bookstore`
   - Changed to `baffoe6/online-bookstore`
   - Updated in both workflow files

---

## 📋 Create DockerHub Repository

You need to create the repository on DockerHub before the workflows can push images.

### **Step 1: Log in to DockerHub**

Go to: https://hub.docker.com/

Log in with:
- Username: `baffoe6`
- Password: (your DockerHub password)

---

### **Step 2: Create Repository**

1. Click **"Create Repository"** button (top right)

2. Fill in the details:
   ```
   Name:        online-bookstore
   Description: Online Bookstore Flask Application with CI/CD
   Visibility:  Public (or Private if you prefer)
   ```

3. Click **"Create"** button

---

### **Step 3: Verify Repository**

After creation, you should see:
```
Repository: baffoe6/online-bookstore
Status: Ready
URL: https://hub.docker.com/r/baffoe6/online-bookstore
```

---

## ✅ What Will Happen After Setup

Once the repository is created:

1. **Workflows will push images:**
   ```
   baffoe6/online-bookstore:20251011-43acd83  (tagged with date-commit)
   baffoe6/online-bookstore:latest             (latest tag)
   baffoe6/online-bookstore:main               (branch tag)
   ```

2. **Docker build will succeed:**
   ```
   ✅ Dockerfile linting: No warnings (casing fixed)
   ✅ Docker login: Authenticated
   ✅ Docker build: Image built
   ✅ Docker push: Image pushed to baffoe6/online-bookstore
   ```

---

## 🔄 Alternative: Use GitHub Container Registry

If you prefer not to create a DockerHub repository, you can use GitHub Container Registry instead:

### Update workflows to use GHCR:

In `.github/workflows/continuous-deployment.yml`:
```yaml
env:
  DOCKER_IMAGE: ghcr.io/baffoe6/online-bookstore  # Use GHCR
  PYTHON_VERSION: '3.11'
```

In `.github/workflows/6-deploy.yml`:
```yaml
- name: Log in to GitHub Container Registry
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

**Benefit:** No need to create repository, GitHub automatically creates it on first push.

---

## 📊 Current Configuration

After these fixes:

```
Dockerfile:
├─ Stage 1: FROM python:3.12-slim AS builder      ✅ (fixed casing)
├─ Stage 2: FROM python:3.12-slim AS production   ✅ (fixed casing)
├─ Stage 3: FROM production AS development        ✅ (fixed casing)
└─ Stage 4: FROM development AS testing           ✅ (fixed casing)

Workflows:
├─ continuous-deployment.yml: baffoe6/online-bookstore  ✅
└─ 6-deploy.yml: baffoe6/online-bookstore               ✅

Docker Secrets (Required):
├─ DOCKER_USERNAME: baffoe6                       ✅ (must be set)
└─ DOCKER_PASSWORD: dckr_pat_X5Vq-ig3hQ4EhCZ...   ✅ (must be set)
```

---

## 🚀 After Creating Repository

1. **Verify secrets are set:**
   - https://github.com/Baffoe6/online_bookstore_final_assessment_Baffoe_L_K_2416509/settings/secrets/actions
   - Must see: `DOCKER_USERNAME` and `DOCKER_PASSWORD`

2. **Push the fixes:**
   - These fixes are committed and will be pushed next

3. **Re-run workflows:**
   - Go to Actions tab
   - Click "Re-run all jobs"
   - Docker push will now succeed!

---

## ✅ Expected Results

```
╔════════════════════════════════════════════════════════════╗
║  Docker Build & Push: SUCCESS                              ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  ✅ Dockerfile linting: PASSED (no warnings)              ║
║  ✅ Docker login: Authenticated                           ║
║  ✅ Docker build: Image built successfully                ║
║  ✅ Docker push: Pushed to baffoe6/online-bookstore       ║
║                                                            ║
║  Image tags created:                                       ║
║  • baffoe6/online-bookstore:latest                        ║
║  • baffoe6/online-bookstore:main                          ║
║  • baffoe6/online-bookstore:20251011-xxxxxxx              ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

---

**Summary:**
1. Create repository: `baffoe6/online-bookstore` on DockerHub ✅
2. Verify Docker secrets are set correctly ✅
3. Push these fixes and re-run workflows ✅
4. Docker build and push will succeed! 🎉

