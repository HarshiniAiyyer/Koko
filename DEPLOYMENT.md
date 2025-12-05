# Deployment Guide: Vercel (Frontend) + Render (Backend)

This guide walks you through deploying KOKO to production using Vercel for the frontend and Render for the backend.

---

## Prerequisites

- GitHub account
- Vercel account ([Sign up](https://vercel.com/signup))
- Render account ([Sign up](https://render.com/register))
- Groq API key
- HuggingFace API token (optional)

---

## Part 1: Prepare Your Repository

### 1. Initialize Git Repository (if not already done)

```bash
cd d:\koko
git init
git add .
git commit -m "Initial commit: KOKO - The Personality Engine"
```

### 2. Push to GitHub

Create a new repository on GitHub, then:

```bash
git remote add origin https://github.com/YOUR_USERNAME/koko.git
git branch -M main
git push -u origin main
```

---

## Part 2: Deploy Backend to Render

### 1. Create New Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your `koko` repository

### 2. Configure Service

**Basic Settings:**
- **Name**: `koko-backend`
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 3. Set Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**:

| Key | Value |
|-----|-------|
| `GROQ_API_KEY` | `your_groq_api_key_here` |
| `HF_API_TOKEN` | `your_huggingface_token` |
| `LLM_MODEL` | `llama3-8b-8192` |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` |
| `PYTHON_VERSION` | `3.10.0` |

### 4. Deploy

Click **"Create Web Service"**

Render will:
1. Clone your repository
2. Install dependencies
3. Start the FastAPI server
4. Provide a URL like: `https://koko-backend.onrender.com`

**⚠️ Note**: Free tier sleeps after 15 minutes of inactivity (first request will be slow)

### 5. Verify Backend

Visit: `https://koko-backend.onrender.com/health`

Should return:
```json
{
  "status": "healthy",
  "service": "AI Companion API"
}
```

---

## Part 3: Deploy Frontend to Vercel

### 1. Update Frontend API URL

Edit `frontend/vite.config.js`:

```javascript
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "./src"),
        },
    },
    server: {
        proxy: {
            '/api': {
                target: process.env.VITE_API_URL || 'http://127.0.0.1:8000',
                changeOrigin: true,
            },
        },
    },
    // Add for production builds
    define: {
        'process.env.VITE_API_URL': JSON.stringify(process.env.VITE_API_URL || 'http://127.0.0.1:8000')
    }
})
```

### 2. Update Frontend to Use Environment Variable

Edit `frontend/src/App.jsx` (find the axios baseURL):

```javascript
// Add at the top of the file
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Update axios calls to use API_BASE_URL
// Example:
const response = await axios.post(`${API_BASE_URL}/api/chat`, {
    message: inputText,
    requested_persona: selectedTone
});
```

### 3. Commit Changes

```bash
git add .
git commit -m "Configure for production deployment"
git push origin main
```

### 4. Deploy to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Import your `koko` repository
4. Configure project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 5. Set Environment Variables

In Vercel project settings → **"Environment Variables"**:

| Name | Value |
|------|-------|
| `VITE_API_URL` | `https://koko-backend.onrender.com` |

### 6. Deploy

Click **"Deploy"**

Vercel will:
1. Build your React app
2. Deploy to CDN
3. Provide a URL like: `https://koko-xyz123.vercel.app`

---

## Part 4: Configure CORS for Production

Update `backend/app/main.py` to allow your Vercel domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local development
        "https://koko-xyz123.vercel.app",  # Your Vercel URL
        "https://*.vercel.app",  # All Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Commit and push:

```bash
git add backend/app/main.py
git commit -m "Update CORS for production"
git push origin main
```

Render will auto-deploy the update.

---

## Part 5: Testing Your Deployment

1. **Visit your Vercel URL**: `https://koko-xyz123.vercel.app`
2. **Test a conversation**:
   - Type a message
   - Click "DEAL CARDS"
   - Verify response appears
   - Check sidebar updates

3. **Check for errors**:
   - Open browser console (F12)
   - Look for any API errors
   - Verify network requests succeed

---

## Post-Deployment Configuration

### Custom Domain (Optional)

**Vercel:**
1. Go to project settings → **"Domains"**
2. Add your custom domain
3. Follow DNS configuration instructions

**Render:**
1. Go to service settings → **"Custom Domain"**
2. Add your domain
3. Update DNS records

### Monitoring

**Render:**
- View logs: Dashboard → Your Service → **"Logs"**
- Monitor metrics: **"Metrics"** tab
- Set up alerts: **"Notifications"**

**Vercel:**
- Analytics: Project → **"Analytics"**
- Function logs: **"Functions"** → **"Logs"**

---

## Troubleshooting

### Backend Issues

**Problem**: Service won't start
- Check **"Logs"** in Render dashboard
- Verify all environment variables are set
- Ensure `requirements.txt` is in `backend/` directory

**Problem**: Timeout errors
- Render free tier can be slow on first request (cold start)
- Consider upgrading to paid plan for always-on service

### Frontend Issues

**Problem**: API requests fail
- Verify `VITE_API_URL` is set correctly
- Check CORS configuration in backend
- Ensure backend service is running (visit `/health`)

**Problem**: Build fails
- Check Vercel build logs
- Verify `package.json` scripts are correct
- Ensure `vite.config.js` is properly configured

### Memory Persistence

**⚠️ Important**: Render's free tier uses ephemeral storage. Your `memory.json` will reset when the service restarts.

**Solutions**:
1. Use Render's **Persistent Disk** (paid feature)
2. Migrate to a database (PostgreSQL, MongoDB)
3. Use Render Postgres free tier + update memory engine to use database

---

## Cost Breakdown

### Free Tier Limits

**Render (Backend):**
- ✅ 750 hours/month free
- ⚠️ Sleeps after 15 min inactivity
- ⚠️ Ephemeral storage (data resets on restart)

**Vercel (Frontend):**
- ✅ Unlimited hobby projects
- ✅ 100GB bandwidth/month
- ✅ Automatic HTTPS
- ✅ Global CDN

### Paid Upgrades (Optional)

**Render:**
- **Starter ($7/month)**: Always-on, persistent disk
- **Standard ($25/month)**: More resources, faster

**Vercel:**
- **Pro ($20/month)**: Team collaboration, analytics
- Hobby tier is usually sufficient for personal projects

---

## Continuous Deployment

Both platforms support **automatic deployments**:

1. Push to GitHub `main` branch
2. Render rebuilds backend automatically
3. Vercel rebuilds frontend automatically
4. Changes go live in ~2-5 minutes

---

## Security Checklist

- [ ] Remove wildcard CORS origins in production
- [ ] Set specific allowed origins in `main.py`
- [ ] Keep API keys in environment variables (never commit)
- [ ] Enable Vercel's password protection for staging
- [ ] Set up Render IP allowlist if needed
- [ ] Monitor Render logs for suspicious activity

---

## Next Steps

1. ✅ Deploy backend to Render
2. ✅ Deploy frontend to Vercel
3. ⚠️ Consider persistent storage solution
4. 🚀 Share your KOKO app with the world!

---

**Need Help?**
- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- Check service logs for detailed error messages
