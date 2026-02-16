'use client';

import { AuditLog } from '@/lib/supabase';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { useMemo, useState } from 'react';

type TimeRange = 'today' | 'yesterday' | '1week' | '1month' | '3months' | '6months' | 'ytd';

interface RiskTrendChartProps {
  logs: AuditLog[];
}

export function RiskTrendChart({ logs }: RiskTrendChartProps) {
  const [timeRange, setTimeRange] = useState<TimeRange>('1week');

  const getDateRange = (range: TimeRange) => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    
    switch (range) {
      case 'today':
        return { start: today, end: now };
      case 'yesterday':
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        return { start: yesterday, end: today };
      case '1week':
        const weekAgo = new Date(today);
        weekAgo.setDate(weekAgo.getDate() - 7);
        return { start: weekAgo, end: now };
      case '1month':
        const monthAgo = new Date(today);
        monthAgo.setMonth(monthAgo.getMonth() - 1);
        return { start: monthAgo, end: now };
      case '3months':
        const threeMonthsAgo = new Date(today);
        threeMonthsAgo.setMonth(threeMonthsAgo.getMonth() - 3);
        return { start: threeMonthsAgo, end: now };
      case '6months':
        const sixMonthsAgo = new Date(today);
        sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);
        return { start: sixMonthsAgo, end: now };
      case 'ytd':
        const yearStart = new Date(now.getFullYear(), 0, 1);
        return { start: yearStart, end: now };
    }
  };

  const chartData = useMemo(() => {
    const { start, end } = getDateRange(timeRange);
    
    // Filter logs by date range
    const filteredLogs = logs.filter(log => {
      const logDate = new Date(log.created_at);
      return logDate >= start && logDate <= end;
    }).reverse();
    
    if (filteredLogs.length === 0) return { points: [], trend: 'stable', avgChange: 0, count: 0 };
    
    // Calculate trend
    const firstHalf = filteredLogs.slice(0, Math.floor(filteredLogs.length / 2));
    const secondHalf = filteredLogs.slice(Math.floor(filteredLogs.length / 2));
    
    const firstAvg = firstHalf.reduce((sum, log) => sum + log.audit.risk_score, 0) / firstHalf.length;
    const secondAvg = secondHalf.reduce((sum, log) => sum + log.audit.risk_score, 0) / secondHalf.length;
    
    const avgChange = secondAvg - firstAvg;
    const trend = avgChange > 0.5 ? 'up' : avgChange < -0.5 ? 'down' : 'stable';
    
    return { points: filteredLogs, trend, avgChange, count: filteredLogs.length };
  }, [logs, timeRange]);

  const { points, trend, avgChange, count } = chartData;

  const timeRangeOptions: { value: TimeRange; label: string }[] = [
    { value: 'today', label: 'Today' },
    { value: 'yesterday', label: 'Yesterday' },
    { value: '1week', label: '1 Week' },
    { value: '1month', label: '1 Month' },
    { value: '3months', label: '3 Months' },
    { value: '6months', label: '6 Months' },
    { value: 'ytd', label: 'YTD' },
  ];

  const maxRisk = 10;
  const chartHeight = 120;

  return (
    <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
        <h3 className="text-lg font-semibold text-white">Risk Trend</h3>
        
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          {/* Time Range Selector - Dropdown on mobile, buttons on desktop */}
          <div className="sm:hidden">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value as TimeRange)}
              className="w-full px-3 py-2 text-sm font-medium bg-slate-900/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {timeRangeOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Desktop button group */}
          <div className="hidden sm:flex items-center gap-1 bg-slate-900/50 rounded-lg p-1">
            {timeRangeOptions.map((option) => (
              <button
                key={option.value}
                onClick={() => setTimeRange(option.value)}
                className={`px-2 lg:px-3 py-1 text-xs font-medium rounded transition-colors whitespace-nowrap ${
                  timeRange === option.value
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
          
          {/* Trend Indicator */}
          {points.length > 0 && (
            <div className="flex items-center gap-2 justify-end sm:justify-start">
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
          )}
        </div>
      </div>

      {/* Query Count */}
      {points.length > 0 && (
        <div className="mb-3 text-sm text-slate-400">
          {count} {count === 1 ? 'query' : 'queries'} in this period
        </div>
      )}

      {points.length === 0 ? (
        <div className="text-center py-8 text-slate-400">
          No data for this time range. Try a different period.
        </div>
      ) : (
        <>
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
          <div className="mt-4 pt-4 border-t border-slate-700 flex flex-wrap items-center justify-center gap-4 sm:gap-6 text-xs">
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
        </>
      )}
    </div>
  );
}
