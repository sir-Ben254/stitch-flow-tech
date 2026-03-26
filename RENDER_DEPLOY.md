# Deploy Backend on Render (GitHub)

## Step 1: Push Code to GitHub

1. Create a new repository on GitHub
2. Initialize git in your project:
```bash
git init
git add .
git commit -m "Initial commit"
```
3. Add your GitHub repo and push:
```bash
git remote add origin https://github.com/yourusername/stitchflow.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy Backend on Render

### 2.1 Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub (authorize Render to access your repos)

### 2.2 Create Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub account if not already connected
3. Select your `stitchflow` repository
4. Configure the service:
   | Setting | Value |
   |---------|-------|
   | **Name** | `stitchflow-api` |
   | **Root Directory** | `backend` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

### 2.3 Add Environment Variables
Click **"Advanced"** → **"Add Environment Variables**:

| Key | Value |
|-----|-------|
| `DEBUG` | `false` |
| `SECRET_KEY` | Generate a random secret (use: `openssl rand -base64 32`) |
| `SUPABASE_URL` | Your Supabase URL (e.g., `https://abc123.supabase.co`) |
| `SUPABASE_KEY` | Your Supabase anon key |
| `SUPABASE_SERVICE_KEY` | Your Supabase service_role key |
| `DARAJA_CONSUMER_KEY` | Your Safaricom Daraja consumer key |
| `DARAJA_CONSUMER_SECRET` | Your Safaricom Daraja consumer secret |
| `DARAJA_SHORTCODE` | Your M-Pesa shortcode |
| `DARAJA_PASSKEY` | Your Daraja passkey |
| `DARAJA_CALLBACK_URL` | `https://stitchflow-api.onrender.com/api/payments/callback` |
| `DARAJA_ENVIRONMENT` | `sandbox` (or `production`) |
| `REDIS_URL` | Leave blank (or add Redis if using) |
| `CELERY_BROKER_URL` | Leave blank |
| `CELERY_RESULT_BACKEND` | Leave blank |

### 2.4 Deploy
1. Click **"Create Web Service"**
2. Wait for build to complete (may take 2-5 minutes)
3. Your API will be live at `https://stitchflow-api.onrender.com`

---

## Step 3: Verify Deployment

Test the API:
```bash
curl https://stitchflow-api.onrender.com/
# Should return: {"name":"StitchFlow","version":"1.0.0","status":"running"}

curl https://stitchflow-api.onrender.com/health
# Should return: {"status":"healthy","mode":"LOW","timestamp":...}
```

---

## Troubleshooting

### Build Fails
- Check that `root directory` is set to `backend`
- Ensure `requirements.txt` is in the `backend` folder

### 500 Error on API Calls
- Verify environment variables are set correctly
- Check Supabase credentials are valid

### CORS Errors
- Update `CORS_ORIGINS` env var to include your frontend URL

---

## Next: Deploy Frontend

After backend is running, deploy the frontend to Vercel:
1. Go to [vercel.com](https://vercel.com)
2. Import the same GitHub repo
3. Set root directory to `frontend`
4. Add env var: `NEXT_PUBLIC_API_URL=https://stitchflow-api.onrender.com/api`
5. Deploy!
