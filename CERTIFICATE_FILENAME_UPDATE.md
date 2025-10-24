# Certificate Filename Update

## Change Made

Updated the certificate download filename format:

**Before:**
```
PreQualification_Certificate_4F37D71F.pdf
```

**After:**
```
Pre-Qualification_Certificate_4F37D71F.pdf
```

## Technical Details

**File Changed:** `/app/backend/server.py`

**Line 482:** Updated filename parameter in FileResponse

```python
# Before
filename=f"PreQualification_Certificate_{certificate_id}.pdf"

# After
filename=f"Pre-Qualification_Certificate_{certificate_id}.pdf"
```

## Format

The certificate files will now download with the format:
```
Pre-Qualification_Certificate_{UNIQUE_ID}.pdf
```

Where `{UNIQUE_ID}` is an 8-character unique identifier (e.g., `4F37D71F`)

## Testing

To verify:
1. Log into the app
2. Generate a pre-qualification certificate
3. Download the PDF
4. Check that the filename is: `Pre-Qualification_Certificate_[ID].pdf`

## Status

✅ Change implemented
✅ Backend restarted
✅ App is running and accessible
