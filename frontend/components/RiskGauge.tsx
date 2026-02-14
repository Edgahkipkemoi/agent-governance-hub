'use client';

interface RiskGaugeProps {
  averageRisk: number;
  totalLogs: number;
}

export function RiskGauge({ averageRisk, totalLogs }: RiskGaugeProps) {
  const percentage = (averageRisk / 10) * 100;
  
  const getColor = () => {
    if (averageRisk <= 3) return { bg: 'bg-green-500', text: 'text-green-400', ring: 'ring-green-500/20' };
    if (averageRisk <= 6) return { bg: 'bg-yellow-500', text: 'text-yellow-400', ring: 'ring-yellow-500/20' };
    return { bg: 'bg-red-500', text: 'text-red-400', ring: 'ring-red-500/20' };
  };

  const getStatus = () => {
    if (averageRisk <= 3) return 'Safe';
    if (averageRisk <= 6) return 'Warning';
    return 'Critical';
  };

  const colors = getColor();
  const status = getStatus();

  return (
    <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-white mb-2">Average Risk Score</h3>
          <div className="flex items-baseline gap-2 mb-3">
            <span className={`text-5xl font-bold ${colors.text}`}>
              {averageRisk.toFixed(1)}
            </span>
            <span className="text-2xl text-slate-400">/ 10</span>
          </div>
          <div className="flex items-center gap-3">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${colors.bg} bg-opacity-20 ${colors.text}`}>
              {status}
            </span>
            <span className="text-sm text-slate-400">
              Based on {totalLogs} {totalLogs === 1 ? 'query' : 'queries'}
            </span>
          </div>
        </div>

        {/* Circular Progress */}
        <div className="relative w-40 h-40">
          <svg className="transform -rotate-90 w-40 h-40">
            {/* Background circle */}
            <circle
              cx="80"
              cy="80"
              r="70"
              stroke="currentColor"
              strokeWidth="12"
              fill="transparent"
              className="text-slate-700"
            />
            {/* Progress circle */}
            <circle
              cx="80"
              cy="80"
              r="70"
              stroke="currentColor"
              strokeWidth="12"
              fill="transparent"
              strokeDasharray={`${2 * Math.PI * 70}`}
              strokeDashoffset={`${2 * Math.PI * 70 * (1 - percentage / 100)}`}
              className={colors.text}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className={`text-3xl font-bold ${colors.text}`}>
                {percentage.toFixed(0)}%
              </div>
              <div className="text-xs text-slate-400 mt-1">Risk Level</div>
            </div>
          </div>
        </div>
      </div>

      {/* Risk Scale */}
      <div className="mt-6 pt-6 border-t border-slate-700">
        <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
          <span>Risk Scale</span>
          <span>0 - 10</span>
        </div>
        <div className="h-2 bg-slate-700 rounded-full overflow-hidden flex">
          <div className="flex-1 bg-green-500"></div>
          <div className="flex-1 bg-yellow-500"></div>
          <div className="flex-1 bg-red-500"></div>
        </div>
        <div className="flex items-center justify-between text-xs text-slate-400 mt-2">
          <span>Safe (0-3)</span>
          <span>Warning (4-6)</span>
          <span>Critical (7-10)</span>
        </div>
      </div>
    </div>
  );
}
