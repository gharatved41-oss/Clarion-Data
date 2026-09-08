import React from 'react';
import { useTelemetry } from '../../context/TelemetryContext';

export const Sidebar = () => {
  const {
    currentView,
    setCurrentView,
    setIsAiDrawerOpen,
    setActiveModal,
    activeDatasetId,
    theme,
    toggleTheme,
    metadata
  } = useTelemetry();

  const pipelineNav = [
    { id: 'schema-detection', label: 'Schema Detection', icon: 'schema' },
    { id: 'quality-and-audit', label: 'Quality & Audit', icon: 'verified' },
    { id: 'visualizations', label: 'Visualizations', icon: 'monitoring' },
    { id: 'insights-explorer', label: 'Insights & Stats', icon: 'neurology' },
    { id: 'tabular-explorer', label: 'Tabular Explorer', icon: 'table_chart' },
  ];

  const auxiliaryNav = [
    { id: 'domain-detection', label: 'Domain & KPIs', icon: 'domain_verification' },
    { id: 'ai-analyst', label: 'AI Analyst Copilot', icon: 'smart_toy', isTertiary: true, isDrawerTrigger: true },
    { id: 'executive-reports', label: 'Executive Reports', icon: 'assignment' },
    { id: 'audit-history', label: 'Audit History', icon: 'history' },
    { id: 'settings-and-tolerances', label: 'Settings & Tolerances', icon: 'tune' },
  ];

  const handleNavClick = (item) => {
    if (item.isDrawerTrigger) {
      setIsAiDrawerOpen(true);
    }
    setCurrentView(item.id);
  };

  return (
    <aside className="fixed left-0 top-0 h-screen w-60 bg-surface-container-lowest border-r border-outline-variant/30 z-50 flex flex-col justify-between select-none font-body-md print:hidden">
      <div className="flex flex-col">
        {/* Brand Header with Clarion Data Logo */}
        <div className="h-14 px-space-4 border-b border-outline-variant/30 flex items-center gap-space-3 bg-surface-container-low">
          <img
            src="/clarion-data-logo.png"
            alt="Clarion Data Logo"
            className="h-8 w-8 object-contain shrink-0 rounded-sm"
          />
          <div className="flex flex-col min-w-0">
            <span className="font-headline-sm text-[14px] text-on-surface truncate tracking-tight font-semibold">
              Clarion Data
            </span>
            <span className="font-label-caps text-[10px] text-on-surface-variant uppercase tracking-wider">
              AI Insight Analyst
            </span>
          </div>
        </div>

        {/* Action Button: Ingest New Dataset & Push to Supabase DB */}
        <div className="p-space-3 border-b border-outline-variant/20 bg-surface-container-low flex flex-col gap-1.5">
          <button
            onClick={() => setActiveModal('upload-dataset')}
            className="w-full flex items-center justify-center gap-2 py-2 px-3 bg-primary hover:bg-primary-fixed-dim text-on-primary text-xs font-bold font-headline-sm transition-all shadow-sm active:scale-98"
            type="button"
          >
            <span className="material-symbols-outlined text-[16px]">cloud_upload</span>
            <span>Ingest Dataset</span>
          </button>
          <button
            onClick={() => setActiveModal('supabase-sync')}
            className="w-full flex items-center justify-center gap-2 py-1.5 px-3 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[11px] font-semibold font-data-mono transition-all active:scale-98"
            type="button"
            title="Synchronize active dataset with Supabase database"
          >
            <span className="material-symbols-outlined text-[15px]">database</span>
            <span>Push to Database</span>
          </button>
        </div>

        {/* Pipeline Operations */}
        <div className="px-space-4 pt-space-3 pb-space-1">
          <span className="font-label-caps text-[11px] text-outline uppercase tracking-wider block font-bold">
            Pipeline Operations
          </span>
        </div>
        <nav className="flex flex-col gap-1 px-space-2">
          {pipelineNav.map((item) => {
            const isActive = currentView === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item)}
                className={`w-full flex items-center gap-space-3 px-space-3 py-1.5 transition-colors text-left text-[13px] font-medium ${
                  isActive
                    ? 'bg-primary-container text-on-surface border-l-2 border-primary font-semibold'
                    : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface'
                }`}
              >
                <span className="material-symbols-outlined text-[18px] shrink-0">
                  {item.icon}
                </span>
                <span className="truncate">{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Auxiliary Tools */}
        <div className="px-space-4 pt-space-4 pb-space-1">
          <span className="font-label-caps text-[11px] text-outline uppercase tracking-wider block font-bold">
            Intelligence & Audit
          </span>
        </div>
        <nav className="flex flex-col gap-1 px-space-2">
          {auxiliaryNav.map((item) => {
            const isActive = currentView === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item)}
                className={`w-full flex items-center gap-space-3 px-space-3 py-1.5 transition-colors text-left text-[13px] font-medium ${
                  isActive
                    ? 'bg-primary-container text-on-surface border-l-2 border-primary font-semibold'
                    : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface'
                }`}
              >
                <span className={`material-symbols-outlined text-[18px] shrink-0 ${item.isTertiary ? 'text-tertiary' : ''}`}>
                  {item.icon}
                </span>
                <span className="truncate">{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer / Active Dataset Pill & System Status */}
      <div className="p-space-3 border-t border-outline-variant/30 bg-surface-container-low flex flex-col gap-2 font-data-mono">
        {/* Active Context Card */}
        <div className="p-2 bg-surface-container-lowest border border-outline-variant/40 flex flex-col gap-1 text-[11px]">
          <div className="flex items-center justify-between text-outline text-[10px] uppercase font-bold">
            <span>Active Dataset</span>
            <span className="text-tertiary">Live</span>
          </div>
          <span className="text-on-surface font-semibold truncate" title={activeDatasetId}>
            {activeDatasetId}
          </span>
          <span className="text-outline text-[10px]">
            {metadata.rows.toLocaleString()} rows • {metadata.columns} cols
          </span>
        </div>

        {/* Quick Theme Toggle Button */}
        <button
          onClick={toggleTheme}
          className="w-full flex items-center justify-between px-2.5 py-1.5 bg-surface-container hover:bg-surface-container-high border border-outline-variant/30 text-body-sm text-on-surface transition-colors"
          type="button"
          title={`Click to switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
        >
          <div className="flex items-center gap-1.5">
            <span className={`material-symbols-outlined text-[16px] ${theme === 'dark' ? 'text-amber-400' : 'text-primary'}`}>
              {theme === 'dark' ? 'light_mode' : 'dark_mode'}
            </span>
            <span className="text-xs font-semibold">{theme === 'dark' ? 'Dark Mode' : 'Light Mode'}</span>
          </div>
          <span className="text-[10px] font-label-caps uppercase text-outline">TOGGLE</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
