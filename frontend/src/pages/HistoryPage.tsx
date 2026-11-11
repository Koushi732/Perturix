import React, { useState, useEffect, useMemo } from 'react';
import { PageContainer } from '../components/common/PageContainer';
import { History, Search, Download, Trash2, Loader2, Eye, X, Shield, Play, Image as ImageIcon } from 'lucide-react';
import { Button } from '../components/common/Button';
import { historyService } from '../services/historyService';
import { imageService } from '../services/imageService';
import { motion, AnimatePresence } from 'framer-motion';
import { MetricCard } from '../components/common/MetricCard';
import { useToast } from '../context/ToastContext';

export default function HistoryPage() {
  const [historyData, setHistoryData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortField, setSortField] = useState<'date' | 'name'>('date');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');
  
  const { addToast } = useToast();
  
  const [viewingSession, setViewingSession] = useState<any | null>(null);
  const [loadingSession, setLoadingSession] = useState(false);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = () => {
    setLoading(true);
    historyService.getHistory().then(res => {
      if (res.success) {
        setHistoryData(res.data.items);
      }
      setLoading(false);
    }).catch(_err => {
      addToast({ type: 'error', message: 'Failed to load history.' });
      setLoading(false);
    });
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this session?")) return;
    try {
      await historyService.deleteSession(id);
      setHistoryData(prev => prev.filter(item => item.id !== id));
      if (viewingSession?.id === id) setViewingSession(null);
      addToast({ type: 'success', message: 'Session deleted successfully.' });
    } catch (_err) {
      addToast({ type: 'error', message: 'Failed to delete session.' });
    }
  };

  const handleView = async (id: string) => {
    setLoadingSession(true);
    try {
      const res = await historyService.getSession(id);
      if (res.success) {
        setViewingSession(res.data);
      }
    } catch (_err) {
      addToast({ type: 'error', message: 'Failed to load session details.' });
    } finally {
      setLoadingSession(false);
    }
  };

  const sortedAndFilteredData = useMemo(() => {
    let data = [...historyData];
    
    // Search
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      data = data.filter(item => 
        item.original_image_name.toLowerCase().includes(q) || 
        (item.attacks && item.attacks.length > 0 && item.attacks[0].attack_name.toLowerCase().includes(q))
      );
    }
    
    // Sort
    data.sort((a, b) => {
      if (sortField === 'date') {
        const valA = new Date(a.created_at).getTime();
        const valB = new Date(b.created_at).getTime();
        return sortDir === 'asc' ? valA - valB : valB - valA;
      } else {
        const valA = a.original_image_name;
        const valB = b.original_image_name;
        return sortDir === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA);
      }
    });
    
    return data;
  }, [historyData, searchQuery, sortField, sortDir]);

  return (
    <PageContainer title="Processing History" description="Log of all images processed through the Perturix pipeline.">
      <div className="glass-panel overflow-hidden relative">
        <div className="p-4 border-b border-black/5 flex flex-wrap gap-4 justify-between items-center bg-white dark:bg-dark-800/50">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 dark:text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input 
              type="text" 
              placeholder="Search history..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="glass-input pl-9 pr-4 py-2 text-sm w-64"
            />
          </div>
          <div className="flex items-center gap-4 text-sm">
            <span className="text-slate-300">Sort by:</span>
            <select 
              className="glass-input py-1 px-2 text-sm bg-slate-50 dark:bg-dark-900 border-black/10 text-slate-700 dark:text-slate-300"
              value={`${sortField}-${sortDir}`}
              onChange={(e) => {
                const [f, d] = e.target.value.split('-');
                setSortField(f as any);
                setSortDir(d as any);
              }}
            >
              <option value="date-desc">Newest First</option>
              <option value="date-asc">Oldest First</option>
              <option value="name-asc">File Name (A-Z)</option>
              <option value="name-desc">File Name (Z-A)</option>
            </select>
          </div>
        </div>
        
        <div className="overflow-x-auto min-h-[400px]">
          <table className="w-full text-left text-sm text-slate-700 dark:text-slate-300">
            <thead className="bg-slate-50 dark:bg-dark-900/50 text-slate-300 font-medium border-b border-black/5">
              <tr>
                <th className="px-6 py-4">File Name</th>
                <th className="px-6 py-4">Algorithm</th>
                <th className="px-6 py-4">Epsilon</th>
                <th className="px-6 py-4">Date</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {sortedAndFilteredData.map((item) => (
                <tr 
                  key={item.id} 
                  className="hover:bg-black/[0.05] transition-colors group cursor-pointer"
                  onClick={() => handleView(item.id)}
                >
                  <td className="px-6 py-4 font-medium text-slate-900 dark:text-white flex items-center gap-3">
                    <div className="w-10 h-10 rounded overflow-hidden bg-slate-50 dark:bg-dark-900 border border-black/10 shrink-0">
                      <img src={imageService.getImageUrl(item.original_image_name)} alt="Thumb" className="w-full h-full object-cover" />
                    </div>
                    <span className="truncate max-w-[150px] block" title={item.original_image_name}>{item.original_image_name}</span>
                  </td>
                  <td className="px-6 py-4 text-accent-400 font-mono">
                    {item.attacks && item.attacks.length > 0 ? item.attacks[0].attack_name : '-'}
                  </td>
                  <td className="px-6 py-4 font-mono">
                    {item.attacks && item.attacks.length > 0 && item.attacks[0].epsilon ? item.attacks[0].epsilon : '-'}
                  </td>
                  <td className="px-6 py-4 text-slate-400 dark:text-slate-500">{new Date(item.created_at).toLocaleString()}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${
                      item.status === 'completed' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 
                      item.status === 'failed' ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' :
                      'bg-blue-500/10 text-blue-400 border-blue-500/20'
                    }`}>
                      {item.status.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button 
                        className="p-1.5 text-slate-300 hover:text-slate-900 dark:hover:text-white dark:text-white bg-slate-100 dark:bg-dark-700 rounded transition-colors" 
                        title="View" 
                        aria-label="View"
                        onClick={(e) => { e.stopPropagation(); handleView(item.id); }}
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button 
                        className="p-1.5 text-slate-300 hover:text-rose-400 bg-slate-100 dark:bg-dark-700 rounded transition-colors" 
                        title="Delete" 
                        aria-label="Delete"
                        onClick={(e) => handleDelete(item.id, e)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {loading ? (
            <div className="flex flex-col items-center justify-center p-12 text-center absolute inset-0 bg-white dark:bg-dark-800/80 backdrop-blur z-10">
              <Loader2 className="w-8 h-8 text-primary-500 animate-spin mb-4" />
              <p className="text-sm text-slate-300">Loading history...</p>
            </div>
          ) : sortedAndFilteredData.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-12 text-center">
              <History className="w-12 h-12 text-slate-400 dark:text-slate-500 mb-4 opacity-50" />
              <h4 className="text-slate-900 dark:text-white font-medium mb-1">No processing history</h4>
              <p className="text-sm text-slate-300">No records found matching your criteria.</p>
            </div>
          ) : null}
        </div>
      </div>

      {/* History Details Modal */}
      <AnimatePresence>
        {viewingSession && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
            onClick={() => setViewingSession(null)}
          >
            <motion.div 
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="bg-white dark:bg-dark-800 border border-black/10 rounded-2xl shadow-2xl w-full max-w-6xl max-h-[90vh] overflow-y-auto custom-scrollbar relative flex flex-col"
              onClick={e => e.stopPropagation()}
            >
              <div className="sticky top-0 bg-white dark:bg-dark-800/90 backdrop-blur-md border-b border-black/10 p-6 flex justify-between items-center z-10">
                <div>
                  <h3 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                    Session Details
                    <span className="text-sm font-normal text-slate-300 bg-slate-50 dark:bg-dark-900 px-2 py-1 rounded border border-black/5">{viewingSession.id}</span>
                  </h3>
                  <p className="text-slate-300 text-sm mt-1">{new Date(viewingSession.created_at).toLocaleString()}</p>
                </div>
                <button 
                  onClick={() => setViewingSession(null)}
                  className="p-2 text-slate-300 hover:text-slate-900 dark:hover:text-white dark:text-white bg-black/5 hover:bg-black/10 rounded-full transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
              
              <div className="p-6 space-y-8">
                {/* Images View */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Original */}
                  <div className="glass-panel p-4 flex flex-col">
                    <div className="flex justify-between items-center mb-4">
                      <span className="text-sm font-medium text-slate-300">Original Image</span>
                    </div>
                    <div className="flex-1 bg-slate-50 dark:bg-dark-900/50 rounded-lg border border-black/5 overflow-hidden flex items-center justify-center min-h-[300px] p-2">
                      <img src={imageService.getImageUrl(viewingSession.original_image_name)} alt="Original" className="max-h-[400px] object-contain rounded" />
                    </div>
                  </div>
                  
                  {/* Protected */}
                  <div className="glass-panel p-4 flex flex-col ring-1 ring-primary-500/30">
                    <div className="flex justify-between items-center mb-4">
                      <span className="text-sm font-medium text-primary-400 flex items-center">
                        <Shield className="w-4 h-4 mr-1" />
                        Protected Image
                      </span>
                      <Button size="sm" onClick={() => {
                        const a = document.createElement('a');
                        a.href = imageService.getImageUrl(`${viewingSession.id}_adv.png`);
                        a.download = "protected_image.png";
                        a.click();
                      }}>
                        <Download className="w-4 h-4 mr-2" />
                        Download
                      </Button>
                    </div>
                    <div className="flex-1 bg-slate-50 dark:bg-dark-900/50 rounded-lg border border-black/5 overflow-hidden flex items-center justify-center min-h-[300px] p-2">
                      <img 
                        src={imageService.getImageUrl(`${viewingSession.id}_adv.png`)} 
                        alt="Protected" 
                        className="max-h-[400px] object-contain rounded"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = '';
                          (e.target as HTMLImageElement).alt = 'Protected image not available';
                        }} 
                      />
                    </div>
                  </div>
                </div>

                {/* Metrics */}
                {viewingSession.evaluations && viewingSession.evaluations.length > 0 ? (
                  <div>
                    <h4 className="text-lg font-medium text-slate-900 dark:text-white mb-4 border-b border-black/10 pb-2">Evaluation Metrics</h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                      <MetricCard title="PSNR" value={viewingSession.evaluations[0].psnr?.toFixed(2) || 'N/A'} icon={ImageIcon} />
                      <MetricCard title="SSIM" value={viewingSession.evaluations[0].ssim?.toFixed(4) || 'N/A'} icon={ImageIcon} />
                      <MetricCard title="LPIPS" value={viewingSession.evaluations[0].lpips?.toFixed(4) || 'N/A'} icon={ImageIcon} />
                      <MetricCard title="L2 Norm" value={viewingSession.evaluations[0].l2?.toFixed(2) || 'N/A'} icon={ImageIcon} />
                      <MetricCard title="Conf. Drop" value={((viewingSession.evaluations[0].confidence_drop || 0) * 100).toFixed(1) + '%'} icon={ImageIcon} />
                    </div>
                  </div>
                ) : (
                  <div className="p-4 bg-slate-50 dark:bg-dark-900 border border-black/5 rounded-lg text-slate-300 text-center">
                    No evaluation metrics available for this session.
                  </div>
                )}
                
                {/* Attack Info */}
                {viewingSession.attacks && viewingSession.attacks.length > 0 && (
                  <div className="glass-panel p-6 flex flex-col sm:flex-row gap-8 items-start sm:items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium text-slate-300 uppercase tracking-wider mb-2">Algorithm</h4>
                      <p className="text-xl font-mono text-slate-900 dark:text-white">{viewingSession.attacks[0].attack_name}</p>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-slate-300 uppercase tracking-wider mb-2">Strength (ε)</h4>
                      <p className="text-xl font-mono text-primary-400">{viewingSession.attacks[0].epsilon || 'N/A'}</p>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-slate-300 uppercase tracking-wider mb-2">Runtime</h4>
                      <p className="text-xl font-mono text-slate-900 dark:text-white flex items-center">
                        <Play className="w-5 h-5 mr-2 text-slate-400 dark:text-slate-500" />
                        {Math.round(viewingSession.attacks[0].execution_time_ms || 0)} ms
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {loadingSession && !viewingSession && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-white dark:bg-dark-800 p-6 rounded-xl border border-black/10 flex flex-col items-center">
            <Loader2 className="w-8 h-8 text-primary-500 animate-spin mb-4" />
            <p className="text-slate-900 dark:text-white font-medium">Loading session details...</p>
          </div>
        </div>
      )}
    </PageContainer>
  );
}
