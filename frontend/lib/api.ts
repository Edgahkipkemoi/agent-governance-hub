const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ProcessAgentResponse {
  id: string;
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
  created_at: string;
}

export async function processAgentQuery(query: string): Promise<ProcessAgentResponse> {
  const response = await fetch(`${API_URL}/process-agent`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ user_query: query }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Failed to process query');
  }

  return response.json();
}
