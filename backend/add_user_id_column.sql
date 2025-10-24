-- Add user_id column to certificates table
ALTER TABLE public.certificates 
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id);

-- Create index on user_id for faster queries
CREATE INDEX IF NOT EXISTS idx_certificates_user_id ON public.certificates(user_id);

-- Update RLS policies to be user-specific
DROP POLICY IF EXISTS "Allow all operations" ON public.certificates;

-- Users can only see their own certificates
CREATE POLICY "Users can view own certificates" ON public.certificates
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can only insert their own certificates
CREATE POLICY "Users can insert own certificates" ON public.certificates
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can only update their own certificates
CREATE POLICY "Users can update own certificates" ON public.certificates
    FOR UPDATE
    USING (auth.uid() = user_id);

-- Users can only delete their own certificates
CREATE POLICY "Users can delete own certificates" ON public.certificates
    FOR DELETE
    USING (auth.uid() = user_id);
