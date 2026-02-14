'use client';

import { useEffect, useState } from 'react';
import { supabase, AuditLog } from '@/lib/supabase';
import { TestQueryInput } from '@/components/TestQueryInput';
import { RiskGauge } from '@/components/RiskGauge';
import { RiskTrendChart } from '@/components/RiskTrendChart';
import { AuditLogTable } from '@/components/AuditLogTable';
import { Activity, Shield, AlertTriangle, CheckCircle } from 'lucide-react';

export default function DashboardPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'connecting'>('connecting');
  const [averageRisk, setAverageRisk] = useState(0);
  const [setupError, setSetupError] = useState<string | null>(null);

  // Calculate statistics
  const stats = {
    total: logs.length,
    safe: logs.filter(l => l.status === 'Safe').length,
    warning: logs.filter(l => l.status === 'Warning').length,
    flagged: logs.filter(l => l.status === 'Flagged').length,
  };

  // Calculate average risk score
  useEffect(() => {
    if (logs.length === 0) {
      setAverageRisk(0);
      return;
    }

    const totalRisk = logs.reduce((sum, log) => sum + log.audit.risk_score, 0);
    setAverageRisk(totalRisk / logs.length);
  }, [logs]);

  // Fetch initial logs
  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const { data, error } = await supabase
          .from('logs')
          .select('*')
          .order('created_at', { ascending: false })
          .limit(50);

        if (error) {
          console.error('Supabase error:', error);
          if (error.message.includes('relation "logs" does not exist')) {
            setSetupError('Database table not found. Please run the migration SQL in Supabase.');
          } else if (error.message.includes('JWT')) {
            setSetupError('Invalid Supabase API key. Please check your NEXT_PUBLIC_SUPABASE_ANON_KEY.');
          } else {
            setSetupError(`Database error: ${error.message}`);
          }
          return;
        }
        setLogs(data || []);
        setSetupError(null);
      } catch (error) {
        console.error('Error fetching logs:', error);
        setSetupError('Unable to connect to database. Check your configuration.');
      }
    };

    fetchLogs();
  }, []);

  // Set up real-time subscription
  useEffect(() => {
    setConnectionStatus('connecting');

    const channel = supabase
      .channel('logs-changes')
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'logs',
        },
        (payload) => {
          console.log('✅ Real-time update received:', payload);
          setLogs((current) => [payload.new as AuditLog, ...current]);
        }
      )
      .subscribe((status, err) => {
        console.log('Realtime subscription status:', status, err);
        if (status === 'SUBSCRIBED') {
          setConnectionStatus('connected');
          console.log('✅ Successfully subscribed to real-time updates');
        } else if (status === 'CLOSED' || status === 'CHANNEL_ERROR') {
          setConnectionStatus('disconnected');
          console.error('❌ Realtime connection error:', err);
        }
      });

    return () => {
      console.log('Cleaning up realtime subscription');
      supabase.removeChannel(channel);
    };
  }, []);

  const handleQuerySuccess = () => {
    console.log('Query submitted successfully');
    // Manually fetch the latest logs as a fallback
    setTimeout(async () => {
      try {
        const { data, error } = await supabase
          .from('logs')
          .select('*')
          .order('created_at', { ascending: false })
          .limit(50);
        
        if (!error && data) {
          setLogs(data);
        }
      } catch (error) {
        console.error('Error refreshing logs:', error);
      }
    }, 1000); // Wait 1 second for the backend to save
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-500/10 rounded-xl border border-blue-500/20">
              <Shield className="w-8 h-8 text-blue-400" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">Agent Audit System</h1>
              <p className="text-slate-400 mt-1">Real-time AI governance & monitoring</p>
            </div>
          </div>
          
          {/* Connection Status */}
          <div className="flex items-center gap-3 px-4 py-2 bg-slate-800/50 rounded-lg border border-slate-700">
            <div className={`w-2 h-2 rounded-full ${
              connectionStatus === 'connected' ? 'bg-green-500 animate-pulse' : 
              connectionStatus === 'connecting' ? 'bg-yellow-500 animate-pulse' : 
              'bg-red-500'
            }`} />
            <span className="text-sm text-slate-300 capitalize">{connectionStatus}</span>
          </div>
        </div>

        {/* Setup Error Alert */}
        {setupError && (
          <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4">
            <div className="flex gap-3">
              <AlertTriangle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-yellow-400 mb-2">Setup Required</h3>
                <p className="text-sm text-slate-300 mb-3">{setupError}</p>
                <div className="text-xs text-slate-400 space-y-1">
                  <p className="font-medium text-slate-300">Quick fix:</p>
                  <ol className="list-decimal ml-4 space-y-1">
                    <li>Open Supabase SQL Editor</li>
                    <li>Run migration from <code className="bg-slate-800 px-1.5 py-0.5 rounded">backend/migrations/001_create_logs_table.sql</code></li>
                    <li>Enable table replication</li>
                  </ol>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm font-medium">Total Queries</p>
                <p className="text-3xl font-bold text-white mt-1">{stats.total}</p>
              </div>
              <Activity className="w-8 h-8 text-blue-400" />
            </div>
          </div>

          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm font-medium">Safe</p>
                <p className="text-3xl font-bold text-green-400 mt-1">{stats.safe}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-400" />
            </div>
          </div>

          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm font-medium">Warnings</p>
                <p className="text-3xl font-bold text-yellow-400 mt-1">{stats.warning}</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-yellow-400" />
            </div>
          </div>

          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm font-medium">Flagged</p>
                <p className="text-3xl font-bold text-red-400 mt-1">{stats.flagged}</p>
              </div>
              <Shield className="w-8 h-8 text-red-400" />
            </div>
          </div>
        </div>

        {/* Risk Gauge and Trend Chart */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <RiskGauge averageRisk={averageRisk} totalLogs={logs.length} />
          <RiskTrendChart logs={logs} />
        </div>

        {/* Test Query Input */}
        <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Test Agent Query</h2>
          <TestQueryInput onSuccess={handleQuerySuccess} />
        </div>

        {/* Audit Logs Table */}
        <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Recent Audit Logs</h2>
          <AuditLogTable logs={logs} />
        </div>
      </div>
    </main>
  );
}
