'use client';

import { CheckCircle, XCircle, RefreshCw, Archive, ShieldAlert, EyeOff } from 'lucide-react';
import { useState } from 'react';

interface ActionButtonsProps {
  logId: string;
  status: 'Safe' | 'Warning' | 'Flagged';
  onAction: (action: string) => void;
}

export function ActionButtons({ logId, status, onAction }: ActionButtonsProps) {
  const [showConfirm, setShowConfirm] = useState<string | null>(null);

  const handleAction = (action: string) => {
    // Critical actions need confirmation
    if ((action === 'Revoke' || action === 'Redact') && !showConfirm) {
      setShowConfirm(action);
      return;
    }

    setShowConfirm(null);
    onAction(action);
  };

  const cancelConfirm = () => {
    setShowConfirm(null);
  };

  if (status === 'Safe') return null;

  // Confirmation dialog for critical actions
  if (showConfirm) {
    return (
      <div className="px-4 py-3 bg-red-500/10 border border-red-500/20 rounded-lg">
        <div className="text-sm font-semibold text-red-400 mb-2">
          ⚠️ Confirm {showConfirm === 'Revoke' ? 'Agent Session Revocation' : 'Force Redaction'}
        </div>
        <div className="text-xs text-slate-400 mb-3">
          {showConfirm === 'Revoke' 
            ? 'This will immediately terminate the agent session and prevent similar queries.'
            : 'This will permanently redact the response from all logs and audit trails.'}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleAction(showConfirm)}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-xs font-semibold transition-all"
          >
            Confirm {showConfirm}
          </button>
          <button
            onClick={cancelConfirm}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-xs font-semibold transition-all"
          >
            Cancel
          </button>
        </div>
      </div>
    );
  }

  // Flagged items get critical HITL actions
  if (status === 'Flagged') {
    return (
      <div className="space-y-3">
        <div className="text-xs font-semibold text-red-400 uppercase tracking-wide flex items-center gap-2">
          <ShieldAlert className="w-4 h-4" />
          Human-in-the-Loop Required
        </div>
        
        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={() => handleAction('Revoke')}
            className="px-4 py-3 bg-red-600 hover:bg-red-700 text-white border-2 border-red-500 rounded-lg text-sm font-bold transition-all flex items-center justify-center gap-2 shadow-lg hover:shadow-red-500/50"
            title="Immediately revoke agent session"
          >
            <ShieldAlert className="w-4 h-4" />
            Revoke Agent Session
          </button>
          
          <button
            onClick={() => handleAction('Redact')}
            className="px-4 py-3 bg-orange-600 hover:bg-orange-700 text-white border-2 border-orange-500 rounded-lg text-sm font-bold transition-all flex items-center justify-center gap-2 shadow-lg hover:shadow-orange-500/50"
            title="Permanently redact response"
          >
            <EyeOff className="w-4 h-4" />
            Force Redact
          </button>
        </div>

        <div className="flex items-center gap-2 pt-2 border-t border-slate-700">
          <button
            onClick={() => handleAction('Override')}
            className="flex-1 px-3 py-2 bg-green-500/10 hover:bg-green-500/20 text-green-400 border border-green-500/20 rounded-lg text-xs font-medium transition-all flex items-center justify-center gap-1.5"
            title="False positive - AI was correct"
          >
            <CheckCircle className="w-3.5 h-3.5" />
            Override (False Positive)
          </button>
          
          <button
            onClick={() => handleAction('Archive')}
            className="flex-1 px-3 py-2 bg-slate-500/10 hover:bg-slate-500/20 text-slate-400 border border-slate-500/20 rounded-lg text-xs font-medium transition-all flex items-center justify-center gap-1.5"
            title="Archive for review"
          >
            <Archive className="w-3.5 h-3.5" />
            Archive
          </button>
        </div>
      </div>
    );
  }

  // Warning items get standard actions
  return (
    <div className="space-y-2">
      <div className="text-xs font-semibold text-yellow-400 uppercase tracking-wide">
        Review Required
      </div>
      
      <div className="flex items-center gap-2 flex-wrap">
        <button
          onClick={() => handleAction('Override')}
          className="px-3 py-2 bg-green-500/10 hover:bg-green-500/20 text-green-400 border border-green-500/20 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5"
          title="Confirm AI response was correct"
        >
          <CheckCircle className="w-3.5 h-3.5" />
          Override
        </button>
        
        <button
          onClick={() => handleAction('Block')}
          className="px-3 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5"
          title="Block this query type"
        >
          <XCircle className="w-3.5 h-3.5" />
          Block
        </button>
        
        <button
          onClick={() => handleAction('Regenerate')}
          className="px-3 py-2 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/20 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5"
          title="Regenerate response"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Retry
        </button>
        
        <button
          onClick={() => handleAction('Archive')}
          className="px-3 py-2 bg-slate-500/10 hover:bg-slate-500/20 text-slate-400 border border-slate-500/20 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5"
          title="Archive this log"
        >
          <Archive className="w-3.5 h-3.5" />
          Archive
        </button>
      </div>
    </div>
  );
}
