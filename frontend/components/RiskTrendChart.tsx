'use client';

import { AuditLog } from '@/lib/supabase';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { useMemo } from 'react';

interface RiskTrendChartProps {
  logs: AuditLog[];
}

export function RiskTrendChart({ logs }: RiskTrendChartProps) {
  const chartData = useMemo(() => {
    // Get last 10 logs for the chart
    const recentLogs = logs.slice(0, 10).reverse();
    
    if (recentLogs.length === 0) return { points: [], trend: 'stable', avgChange: 0 };
    
    // Calculate trend
    const firstHalf = recentLogs.slice(0, Math.floor(recentLogs.length / 2));
    const secondHalf = recentLogs.slice(Math.floor(recentLogs.length / 2));
    
    const firstAvg = firstHalf.reduce((sum, log) => sum + log.audit.risk_score, 0) / firstHalf.length;
    const secondAvg = secondHalf.reduce((sum, log) => sum + log.audit.risk_score, 0) / secondHalf.length;
    
    const avgChange = secondAvg - firstAvg;
    const trend = avgChange > 0.5 ? 'up' : avgChange < -0.5 ? 'down' : 'stable';
    
    return { points: recentLogs, trend, avgChange };
  }, [logs]);

  const { points, trend, avgChange } = chartData;

  if (points.length === 0) {
    return (
      <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Risk Trend</h3>
        <div className="text-center py-8 text-slate-400">
          No data yet. Submit queries to see trends.
        </div>
      </div>
    );
  }

  const maxRisk = 10;
  const chartHeight = 120;

  return (
    <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Risk Trend (Last 10 Queries)</h3>
        <div className="flex items-center gap-2">
          {trend === 'up' && (
            <div className="flex items-center gap-1 text-red-400 text-sm">
              <TrendingUp className="w-4 h-4" />
              <span>+{avgChange.toFixed(1)}</span>
            </div>
          )}
          {trend === 'down' && (
            <div className="flex items-center gap-1 text-green-400 text-sm">
              <TrendingDown className="w-4 h-4" />
              <span>{avgChange.toFixed(1)}</span>
            </div>
          )}
          {trend === 'stable' && (
            <div className="flex items-center gap-1 text-slate-400 text-sm">
              <Minus className="w-4 h-4" />
              <span>Stable</span>
            </div>
          )}
        </div>
      </div>

      {/* Chart */}
      <div className="relative" style={{ height: chartHeight }}>
        {/* Y-axis labels */}
        <div className="absolute left-0 top-0 bottom-0 w-8 flex flex-col justify-between text-xs text-slate-500">
          <span>10</span>
          <span>5</span>
          <span>0</span>
        </div>

        {/* Chart area */}
        <div className="ml-10 h-full relative">
          {/* Grid lines */}
          <div className="absolute inset-0 flex flex-col justify-between">
            {[0, 1, 2, 3, 4].map((i) => (
              <div key={i} className="border-t border-slate-700/50"></div>
            ))}
          </div>

          {/* Line chart */}
          <svg className="absolute inset-0 w-full h-full">
            {/* Area fill */}
            <defs>
              <linearGradient id="riskGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="rgb(239, 68, 68)" stopOpacity="0.2" />
                <stop offset="100%" stopColor="rgb(34, 197, 94)" stopOpacity="0.2" />
              </linearGradient>
            </defs>
            
            <path
              d={`
                M 0 ${chartHeight}
                ${points.map((log, i) => {
                  const x = (i / (points.length - 1)) * 100;
                  const y = chartHeight - (log.audit.risk_score / maxRisk) * chartHeight;
                  return `L ${x}% ${y}`;
                }).join(' ')}
                L 100% ${chartHeight}
                Z
              `}
              fill="url(#riskGradient)"
            />

            {/* Line */}
            <polyline
              points={points.map((log, i) => {
                const x = (i / (points.length - 1)) * 100;
                const y = chartHeight - (log.audit.risk_score / maxRisk) * chartHeight;
                return `${x}%,${y}`;
              }).join(' ')}
              fill="none"
              stroke="rgb(59, 130, 246)"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />

            {/* Points */}
            {points.map((log, i) => {
              const x = (i / (points.length - 1)) * 100;
              const y = chartHeight - (log.audit.risk_score / maxRisk) * chartHeight;
              const color = log.audit.risk_score <= 3 ? 'rgb(34, 197, 94)' : 
                           log.audit.risk_score <= 6 ? 'rgb(234, 179, 8)' : 
                           'rgb(239, 68, 68)';
              
              return (
                <g key={log.id}>
                  <circle
                    cx={`${x}%`}
                    cy={y}
                    r="4"
                    fill={color}
                    stroke="rgb(15, 23, 42)"
                    strokeWidth="2"
                  />
                </g>
              );
            })}
          </svg>
        </div>
      </div>

      {/* Legend */}
      <div className="mt-4 pt-4 border-t border-slate-700 flex items-center justify-center gap-6 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-green-500"></div>
          <span className="text-slate-400">Safe (0-3)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
          <span className="text-slate-400">Warning (4-6)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500"></div>
          <span className="text-slate-400">Critical (7-10)</span>
        </div>
      </div>
    </div>
  );
}
