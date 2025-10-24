# Vercel Deployment Guide - Pre-Qualification App

## Overview
This guide covers deploying the **React frontend** of the Pre-Qualification App to Vercel. The FastAPI backend will remain hosted on Emergent.

---

## Prerequisites

✅ **Vercel Account** - Sign up at [vercel.com](https://vercel.com)  
✅ **Backend Running** - Ensure your FastAPI backend is accessible at: `https://mortgage-preapp.preview.emergentagent.com`  
✅ **Supabase Active** - Your Supabase project should be running

---

## Deployment Steps

### 1. **Connect Your Repository to Vercel**

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New Project"**
3. Import your Git repository (GitHub/GitLab/Bitbucket)
   - OR use Vercel CLI: `vercel deploy`

---

### 2. **Configure Project Settings**

#### **Framework Preset:**
```
Create React App
```
*(Vercel should auto-detect this)*

---

#### **Root Directory:**
```
frontend
```
⚠️ **IMPORTANT:** Click "Edit" next to Root Directory and set it to `frontend`

---

#### **Build & Output Settings:**

| Setting | Value |
|---------|-------|
| **Build Command** | `yarn build` |
| **Output Directory** | `build` |
| **Install Command** | `yarn install` |
| **Development Command** | `yarn start` |

---

### 3. **Environment Variables**

Add these in Vercel Dashboard → Project Settings → Environment Variables:

| Variable Name | Value | Notes |
|--------------|-------|-------|
| `REACT_APP_BACKEND_URL` | `https://mortgage-preapp.preview.emergentagent.com` | Your backend API URL |
| `REACT_APP_SUPABASE_URL` | `https://hihltoviggrktrcnomyx.supabase.co` | Your Supabase project URL |
| `REACT_APP_SUPABASE_ANON_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` | Your Supabase anon key |

#### **How to Add Environment Variables:**
1. In Vercel Dashboard → Select your project
2. Go to **Settings** → **Environment Variables**
3. Add each variable for **Production**, **Preview**, and **Development** environments
4. Click **Save**

---

### 4. **Deploy**

Once configured, click **"Deploy"**

Vercel will:
1. Clone your repository
2. Install dependencies (`yarn install`)
3. Build the React app (`yarn build`)
4. Deploy to a CDN with automatic HTTPS

---

## Post-Deployment

### **Access Your App:**
- Production URL: `https://your-project.vercel.app`
- Custom Domain: Configure in Vercel Settings → Domains

### **Verify Deployment:**
1. Open your Vercel URL
2. Try logging in with Supabase credentials
3. Test the calculator functionality
4. Check browser console for any errors

---

## Important Notes

### ⚠️ **Backend Must Remain Running**
- The FastAPI backend is NOT deployed to Vercel (Vercel is for static/frontend/serverless only)
- Backend must stay on Emergent or be deployed to:
  - **Render** (recommended for Python)
  - **Railway**
  - **Fly.io**
  - **AWS/Google Cloud**

### ⚠️ **CORS Configuration**
Ensure your backend (`server.py`) allows requests from your Vercel domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-project.vercel.app",
        "https://mortgage-preapp.preview.emergentagent.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### ⚠️ **setupProxy.js**
- The `setupProxy.js` file is ignored in production builds
- It only affects local development
- No need to remove it

---

## Troubleshooting

### **Issue: API calls failing**
✅ **Solution:** Check that `REACT_APP_BACKEND_URL` is correctly set in Vercel environment variables

### **Issue: Authentication not working**
✅ **Solution:** Verify Supabase environment variables are correct

### **Issue: Build failing**
✅ **Solution:** 
1. Check build logs in Vercel dashboard
2. Ensure `yarn build` works locally: `cd frontend && yarn build`
3. Check that all dependencies are in `package.json`

### **Issue: Blank page after deployment**
✅ **Solution:** 
1. Check browser console for errors
2. Verify root directory is set to `frontend`
3. Ensure output directory is `build`

---

## Alternative: Vercel CLI Deployment

If you prefer command line:

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to project root
cd /app

# Deploy
vercel

# Follow prompts:
# - Set root directory to: frontend
# - Override build command: yarn build
# - Override output directory: build
```

---

## Summary

✅ Root Directory: `frontend`  
✅ Build Command: `yarn build`  
✅ Output Directory: `build`  
✅ Install Command: `yarn install`  
✅ Environment Variables: Set all three REACT_APP_* variables  
✅ Backend: Stays on Emergent (not deployed to Vercel)

---

## Need Help?

- **Vercel Docs:** https://vercel.com/docs
- **React Deployment:** https://create-react-app.dev/docs/deployment/
- **Supabase + Vercel:** https://supabase.com/docs/guides/getting-started/tutorials/with-vercel

