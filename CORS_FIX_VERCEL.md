# CORS Error Fix - Vercel Deployment

## 🔴 Problem Identified

**Error:** "Access to XMLHttpRequest at 'https://mortgage-preapp.preview.emergentagent.com/api/calculate' from origin 'https://pre-qualification-app-yq1a-6mq1m82ra-marc-alleynes-projects.vercel.app' has been blocked by CORS policy"

**Root Cause:** When using `allow_credentials=True` in FastAPI CORS middleware, you **cannot** use a wildcard (`"*"`) for `allow_origins`. You must explicitly list allowed domains.

---

## ✅ Solution Applied

Updated `/app/backend/server.py` CORS configuration to explicitly include your Vercel domain:

### Before:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ This doesn't work with allow_credentials=True
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### After:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pre-qualification-app-yq1a-6mq1m82ra-marc-alleynes-projects.vercel.app",
        "https://mortgage-preapp.preview.emergentagent.com",
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🔧 What This Fixes

✅ Allows your Vercel frontend to make API calls to the backend  
✅ Enables Supabase JWT authentication to work across domains  
✅ Permits credentials (cookies, authorization headers) in cross-origin requests  
✅ Maintains security by explicitly listing allowed origins

---

## 📝 Adding More Domains (Custom Domains, Production URLs)

When you add a custom domain or get a new Vercel URL, you'll need to add it to the CORS list:

### Step 1: Edit `/app/backend/server.py`
Add your new domain to the `allow_origins` list:

```python
allow_origins=[
    "https://your-custom-domain.com",  # Add your custom domain
    "https://pre-qualification-app-yq1a-6mq1m82ra-marc-alleynes-projects.vercel.app",
    "https://mortgage-preapp.preview.emergentagent.com",
    "http://localhost:3000",
    "http://localhost:3001",
],
```

### Step 2: Restart Backend
```bash
sudo supervisorctl restart backend
```

---

## 🌐 Alternative: Environment Variable Approach (Recommended for Production)

For better flexibility, you can use environment variables:

### In `/app/backend/.env`:
```env
ALLOWED_ORIGINS=https://your-custom-domain.com,https://pre-qualification-app-yq1a-6mq1m82ra-marc-alleynes-projects.vercel.app,https://mortgage-preapp.preview.emergentagent.com
```

### In `/app/backend/server.py`:
```python
import os

# Get allowed origins from environment variable
allowed_origins_str = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:3001"
)
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Benefits:**
- ✅ No code changes needed when adding new domains
- ✅ Different configurations for dev/staging/production
- ✅ Easier to manage in CI/CD pipelines

---

## 🧪 Testing

To verify CORS is working:

1. **Open your Vercel app:** https://pre-qualification-app-yq1a-6mq1m82ra-marc-alleynes-projects.vercel.app
2. **Log in** with your Supabase credentials
3. **Try to generate a certificate**
4. **Check browser console (F12)** - there should be no CORS errors

---

## 🔍 Why This Happens

### The CORS + Credentials Rule:
When a request includes credentials (cookies, authorization headers, etc.):
- ✅ **Allowed:** Specific origins like `"https://example.com"`
- ❌ **Not Allowed:** Wildcard `"*"`

This is a security feature to prevent credential leaking to untrusted origins.

### Your App Uses:
- **Supabase JWT tokens** (sent in Authorization header)
- **`allow_credentials=True`** (required for JWT authentication)
- **Therefore:** Must explicitly list allowed origins

---

## 📋 Quick Checklist

When deploying to a new domain:
- [ ] Add the domain to `allow_origins` list in `server.py`
- [ ] Restart backend: `sudo supervisorctl restart backend`
- [ ] Update Vercel environment variable `REACT_APP_BACKEND_URL` if backend changes
- [ ] Test login and API calls from new domain
- [ ] Check browser console for CORS errors

---

## 🎯 Current Working Configuration

**Backend CORS allows:**
- ✅ https://pre-qualification-app-yq1a-6mq1m82ra-marc-alleynes-projects.vercel.app (Vercel)
- ✅ https://mortgage-preapp.preview.emergentagent.com (Emergent Preview)
- ✅ http://localhost:3000 (Local development)
- ✅ http://localhost:3001 (Local development alt port)

**Status:** ✅ Fixed and backend restarted

---

Your Vercel app should now work correctly! Try making a calculation again. 🎉
