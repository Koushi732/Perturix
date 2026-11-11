import React, { useEffect, useState } from 'react';
import { PageContainer } from '../components/common/PageContainer';
import { apiClient } from '../services/apiClient';
import { Activity } from 'lucide-react';

export default function SettingsPage() {
  const [systemInfo, setSystemInfo] = useState<any>(null);
  const [systemStatus, setSystemStatus] = useState<any>(null);
  
  useEffect(() => {
    apiClient.request<any>('/system/info').then(res => setSystemInfo(res.data)).catch(() => {});
    apiClient.request<any>('/system/status').then(res => setSystemStatus(res.data)).catch(() => {});
  }, []);

  return (
    <PageContainer title="System Status" description="Real-time backend connectivity and system health.">
      <div className="glass-panel p-6 max-w-2xl">
        <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-6 border-b border-black/5 pb-4 flex items-center">
          <Activity className="w-5 h-5 text-primary-500 mr-2" />
          Backend Connection
        </h3>
        
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h4 className="text-sm font-medium text-slate-200">Application Name</h4>
              <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">Configured instance name.</p>
            </div>
            <span className="text-sm font-mono text-primary-400">{systemInfo?.app_name || 'Loading...'}</span>
          </div>

          <div className="flex justify-between items-center">
            <div>
              <h4 className="text-sm font-medium text-slate-200">Environment</h4>
              <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">Current deployment environment.</p>
            </div>
            <span className="text-sm font-mono text-emerald-400">{systemInfo?.environment || 'Loading...'}</span>
          </div>

          <div className="flex justify-between items-center">
            <div>
              <h4 className="text-sm font-medium text-slate-200">AI Engine Status</h4>
              <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">Neural network registry connection.</p>
            </div>
            <span className="text-sm font-mono text-emerald-400">{systemStatus?.ai_registry === 'ready' ? 'Ready' : 'Loading...'}</span>
          </div>
          
          <div className="flex justify-between items-center">
            <div>
              <h4 className="text-sm font-medium text-slate-200">Storage Provider</h4>
              <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">File system read/write availability.</p>
            </div>
            <span className="text-sm font-mono text-emerald-400">{systemStatus?.storage === 'connected' ? 'Connected' : 'Loading...'}</span>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
