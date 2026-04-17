# 🚀 Vercel Deployment Setup

## ⚠️ CRITICAL: Environment Variables

### What to do in Vercel Dashboard:

1. Go to **Project Settings** → **Environment Variables**

2. Add these variables:

| Variable Name | Value | Scope |
|---|---|---|
| `REACT_APP_BACKEND_URL` | `https://your-production-backend-url.com` | Production, Preview, Development |

**Important:** 
- Replace `https://your-production-backend-url.com` with your actual backend URL
- Must include `https://` protocol
- No trailing slash
- Example: `https://api.cropsense.com` or `https://backend-xyz.herokuapp.com`

### How to find your backend URL:
- If backend is deployed on Vercel, it will be something like: `https://backend-cropsense-xyz.vercel.app`
- If backend is on Heroku: `https://your-app-name.herokuapp.com`
- If backend is on a custom domain: `https://api.yourdomain.com`

## 🔧 Local Testing

Before pushing, test locally:

```bash
# Install dependencies
cd frontend
yarn install

# Create .env.local (takes precedence over .env)
echo "REACT_APP_BACKEND_URL=http://localhost:8001" > .env.local

# Start development server (should connect to backend)
yarn start
```

## ✅ Verification Checklist

After deployment:
- [ ] Open deployed app in browser
- [ ] Try uploading an image
- [ ] Check Network tab in DevTools
- [ ] API calls should go to your backend URL (not `undefined`)
- [ ] You should see classification results

## 🐛 Troubleshooting

### Issue: "Cannot POST /api/classify" or 404 errors
- **Check:** Backend URL in Vercel environment variables
- **Fix:** Make sure `REACT_APP_BACKEND_URL` is correct and production backend is running

### Issue: API calls appear undefined in logs
- **Check:** Environment variable might not be set
- **Fix:** Verify it's set in Vercel dashboard, then redeploy

### Issue: CORS errors
- **Check:** Backend CORS_ORIGINS setting
- **Fix:** Add Vercel domain to backend's CORS_ORIGINS (remove `"*"` and specify exact URL)

### Issue: Build succeeds but app doesn't work
- **Check:** Frontend .env has `REACT_APP_BACKEND_URL` pointing to staging URL
- **Fix:** Update .env with production backend URL or rely on Vercel env vars

## 📋 Backend Requirements

Ensure your backend:
1. Is deployed and running
2. Has these endpoints configured:
   - `POST /api/classify` - Disease classification
   - `POST /api/advisory` - Treatment advisory
   - `POST /api/history` - Save diagnosis
   - `GET /api/history` - Fetch history
3. Has `CORS_ORIGINS` configured to allow Vercel domain
4. Has all API keys set (HF_TOKEN, GROQ_API_KEY, etc.)

---

✨ **Pro Tip:** You can also use Vercel's CLI to set env vars:
```bash
vercel env add REACT_APP_BACKEND_URL
```
