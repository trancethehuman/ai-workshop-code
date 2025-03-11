import { createClient } from "npm:@supabase/supabase-js@2";

// Define conversation state type
export interface ConversationState {
  history: Array<{ role: string; content: string }>;
}

// Create Supabase client using service role to bypass RLS
export function getSupabaseClient() {
  // For edge functions, these environment variables should be available
  const supabaseUrl = Deno.env.get("DB_URL") as string;
  const supabaseServiceKey = Deno.env.get("SERVICE_ROLE_KEY") as string;

  if (!supabaseUrl || !supabaseServiceKey) {
    console.error("Missing Supabase environment variables");
    throw new Error("Missing DB_URL or SERVICE_ROLE_KEY");
  }

  return createClient(supabaseUrl, supabaseServiceKey, {
    auth: {
      persistSession: false,
    },
  });
}

// Get conversation state from Supabase
export async function getConversationState(
  threadId: string
): Promise<ConversationState | null> {
  const supabase = getSupabaseClient();
  console.log(`Fetching conversation state for thread: ${threadId}`);

  try {
    const { data, error } = await supabase
      .from("conversation_state")
      .select("history")
      .eq("thread_id", threadId)
      .single();

    if (error) {
      if (error.code === "PGRST116") {
        // Record not found - this is normal for a new thread
        console.log(`No existing conversation found for thread: ${threadId}`);
        return null;
      }
      console.error("Error fetching conversation state:", error);
      throw error;
    }

    console.log(
      `Successfully retrieved conversation state for thread: ${threadId}`
    );
    return data as ConversationState;
  } catch (error) {
    console.error("Unexpected error in getConversationState:", error);
    throw error;
  }
}

// Save conversation state to Supabase
export async function saveConversationState(
  threadId: string,
  state: ConversationState
): Promise<void> {
  const supabase = getSupabaseClient();
  console.log(`Saving conversation state for thread: ${threadId}`);

  try {
    const { data, error } = await supabase.from("conversation_state").upsert(
      {
        thread_id: threadId,
        history: state.history,
        updated_at: new Date().toISOString(),
      },
      { onConflict: "thread_id" }
    );

    if (error) {
      console.error("Error saving conversation state:", error);
      throw error;
    }

    console.log(
      `Successfully saved conversation state for thread: ${threadId}`
    );
  } catch (error) {
    console.error("Unexpected error in saveConversationState:", error);
    throw error;
  }
}
