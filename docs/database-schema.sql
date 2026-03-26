-- StitchFlow Database Schema for Supabase
-- Run this in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT,
    password_hash TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Wallets table
CREATE TABLE IF NOT EXISTS public.wallets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE REFERENCES public.users(id) ON DELETE CASCADE,
    balance NUMERIC(12, 2) DEFAULT 0.00,
    currency TEXT DEFAULT 'KES',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Jobs table
CREATE TABLE IF NOT EXISTS public.jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    complexity TEXT DEFAULT 'auto',
    mime_type TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    file_path TEXT,
    original_url TEXT,
    output_dst_url TEXT,
    output_svg_url TEXT,
    output_json_url TEXT,
    price NUMERIC(10, 2) NOT NULL,
    payment_status TEXT DEFAULT 'unpaid',
    progress INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Payments table
CREATE TABLE IF NOT EXISTS public.payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    job_id UUID REFERENCES public.jobs(id) ON DELETE SET NULL,
    amount NUMERIC(10, 2) NOT NULL,
    phone TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    transaction_id TEXT,
    checkout_request_id TEXT,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Transactions table
CREATE TABLE IF NOT EXISTS public.transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    amount NUMERIC(10, 2) NOT NULL,
    type TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    description TEXT,
    reference TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create storage buckets (run separately if needed)
-- Note: Storage buckets are managed in Supabase Dashboard > Storage

-- Indexes
CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON public.jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON public.jobs(status);
CREATE INDEX IF NOT EXISTS idx_payments_job_id ON public.payments(job_id);
CREATE INDEX IF NOT EXISTS idx_payments_transaction_id ON public.payments(transaction_id);
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON public.transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_wallets_user_id ON public.wallets(user_id);

-- Enable Row Level Security
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wallets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.transactions ENABLE ROW LEVEL SECURITY;

-- RLS Policies for Users
CREATE POLICY "users_select_policy" ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "users_update_policy" ON public.users
    FOR UPDATE USING (auth.uid() = id);

-- RLS Policies for Wallets
CREATE POLICY "wallets_select_policy" ON public.wallets
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "wallets_update_policy" ON public.wallets
    FOR UPDATE USING (auth.uid() = user_id);

-- RLS Policies for Jobs
CREATE POLICY "jobs_select_policy" ON public.jobs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "jobs_insert_policy" ON public.jobs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "jobs_update_policy" ON public.jobs
    FOR UPDATE USING (auth.uid() = user_id);

-- RLS Policies for Payments
CREATE POLICY "payments_select_policy" ON public.payments
    FOR SELECT USING (auth.uid() = user_id);

-- RLS Policies for Transactions
CREATE POLICY "transactions_select_policy" ON public.transactions
    FOR SELECT USING (auth.uid() = user_id);

-- Create admin function (for service role operations)
CREATE OR REPLACE FUNCTION public.admin_can_read_all()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM pg_roles 
        WHERE rolname = 'service_role' 
        AND pg_has_role(current_user, rolname, 'member')
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Note: For production, manage storage buckets in Supabase Dashboard
-- Go to Storage > New bucket > Create "uploads" and "outputs"

-- Wallet balance functions
CREATE OR REPLACE FUNCTION public.add_wallet_balance(p_user_id UUID, p_amount NUMERIC)
RETURNS NUMERIC AS $
DECLARE
    new_balance NUMERIC;
BEGIN
    UPDATE public.wallets 
    SET balance = balance + p_amount, updated_at = NOW()
    WHERE user_id = p_user_id
    RETURNING balance INTO new_balance;
    RETURN new_balance;
END;
$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.deduct_wallet_balance(p_user_id UUID, p_amount NUMERIC)
RETURNS NUMERIC AS $
DECLARE
    new_balance NUMERIC;
BEGIN
    UPDATE public.wallets 
    SET balance = balance - p_amount, updated_at = NOW()
    WHERE user_id = p_user_id AND balance >= p_amount
    RETURNING balance INTO new_balance;
    RETURN new_balance;
END;
$ LANGUAGE plpgsql;
