-- Create a table for storing conversation state
CREATE TABLE public.conversation_state (
  thread_id UUID PRIMARY KEY,
  history JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);

-- Add RLS policies
ALTER TABLE public.conversation_state ENABLE ROW LEVEL SECURITY;

-- Create policy to allow edge functions to read/write
CREATE POLICY "Enable read for authenticated users" 
  ON public.conversation_state 
  FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Enable insert for authenticated users" 
  ON public.conversation_state 
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Enable update for authenticated users" 
  ON public.conversation_state 
  FOR UPDATE USING (auth.role() = 'authenticated');

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at
CREATE TRIGGER update_conversation_state_updated_at
BEFORE UPDATE ON public.conversation_state
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column(); 