'use client';

import { Shield, AlertTriangle, CheckCircle } from 'lucide-react';

interface StatusBadgeProps {
  status: 'Safe' | 'Warning' | 'Flagged';
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const config = {
    Safe: {
      bg: 'bg-green-500/10',
      text: 'text-green-400',
      border: 'border-green-500/20',
      icon: CheckCircle,
    },
    Warning: {
      bg: 'bg-yellow-500/10',
      text: 'text-yellow-400',
      border: 'border-yellow-500/20',
      icon: AlertTriangle,
    },
    Flagged: {
      bg: 'bg-red-500/10',
      text: 'text-red-400',
      border: 'border-red-500/20',
      icon: Shield,
    },
  };

  const { bg, text, border, icon: Icon } = config[status];

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${bg} ${text} ${border}`}>
      <Icon className="w-3 h-3" />
      {status}
    </span>
  );
}
