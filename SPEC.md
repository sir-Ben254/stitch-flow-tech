# StitchFlow - Embroidery File Conversion SaaS

## Project Overview

**Project Name:** StitchFlow
**Type:** SaaS Web Application
**Core Functionality:** Upload images and receive embroidery-ready files (DST for simple images, SVG + structured format for complex images that can be imported into Wilcom EmbroideryStudio)
**Target Users:** Embroidery businesses, hobbyists, fashion designers, custom apparel shops

---

## Technical Architecture

### Tech Stack
- **Frontend:** Next.js 14 (App Router), TailwindCSS, Framer Motion
- **Backend:** FastAPI (Python)
- **Worker:** Celery + Redis
- **Database & Storage:** Supabase (PostgreSQL + Storage)
- **Payments:** Safaricom Daraja API (STK Push)
- **Deployment:** Render (default), VPS-ready

### Project Structure
```
stitchflow/
├── frontend/           # Next.js application
│   ├── src/
│   │   ├── app/       # App router pages
│   │   ├── components/# React components
│   │   ├── lib/       # Utilities
│   │   └── styles/    # Global styles
│   └── public/        # Static assets
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── api/       # API routes
│   │   ├── core/      # Core config
│   │   ├── models/    # Database models
│   │   ├── schemas/   # Pydantic schemas
│   │   └── services/  # Business logic
│   └── requirements.txt
├── worker/           # Celery worker
│   ├── tasks/        # Processing tasks
│   └── requirements.txt
├── infra/           # Infrastructure config
│   ├── docker/      # Docker configs
│   └── render/      # Render configs
└── docs/            # Documentation
```

---

## UI/UX Specification

### Color Palette
- **Primary:** `#6366F1` (Indigo-500)
- **Primary Dark:** `#4F46E5` (Indigo-600)
- **Secondary:** `#EC4899` (Pink-500)
- **Accent:** `#10B981` (Emerald-500)
- **Background:** `#0F172A` (Slate-900)
- **Surface:** `#1E293B` (Slate-800)
- **Surface Light:** `#334155` (Slate-700)
- **Text Primary:** `#F8FAFC` (Slate-50)
- **Text Secondary:** `#94A3B8` (Slate-400)
- **Error:** `#EF4444` (Red-500)
- **Success:** `#22C55E` (Green-500)
- **Warning:** `#F59E0B` (Amber-500)

### Typography
- **Font Family:** "Outfit" (headings), "DM Sans" (body)
- **Headings:**
  - H1: 56px/64px, weight 700
  - H2: 40px/48px, weight 600
  - H3: 28px/36px, weight 600
  - H4: 20px/28px, weight 500
- **Body:**
  - Large: 18px/28px, weight 400
  - Regular: 16px/24px, weight 400
  - Small: 14px/20px, weight 400

### Spacing System
- Base unit: 4px
- Scale: 4, 8, 12, 16, 24, 32, 48, 64, 96, 128

### Responsive Breakpoints
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

### Animations
- Page transitions: 300ms ease-out
- Hover effects: 150ms ease
- Micro-interactions: 200ms spring
- Optimized for 60fps on low-end devices

---

## Pages & Components

### 1. Landing Page

**Hero Section:**
- Headline: "Transform Any Image Into Embroidery"
- Subheadline: "Upload your design and get production-ready embroidery files in minutes"
- CTA Button: "Start Converting" (scrolls to upload)
- Background: Animated gradient mesh with floating thread patterns

**Features Section:**
- 4 feature cards with icons
- DST Output, SVG + Wilcom Compatible, Fast Processing, Secure Storage

**How It Works Section:**
- 3-step visual process
- Upload → Process → Download

**Pricing Section:**
- Pay-per-use cards
- Wallet top-up option

**Footer:**
- Logo
- Social links (Instagram, TikTok, Facebook)
- WhatsApp contact only
- Copyright

### 2. Robot Assistant

**Design:**
- Floating character (bottom-left)
- Circular eyes that track cursor/touch
- Animated idle state (breathing/blinking)
- Toggle button (on/off)

**Behavior:**
- Eyes follow cursor on desktop
- Eyes follow scroll direction on mobile
- Low CPU usage (CSS transforms only)
- Can be minimized

### 3. Chatbot

**Trigger:**
- Floating button (bottom-right)
- Opens chat modal

**Features:**
- Pre-defined FAQ responses
- Pricing info
- How system works
- Supported formats
- Troubleshooting
- Unrecognized questions → WhatsApp redirect

### 4. Dashboard

**Layout:**
- Sidebar navigation
- Main content area

**Pages:**
- **Home/Upload:** Drag-drop upload, job queue
- **Jobs:** List of all jobs with status
- **Wallet:** Balance, top-up, transactions
- **Downloads:** Available files

---

## Backend API Specification

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login (returns JWT)
- `GET /api/auth/me` - Get current user

### Jobs
- `POST /api/jobs/upload` - Upload image for processing
- `GET /api/jobs/status/{job_id}` - Get job status
- `GET /api/jobs/` - List user jobs
- `GET /api/jobs/{job_id}/download` - Download output file

### Payments
- `POST /api/payments/stkpush` - Initiate STK push
- `POST /api/payments/callback` - Payment callback
- `GET /api/payments/status/{job_id}` - Payment status

### Wallet
- `GET /api/wallet/balance` - Get balance
- `POST /api/wallet/topup` - Top up wallet
- `GET /api/wallet/transactions` - List transactions

---

## Processing Pipeline

### Image Validation
1. Check MIME type (png, jpg, jpeg, webp, bmp)
2. Check file size (max 10MB)
3. Malware scan (ClamAV)
4. Validate image integrity

### Image Processing
1. Clean image (OpenCV denoise, enhance)
2. Vectorize (potrace/imagetracer)
3. Detect complexity level

### Simple Images → DST
- Convert to embroidery pattern
- Optimize for production
- Generate clean DST file

### Complex Images → SVG + Wilcom
- Layer by color
- Preserve stitch types
- Export as SVG
- Export structured JSON (Wilcom-compatible)

---

## Security Specification

### Authentication
- JWT tokens (access + refresh)
- bcrypt password hashing
- Token expiry: 15min access, 7 days refresh

### Rate Limiting
- Upload: 5 requests/minute/IP
- API: 60 requests/minute/IP

### CAPTCHA
- Cloudflare Turnstile on upload/login forms

### File Security
- MIME type validation
- Extension validation
- Malware scanning
- Secure file storage (signed URLs)

---

## Payment System

### Daraja API Integration
- STK Push for payments
- Callback URL for confirmation
- Payment verification
- Retry logic (3 attempts)

### Wallet System
- Pre-paid wallet
- Auto-deduct on job completion
- Transaction history

---

## Scalability Modes

### Mode 1: LOW (Free/Render)
- Max 10 concurrent users
- Queue processing
- 5MB file limit
- 1 worker

### Mode 2: HIGH (VPS/Paid)
- Horizontal scaling
- Multiple workers
- 20MB file limit
- Priority processing

---

## Acceptance Criteria

1. ✓ Landing page loads in < 3 seconds
2. ✓ Robot assistant follows cursor smoothly
3. ✓ Image upload completes with progress indicator
4. ✓ Job processing shows real-time status
5. ✓ Payment via STK push works end-to-end
6. ✓ Wallet balance updates correctly
7. ✓ Downloaded files are valid
8. ✓ All endpoints protected with JWT
9. ✓ Rate limiting prevents abuse
10. ✓ Responsive on all device sizes
