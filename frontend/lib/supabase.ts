import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export interface AuditLog {
  id: string;
  created_at: string;
  query: string;
  response: string;
  audit: {
    risk_score: number;
    hallucination_detected: boolean;
    pii_detected: boolean;
    toxic_content_detected: boolean;
    details: string;
  };
  status: 'Safe' | 'Warning' | 'Flagged';
}
