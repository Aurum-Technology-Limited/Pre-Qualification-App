-- Create certificates table in Supabase
CREATE TABLE IF NOT EXISTS public.certificates (
    id BIGSERIAL PRIMARY KEY,
    certificate_id TEXT UNIQUE NOT NULL,
    calculation_type TEXT NOT NULL,
    applicant JSONB NOT NULL,
    currency TEXT NOT NULL,
    issue_date TEXT NOT NULL,
    expiry_date TEXT NOT NULL,
    validity_days INTEGER NOT NULL,
    gross_monthly_income NUMERIC,
    dsr_ratio NUMERIC,
    monthly_obligations NUMERIC,
    affordable_payment NUMERIC,
    affordable_payment_formatted TEXT,
    max_loan_amount NUMERIC,
    max_loan_formatted TEXT,
    principal_amount NUMERIC,
    principal_formatted TEXT,
    monthly_payment NUMERIC,
    monthly_payment_formatted TEXT,
    annual_interest_rate NUMERIC NOT NULL,
    interest_rate_percent NUMERIC NOT NULL,
    term_years INTEGER NOT NULL,
    total_payments NUMERIC,
    total_payments_formatted TEXT,
    total_interest NUMERIC,
    total_interest_formatted TEXT,
    stress_test JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    pdf_generated BOOLEAN DEFAULT FALSE,
    pdf_path TEXT
);

-- Create index on certificate_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_certificates_certificate_id ON public.certificates(certificate_id);

-- Create index on created_at for sorting
CREATE INDEX IF NOT EXISTS idx_certificates_created_at ON public.certificates(created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE public.certificates ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (adjust as needed for production)
CREATE POLICY "Allow all operations" ON public.certificates
    FOR ALL
    USING (true)
    WITH CHECK (true);
