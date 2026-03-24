# StitchFlow Deployment Guide

## Quick Deploy (Frontend Only - Static)

The simplest way to start is to deploy the static `index.html` file:

### Option 1: Vercel (Recommended for Frontend)
1. Go to [vercel.com](https://vercel.com)
2. Connect your GitHub repository
3. Import the project
4. Deploy with default settings

### Option 2: Netlify
1. Go to [netlify.com](https://netlify.com)
2. Drag and drop the `index.html` file (or connect GitHub)
3. Your site is live!

---

## Full Stack Deployment

### Prerequisites
- [ ] Supabase account (create at supabase.com)
- [ ] Render account (for backend) or VPS

---

### Step 1: Set up Supabase

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to SQL Editor and run `docs/database-schema.sql`
3. Get your credentials from Settings → API:
   - Project URL
   - anon key (public)
   - service_role key (secret - keep safe!)

---

### Step 2: Deploy Backend (Render)

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repository
4. Configure:
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `backend`
5. Add Environment Variables:
   ```
   SECRET_KEY=your-random-secret-key
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   SUPABASE_SERVICE_KEY=your-service-role-key
   DARAJA_CONSUMER_KEY=your-daraja-key
   DARAJA_CONSUMER_SECRET=your-daraja-secret
   DARAJA_SHORTCODE=your-shortcode
   DARAJA_PASSKEY=your-passkey
   DARAJA_CALLBACK_URL=https://your-backend.onrender.com/api/payments/callback
   DARAJA_ENVIRONMENT=sandbox
   ```
6. Deploy!

---

### Step 3: Deploy Frontend (Vercel)

1. Go to [vercel.com](https://vercel.com) → New Project
2. Import from GitHub
3. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
4. Add Environment Variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.onrender.com/api
   ```
5. Deploy!

---

### Step 4: Configure M-Pesa (Safaricom)

1. Go to [Daraja Portal](https://developer.safaricom.co.ke)
2. Create an app
3. Get Consumer Key & Secret
4. Set up Callback URL (must be HTTPS)
5. Update your backend environment variables

---

### Alternative: Docker Deployment

Use the included Docker Compose for local development or VPS:

```bash
# Clone repository
git clone https://github.com/your-repo/stitchflow.git
cd stitchflow

# Create .env file
cp backend/.env.example backend/.env
# Edit backend/.env with your credentials

# Start all services
docker-compose -f infra/docker/docker-compose.yml up
```

---

### VPS Deployment (Production)

For a production VPS (Ubuntu 22.04):

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Nginx
sudo apt install nginx certbot python3-certbot-nginx

# Clone and configure
git clone https://github.com/your-repo/stitchflow.git
cd stitchflow

# Set up environment
cp backend/.env.example backend/.env
nano backend/.env  # Configure your values

# Deploy with Docker Compose
docker-compose -f infra/docker/docker-compose.yml up -d

# Set up SSL
sudo certbot --nginx -d yourdomain.com
```

---

## Troubleshooting

### Frontend shows nothing
- Ensure `NEXT_PUBLIC_API_URL` points to your backend
- Check browser console for errors

### Backend 500 errors
- Check environment variables are set
- Check Supabase credentials are correct
- Check logs: `render logs` or `docker-compose logs`

### Payments not working
- Verify M-Pesa Daraja credentials
- Ensure callback URL is publicly accessible (HTTPS)
- Check STK Push is enabled for your shortcode

### Database errors
- Run the SQL schema in Supabase SQL Editor
- Check RLS policies are configured
