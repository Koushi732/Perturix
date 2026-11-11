import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, History, Settings, Info,
  ChevronLeft, ChevronRight, Shield
} from 'lucide-react';
import { cn } from '../../utils/cn';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'History', href: '/history', icon: History },
  { name: 'Settings', href: '/settings', icon: Settings },
  { name: 'About', href: '/about', icon: Info },
];

export const Sidebar = React.memo(function Sidebar({ collapsed, setCollapsed }: { collapsed: boolean, setCollapsed: (val: boolean) => void }) {
  return (
    <div className={cn(
      "flex flex-col bg-white dark:bg-dark-800/80 backdrop-blur-xl border-r border-black/5 h-screen sticky top-0 shrink-0 transition-all duration-200",
      collapsed ? "w-20 max-md:w-14" : "w-64 max-md:absolute max-md:z-50"
    )}>
      <div className="flex items-center h-16 px-4 border-b border-black/5 justify-between">
        {!collapsed && (
          <div className="flex items-center overflow-hidden">
            <Shield className="w-8 h-8 text-primary-500 mr-3 shrink-0" />
            <span className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">Perturix</span>
          </div>
        )}
        {collapsed && (
          <Shield className="w-8 h-8 text-primary-500 mx-auto shrink-0" />
        )}
      </div>
      
      <div className="flex-1 overflow-y-auto py-4 px-3 space-y-1 custom-scrollbar">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            title={item.name}
            className={({ isActive }) =>
              cn(
                'flex items-center px-3 py-2.5 max-md:px-2 max-md:py-2 rounded-lg text-sm font-medium transition-all duration-200',
                isActive
                  ? 'bg-primary-600/10 text-primary-500 border border-primary-500/20'
                  : 'text-slate-300 hover:text-slate-900 dark:hover:text-white dark:text-white hover:bg-black/5 border border-transparent',
                collapsed ? 'justify-center' : ''
              )
            }
          >
            <item.icon className={cn("w-5 h-5 shrink-0", !collapsed && "mr-3")} />
            {!collapsed && <span className="truncate">{item.name}</span>}
          </NavLink>
        ))}
      </div>

      <div className="p-4 max-md:p-2 border-t border-black/5 flex justify-end max-md:justify-center">
        <button 
          onClick={() => setCollapsed(!collapsed)}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          className="p-2 rounded-lg text-slate-300 hover:text-slate-900 dark:hover:text-white dark:text-white hover:bg-black/5 transition-colors"
        >
          {collapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
        </button>
      </div>
    </div>
  );
});
