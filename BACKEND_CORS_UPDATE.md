# Backend CORS Update Instructions

## ⚠️ IMPORTANT: Update CORS After Vercel Deployment

Once you have your Vercel deployment URL, you **MUST** update the backend CORS settings to allow requests from your Vercel domain.

---

## Steps to Update CORS:

### 1. Get Your Vercel Deployment URL
After deploying to Vercel, you'll get a URL like:
- `https://your-project.vercel.app`
- Or your custom domain: `https://yourdomain.com`

### 2. Update Backend CORS Configuration

Edit `/app/backend/server.py` and update the CORS middleware:

**Current Configuration (allows all origins):**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Recommended Production Configuration:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-project.vercel.app",  # Replace with your actual Vercel URL
        "https://mortgage-preapp.preview.emergentagent.com",  # Keep Emergent preview
        "http://localhost:3000",  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Restart Backend Service
```bash
sudo supervisorctl restart backend
```

---

## Why This Matters

- **Security:** Restricting CORS to specific domains prevents unauthorized access
- **Production Best Practice:** `allow_origins=["*"]` should only be used in development
- **Authentication:** Supabase JWT tokens require `allow_credentials=True` with specific origins

---

## Alternative: Environment Variable Approach

For better flexibility, you can use environment variables:

**In `/app/backend/.env`:**
```env
ALLOWED_ORIGINS=https://your-project.vercel.app,https://mortgage-preapp.preview.emergentagent.com,http://localhost:3000
```

**In `/app/backend/server.py`:**
```python
import os

allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Testing CORS

After updating, test from your Vercel deployment:
1. Open browser console (F12)
2. Try logging in
3. Look for CORS errors
4. If you see errors, verify the origin URL matches exactly (including https://)

---

## Note

The current configuration with `allow_origins=["*"]` will work for testing, but should be restricted for production security.
