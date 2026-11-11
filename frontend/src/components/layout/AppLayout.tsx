import React, { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { TopNavigation } from './TopNavigation';
import { ErrorBoundary } from '../common/ErrorBoundary';

export function AppLayout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const location = useLocation();

  // Basic breadcrumb generation
  const pathnames = location.pathname.split('/').filter((x) => x);
  const breadcrumbs = pathnames.length > 0 
    ? pathnames.map(p => p.charAt(0).toUpperCase() + p.slice(1))
    : ['Dashboard'];

  return (
    <div className="flex min-h-screen bg-slate-50 dark:bg-dark-900 text-slate-700 dark:text-slate-300 font-sans">
      <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} />
      
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        <TopNavigation breadcrumbs={breadcrumbs} />
        
        <main className="flex-1 overflow-y-auto p-8 relative custom-scrollbar">
          {/* Subtle ambient glows for dark mode */}
          <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-primary-500/10 rounded-full blur-[120px] pointer-events-none -z-10" />
          <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-accent-500/10 rounded-full blur-[100px] pointer-events-none -z-10" />
          
          <div className="max-w-6xl mx-auto w-full pb-20">
            <ErrorBoundary>
              <Outlet />
            </ErrorBoundary>
          </div>
        </main>
      </div>
    </div>
  );
}
