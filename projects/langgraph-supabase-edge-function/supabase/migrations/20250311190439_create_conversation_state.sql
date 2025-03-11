-- Create a table for storing conversation state
CREATE TABLE IF NOT EXISTS public.conversation_state (
  thread_id UUID PRIMARY KEY,
  history JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);

-- Only modify RLS if table exists
DO $block$
BEGIN
  IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'conversation_state') THEN
    -- Add RLS policies
    ALTER TABLE public.conversation_state ENABLE ROW LEVEL SECURITY;

    -- Create policy to allow all access (replacing the authenticated-only policies)
    DROP POLICY IF EXISTS "Enable read for authenticated users" ON public.conversation_state;
    DROP POLICY IF EXISTS "Enable insert for authenticated users" ON public.conversation_state;
    DROP POLICY IF EXISTS "Enable update for authenticated users" ON public.conversation_state;
    
    -- Create policies that allow any access (including anonymous and service roles)
    CREATE POLICY "Allow all read access" 
      ON public.conversation_state 
      FOR SELECT 
      USING (true);
      
    CREATE POLICY "Allow all insert access" 
      ON public.conversation_state 
      FOR INSERT 
      WITH CHECK (true);
      
    CREATE POLICY "Allow all update access" 
      ON public.conversation_state 
      FOR UPDATE 
      USING (true);

    -- Create trigger if doesn't exist
    IF NOT EXISTS (
      SELECT FROM pg_trigger
      WHERE tgname = 'update_conversation_state_updated_at'
    ) THEN
      -- Function to update the updated_at timestamp
      CREATE OR REPLACE FUNCTION public.update_updated_at_column()
      RETURNS TRIGGER AS $func$
      BEGIN
        NEW.updated_at = now();
        RETURN NEW;
      END;
      $func$ LANGUAGE plpgsql;

      -- Trigger to automatically update updated_at
      CREATE TRIGGER update_conversation_state_updated_at
      BEFORE UPDATE ON public.conversation_state
      FOR EACH ROW
      EXECUTE FUNCTION public.update_updated_at_column();
    END IF;
  END IF;
END;
$block$;