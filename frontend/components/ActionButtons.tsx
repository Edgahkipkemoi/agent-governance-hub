'use client';

import { CheckCircle, XCircle, RefreshCw, Archive } from 'lucide-react';
import { useState } from 'react';

interface ActionButtonsProps {
  logId: string;
  status: 'Safe' | 'Warning' | 'Flagged';
  onAction: (action: string) => void;
}

export function ActionButtons({ logId, status, onAction }: ActionButtonsProps) {
  const [actionTaken, setActionTaken] = useState<string | null>(null);

  const handleAction = (action: string) => {
    setActionTaken(action);
    onAction(action);
    
    // Reset after 3 seconds
    setTimeout(() => setActionTaken(null), 3000);
  };

  if (status === 'Safe') return null;

  if (actionTaken) {
    return (
      <div className="flex items-center gap-2 text-xs text-green-400">
        <CheckCircle className="w-4 h-4" />
        Action: {actionTaken}
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={() => handleAction('Override')}
        className="px-3 py-1.5 bg-green-500/10 hover:bg-green-500/20 text-green-400 border border-green-500/20 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5"
        title="Confirm AI response was correct"
      >
        <CheckCircle className="w-3.5 h-3.5" />
        Override
      </button>
      
      <button
        onClick={() => handleAction('Block')}
        className="px-3 py-1.5 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5"
        title="Block this query type"
      >
        <XCircle className="w-3.5 h-3.5" />
        Block
      </button>
      
      <button
        onClick={() => handleAction('Regenerate')}
        className="px-3 py-1.5 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/20 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5"
        title="Regenerate response"
      >
        <RefreshCw className="w-3.5 h-3.5" />
        Retry
      </button>
      
      <button
        onClick={() => handleAction('Archive')}
        className="px-3 py-1.5 bg-slate-500/10 hover:bg-slate-500/20 text-slate-400 border border-slate-500/20 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5"
        title="Archive this log"
      >
        <Archive className="w-3.5 h-3.5" />
        Archive
      </button>
    </div>
  );
}
