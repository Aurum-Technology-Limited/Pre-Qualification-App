# 🔧 Fixed Vercel Configuration

## The Issue
Vercel was trying to run `cd frontend` but was already inside the frontend directory, causing a "No such file or directory" error.

## The Fix
Moved `vercel.json` into the `/frontend` directory with corrected commands.

---

## ✅ Updated Configuration for Vercel

Since you've set **Root Directory** to `frontend`, Vercel is already in that folder. Use these settings:

### **Framework Preset**
```
Create React App
```

### **Root Directory**  
```
frontend
```
*(Keep this as you had it)*

### **Build & Output Settings**

**DO NOT override these** - Vercel will auto-detect from `vercel.json`:
- Build Command: `yarn build`
- Output Directory: `build`
- Install Command: `yarn install`

---

## 🔐 Environment Variables (Still Required)

Add these in Vercel Dashboard → Settings → Environment Variables:

1. **Key:** `REACT_APP_BACKEND_URL`  
   **Value:** `https://mortgage-preapp.preview.emergentagent.com`

2. **Key:** `REACT_APP_SUPABASE_URL`  
   **Value:** `https://hihltoviggrktrcnomyx.supabase.co`

3. **Key:** `REACT_APP_SUPABASE_ANON_KEY`  
   **Value:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhpaGx0b3ZpZ2dya3RyY25vbXl4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyMzEzMjEsImV4cCI6MjA3NjgwNzMyMX0.TGp6jcOEK1-wSx40VP-KF1wo4OUTUtgWnpFzGIm-wnI`

---

## 🚀 Deploy Again

1. **Commit and push** your changes (or let Vercel auto-redeploy)
2. Vercel should now build successfully
3. The `vercel.json` inside the frontend folder will be automatically detected

---

## 📋 Quick Checklist

- [x] Removed incorrect root-level vercel.json
- [x] Created correct vercel.json inside frontend/
- [x] Commands no longer try to `cd` into frontend
- [ ] Push changes to GitHub
- [ ] Redeploy on Vercel (or it will auto-deploy)
- [ ] Add environment variables in Vercel dashboard

---

## Alternative: Simplified Approach

If you prefer, you can also:

1. **Remove "Root Directory"** from Vercel settings (leave it blank)
2. **Override Build Command** to: `cd frontend && yarn build`
3. **Override Output Directory** to: `frontend/build`
4. **Override Install Command** to: `cd frontend && yarn install`

Both approaches work! The current fix (with Root Directory = frontend) is cleaner.
