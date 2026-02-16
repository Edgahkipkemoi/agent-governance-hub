'use client';

import { Info } from 'lucide-react';
import { useState } from 'react';

interface RiskTooltipProps {
  riskScore: number;
  details: string;
  hallucination: boolean;
  pii: boolean;
  toxic: boolean;
}

export function RiskTooltip({ riskScore, details, hallucination, pii, toxic }: RiskTooltipProps) {
  const [show, setShow] = useState(false);

  const getRiskLevel = () => {
    if (riskScore <= 3) return 'Safe';
    if (riskScore <= 6) return 'Warning';
    return 'Critical';
  };

  const getExplanation = () => {
    const issues = [];
    if (toxic) issues.push('safety violations');
    if (pii) issues.push('PII exposure');
    if (hallucination) issues.push('false information');
    
    if (issues.length === 0) {
      return 'No risk indicators detected. Response meets safety standards.';
    }
    
    return `Flagged: Contains ${issues.join(', ')}. ${details.substring(0, 100)}`;
  };

  return (
    <div className="relative inline-block">
      <button
        onMouseEnter={() => setShow(true)}
        onMouseLeave={() => setShow(false)}
        onFocus={() => setShow(true)}
        onBlur={() => setShow(false)}
        className="p-1 hover:bg-slate-700 rounded transition-colors"
        aria-label="Risk explanation"
      >
        <Info className="w-4 h-4 text-slate-400" />
      </button>
      
      {show && (
        <div className="absolute z-50 bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-64 p-3 bg-slate-800 border border-slate-600 rounded-lg shadow-xl">
          <div className="text-xs text-slate-300 leading-relaxed">
            <div className="font-semibold text-white mb-1">
              Risk Level: {getRiskLevel()} ({riskScore}/10)
            </div>
            {getExplanation()}
          </div>
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
            <div className="border-4 border-transparent border-t-slate-800"></div>
          </div>
        </div>
      )}
    </div>
  );
}
