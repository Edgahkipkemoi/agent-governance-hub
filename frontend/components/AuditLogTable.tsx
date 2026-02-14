'use client';

import { AuditLog } from '@/lib/supabase';
import { StatusBadge } from './StatusBadge';
import { Shield, AlertTriangle, CheckCircle, Clock, MessageSquare } from 'lucide-react';
import { useState } from 'react';

interface AuditLogTableProps {
  logs: AuditLog[];
}

export function AuditLogTable({ logs }: AuditLogTableProps) {
  const [expandedLog, setExpandedLog] = useState<string | null>(null);

  if (logs.length === 0) {
    return (
      <div className="text-center py-16 bg-slate-900/30 rounded-lg border border-slate-700 border-dashed">
        <Shield className="w-16 h-16 text-slate-600 mx-auto mb-4" />
        <p className="text-slate-400 text-lg">No audit logs yet</p>
        <p className="text-slate-500 text-sm mt-2">Submit a query above to get started</p>
      </div>
    );
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    }).format(date);
  };

  const toggleExpand = (id: string) => {
    setExpandedLog(expandedLog === id ? null : id);
  };

  return (
    <div className="space-y-3">
      {logs.map((log) => {
        const isExpanded = expandedLog === log.id;
        const riskColor = 
          log.audit.risk_score <= 3 ? 'text-green-400' :
          log.audit.risk_score <= 6 ? 'text-yellow-400' :
          'text-red-400';

        return (
          <div
            key={log.id}
            className="bg-slate-900/50 border border-slate-700 rounded-lg overflow-hidden hover:border-slate-600 transition-all"
          >
            {/* Header */}
            <div
              className="p-4 cursor-pointer"
              onClick={() => toggleExpand(log.id)}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-2">
                    <StatusBadge status={log.status} />
                    <span className={`text-sm font-mono font-semibold ${riskColor}`}>
                      Risk: {log.audit.risk_score}/10
                    </span>
                    <span className="text-xs text-slate-500 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {formatDate(log.created_at)}
                    </span>
                  </div>
                  <p className="text-slate-300 text-sm line-clamp-2">
                    {log.query}
                  </p>
                </div>

                {/* Risk Indicators */}
                <div className="flex items-center gap-2 flex-shrink-0">
                  {log.audit.hallucination_detected && (
                    <div className="p-2 bg-red-500/10 rounded-lg" title="Hallucination detected">
                      <AlertTriangle className="w-4 h-4 text-red-400" />
                    </div>
                  )}
                  {log.audit.pii_detected && (
                    <div className="p-2 bg-yellow-500/10 rounded-lg" title="PII detected">
                      <Shield className="w-4 h-4 text-yellow-400" />
                    </div>
                  )}
                  {log.audit.toxic_content_detected && (
                    <div className="p-2 bg-red-500/10 rounded-lg" title="Toxic content detected">
                      <AlertTriangle className="w-4 h-4 text-red-400" />
                    </div>
                  )}
                  {!log.audit.hallucination_detected && 
                   !log.audit.pii_detected && 
                   !log.audit.toxic_content_detected && (
                    <div className="p-2 bg-green-500/10 rounded-lg" title="No issues detected">
                      <CheckCircle className="w-4 h-4 text-green-400" />
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Expanded Details */}
            {isExpanded && (
              <div className="border-t border-slate-700 bg-slate-900/70">
                <div className="p-4 space-y-4">
                  {/* Response */}
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <MessageSquare className="w-4 h-4 text-blue-400" />
                      <h4 className="text-sm font-semibold text-slate-300">Agent Response</h4>
                    </div>
                    <p className="text-sm text-slate-400 bg-slate-800/50 p-3 rounded-lg border border-slate-700">
                      {log.response}
                    </p>
                  </div>

                  {/* Audit Details */}
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Shield className="w-4 h-4 text-purple-400" />
                      <h4 className="text-sm font-semibold text-slate-300">Audit Analysis</h4>
                    </div>
                    <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700 space-y-2">
                      <p className="text-sm text-slate-400">{log.audit.details}</p>
                      
                      <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-700">
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${log.audit.hallucination_detected ? 'bg-red-400' : 'bg-green-400'}`} />
                          <span className="text-xs text-slate-400">Hallucination</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${log.audit.pii_detected ? 'bg-yellow-400' : 'bg-green-400'}`} />
                          <span className="text-xs text-slate-400">PII Leak</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${log.audit.toxic_content_detected ? 'bg-red-400' : 'bg-green-400'}`} />
                          <span className="text-xs text-slate-400">Toxic Content</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
