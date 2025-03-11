-- Update RLS policies for conversation_state table to allow all access
DO $block$
BEGIN
  IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'conversation_state') THEN
    -- Ensure RLS is enabled
    ALTER TABLE public.conversation_state ENABLE ROW LEVEL SECURITY;

    -- Drop existing policies if they exist
    DROP POLICY IF EXISTS "Enable read for authenticated users" ON public.conversation_state;
    DROP POLICY IF EXISTS "Enable insert for authenticated users" ON public.conversation_state;
    DROP POLICY IF EXISTS "Enable update for authenticated users" ON public.conversation_state;
    
    -- Create new open policies
    DROP POLICY IF EXISTS "Allow all read access" ON public.conversation_state;
    CREATE POLICY "Allow all read access" 
      ON public.conversation_state 
      FOR SELECT 
      USING (true);
      
    DROP POLICY IF EXISTS "Allow all insert access" ON public.conversation_state;
    CREATE POLICY "Allow all insert access" 
      ON public.conversation_state 
      FOR INSERT 
      WITH CHECK (true);
      
    DROP POLICY IF EXISTS "Allow all update access" ON public.conversation_state;
    CREATE POLICY "Allow all update access" 
      ON public.conversation_state 
      FOR UPDATE 
      USING (true);
  END IF;
END;
$block$;