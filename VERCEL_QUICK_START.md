# Quick Reference: Vercel Deployment Configuration

## What to Enter in Vercel Deployment Screen:

### 🎯 Framework Preset
```
Create React App
```
(or let Vercel auto-detect)

---

### 📁 Root Directory
```
frontend
```
⚠️ **Click "Edit" and type:** `frontend`

---

### ⚙️ Build and Output Settings

**Build Command:**
```bash
yarn build
```

**Output Directory:**
```bash
build
```

**Install Command:**
```bash
yarn install
```

---

### 🔐 Environment Variables

Click "Add More" for each variable:

#### Variable 1:
- **Key:** `REACT_APP_BACKEND_URL`
- **Value:** `https://mortgage-preapp.preview.emergentagent.com`

#### Variable 2:
- **Key:** `REACT_APP_SUPABASE_URL`
- **Value:** `https://hihltoviggrktrcnomyx.supabase.co`

#### Variable 3:
- **Key:** `REACT_APP_SUPABASE_ANON_KEY`
- **Value:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhpaGx0b3ZpZ2dya3RyY25vbXl4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyMzEzMjEsImV4cCI6MjA3NjgwNzMyMX0.TGp6jcOEK1-wSx40VP-KF1wo4OUTUtgWnpFzGIm-wnI`

---

## ✅ Quick Checklist

- [ ] Root Directory set to `frontend`
- [ ] Build Command: `yarn build`
- [ ] Output Directory: `build`
- [ ] Install Command: `yarn install`
- [ ] All 3 environment variables added
- [ ] Backend is running on Emergent

---

## 🚀 After Deployment

1. Wait for build to complete
2. Click the deployment URL
3. Test login functionality
4. Test calculator
5. ✅ Done!

---

## ⚠️ Important

- **Backend stays on Emergent** - Only frontend deploys to Vercel
- If you change your backend URL later, update the `REACT_APP_BACKEND_URL` environment variable in Vercel settings
