import React, { useState } from 'react';
import { useTelemetry } from '../../context/TelemetryContext';

export const Header = () => {
  const {
    metadata,
    activeDatasetId,
    setActiveDatasetId,
    availableDatasets,
    setActiveModal,
    setIsAiDrawerOpen,
    currentView,
    setCurrentView,
    theme,
    themeMode,
    setTheme,
    isLoading,
    refreshActiveDataset,
    addAuditLog,
  } = useTelemetry();

  const [isDatasetDropdownOpen, setIsDatasetDropdownOpen] = useState(false);
  const [isThemeDropdownOpen, setIsThemeDropdownOpen] = useState(false);

  return (
    <header className="fixed top-0 left-60 right-0 z-40 bg-surface-container border-b border-outline-variant/30 select-none print:hidden">
      {/* Top Header Bar */}
      <div className="h-14 px-space-4 flex items-center justify-between gap-space-4 font-data-mono">
        {/* Left Telemetry Badges & Dataset Selector */}
        <div className="flex items-center gap-space-3 min-w-0">
          {/* Clarion Data Branding Logo & Title */}
          <div className="flex items-center gap-2 shrink-0 pr-3 border-r border-outline-variant/30">
            <img
              src="/clarion-data-logo.png"
              alt="Clarion Data Logo"
              className="h-8 sm:h-9 w-auto object-contain shrink-0"
              loading="eager"
            />
            <span className="hidden xl:inline text-xs font-bold font-headline-sm text-on-surface tracking-tight">
              Clarion Data
            </span>
          </div>

          {/* Active Dataset Selector Dropdown */}
          <div className="relative">
            <button
              onClick={() => setIsDatasetDropdownOpen(!isDatasetDropdownOpen)}
              className="flex items-center gap-space-2 px-space-3 py-1.5 bg-surface-container-low hover:bg-surface-container-high border border-outline-variant/50 text-body-sm font-semibold text-on-surface transition-all cursor-pointer shadow-sm active:scale-98"
              type="button"
              title="Click to switch active dataset context"
            >
              <span className="material-symbols-outlined text-[17px] text-primary">database</span>
              <span className="truncate max-w-[170px] text-primary">{activeDatasetId}</span>
              <span className="text-outline text-xs">({metadata.rows.toLocaleString()} rows)</span>
              <span className="material-symbols-outlined text-[15px] text-outline">expand_more</span>
            </button>

            {isDatasetDropdownOpen && (
              <div className="absolute left-0 mt-1 w-80 bg-surface-container-high border border-outline-variant/70 shadow-2xl z-50 py-1 max-h-96 overflow-y-auto">
                <div className="px-3 py-1.5 text-[11px] font-label-caps uppercase text-outline tracking-wider border-b border-outline-variant/30 flex items-center justify-between">
                  <span>Select Active Dataset</span>
                  <button
                    onClick={() => {
                      setIsDatasetDropdownOpen(false);
                      setActiveModal('upload-dataset');
                    }}
                    className="text-primary hover:underline text-[10px] font-bold uppercase"
                  >
                    + Upload New
                  </button>
                </div>
                {availableDatasets.map((ds) => (
                  <button
                    key={ds.id}
                    onClick={() => {
                      setActiveDatasetId(ds.id);
                      setIsDatasetDropdownOpen(false);
                      addAuditLog("DATASET_SWITCHED", `Switched active context to '${ds.id}'`);
                    }}
                    className={`w-full px-3 py-2 text-left text-xs flex items-center justify-between hover:bg-primary-container/40 transition-colors ${
                      activeDatasetId === ds.id ? 'bg-primary-container text-primary font-bold' : 'text-on-surface'
                    }`}
                  >
                    <div className="flex flex-col truncate pr-2">
                      <span className="font-semibold truncate">{ds.name || ds.id}</span>
                      <span className="text-[10px] text-outline">{ds.domain || 'Tabular'}</span>
                    </div>
                    {activeDatasetId === ds.id && (
                      <span className="material-symbols-outlined text-sm text-primary shrink-0">check</span>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Quick Upload Button */}
          <button
            onClick={() => setActiveModal('upload-dataset')}
            className="flex items-center gap-1.5 px-space-2.5 py-1.5 bg-primary-container hover:bg-primary-container/80 text-primary border border-primary/50 text-xs font-bold transition-all cursor-pointer active:scale-95"
            type="button"
            title="Upload CSV or Excel dataset"
          >
            <span className="material-symbols-outlined text-[16px]">cloud_upload</span>
            <span className="hidden md:inline">Upload</span>
          </button>

          {/* Validity & Health Status */}
          <div className="hidden sm:flex items-center gap-1 px-space-2 py-1 bg-tertiary-container border border-tertiary/30 font-label-caps text-[10px] text-tertiary uppercase font-bold tracking-wider">
            <span className="w-1.5 h-1.5 bg-tertiary inline-block"></span>
            <span>{metadata.validity}</span>
          </div>

          <div className="hidden xl:flex items-center gap-space-2 px-space-2 py-1 bg-surface-container-low border border-outline-variant/30 text-body-sm">
            <span className="text-outline">Health:</span>
            <span className="text-secondary font-semibold">{metadata.healthScore} / 100</span>
          </div>

          {isLoading && (
            <div className="flex items-center gap-1.5 text-xs text-primary font-mono animate-pulse">
              <span className="material-symbols-outlined text-[15px] animate-spin">sync</span>
              <span className="hidden lg:inline">Syncing...</span>
            </div>
          )}
        </div>

        {/* Right Action Bar */}
        <div className="flex items-center gap-space-2 relative">
          {/* Refresh Data Button */}
          <button
            onClick={refreshActiveDataset}
            className="p-1.5 bg-surface-container hover:bg-surface-container-high text-outline hover:text-on-surface border border-outline-variant/40 transition-colors"
            type="button"
            title="Refresh active dataset telemetry"
          >
            <span className="material-symbols-outlined text-[17px]">refresh</span>
          </button>

          {/* Theme Switcher 3-Way Selector */}
          <div className="relative">
            <button
              onClick={() => setIsThemeDropdownOpen(!isThemeDropdownOpen)}
              className="flex items-center gap-1.5 px-space-2.5 py-1.5 bg-surface-container hover:bg-surface-container-high text-on-surface border border-outline-variant/40 text-xs font-semibold transition-all cursor-pointer shadow-sm active:scale-95"
              type="button"
              title={`Active Theme: ${themeMode.toUpperCase()} (${theme})`}
              id="theme-switcher-btn"
            >
              <span className={`material-symbols-outlined text-[16px] ${theme === 'dark' ? 'text-amber-400' : 'text-primary'}`}>
                {themeMode === 'light' ? 'light_mode' : themeMode === 'dark' ? 'dark_mode' : 'settings_brightness'}
              </span>
              <span className="hidden md:inline capitalize">{themeMode}</span>
              <span className="material-symbols-outlined text-[13px] text-outline">expand_more</span>
            </button>

            {isThemeDropdownOpen && (
              <div className="absolute right-0 mt-1 w-36 bg-surface-container-high border border-outline-variant/60 shadow-2xl z-50 py-1">
                <button
                  onClick={() => {
                    setTheme('light');
                    setIsThemeDropdownOpen(false);
                    addAuditLog("THEME_CHANGED", "Switched theme to Light Mode");
                  }}
                  className={`w-full px-3 py-1.5 text-left text-xs flex items-center gap-2 hover:bg-primary-container/40 ${
                    themeMode === 'light' ? 'bg-primary-container text-primary font-bold' : 'text-on-surface'
                  }`}
                >
                  <span className="material-symbols-outlined text-sm text-amber-500">light_mode</span>
                  <span>Light</span>
                </button>
                <button
                  onClick={() => {
                    setTheme('dark');
                    setIsThemeDropdownOpen(false);
                    addAuditLog("THEME_CHANGED", "Switched theme to Dark Mode");
                  }}
                  className={`w-full px-3 py-1.5 text-left text-xs flex items-center gap-2 hover:bg-primary-container/40 ${
                    themeMode === 'dark' ? 'bg-primary-container text-primary font-bold' : 'text-on-surface'
                  }`}
                >
                  <span className="material-symbols-outlined text-sm text-sky-400">dark_mode</span>
                  <span>Dark</span>
                </button>
                <button
                  onClick={() => {
                    setTheme('system');
                    setIsThemeDropdownOpen(false);
                    addAuditLog("THEME_CHANGED", "Switched theme to System Default");
                  }}
                  className={`w-full px-3 py-1.5 text-left text-xs flex items-center gap-2 hover:bg-primary-container/40 ${
                    themeMode === 'system' ? 'bg-primary-container text-primary font-bold' : 'text-on-surface'
                  }`}
                >
                  <span className="material-symbols-outlined text-sm text-outline">settings_brightness</span>
                  <span>System</span>
                </button>
              </div>
            )}
          </div>

          {/* Push to Supabase Cloud Database Button */}
          <button
            onClick={() => setActiveModal('supabase-sync')}
            className="hidden sm:flex items-center gap-1.5 px-space-2.5 py-1.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-body-sm font-semibold transition-all cursor-pointer active:scale-95"
            type="button"
            title="Push active dataset records into Supabase cloud database"
          >
            <span className="material-symbols-outlined text-[16px] text-emerald-400">database</span>
            <span>Push to DB</span>
          </button>

          {/* Export Button */}
          <button
            onClick={() => setActiveModal('csv-export')}
            className="hidden md:flex items-center gap-1.5 px-space-2.5 py-1.5 bg-surface-container-low hover:bg-surface-container-high text-on-surface border border-outline-variant/40 text-body-sm transition-colors"
            type="button"
            title="Export Cleaned Dataset"
          >
            <span className="material-symbols-outlined text-[16px]">download</span>
            <span>Export</span>
          </button>

          {/* Copilot AI Button */}
          <button
            onClick={() => setIsAiDrawerOpen(true)}
            className="flex items-center gap-1.5 px-space-3 py-1.5 bg-primary text-on-primary font-bold text-xs hover:bg-primary-fixed-dim transition-all shadow-sm active:scale-95"
            type="button"
          >
            <span className="material-symbols-outlined text-[16px]">smart_toy</span>
            <span>AI Analyst</span>
          </button>
        </div>
      </div>

      {/* Sub Pipeline Progression Bar */}
      <div className="h-8 px-space-4 bg-surface-container-lowest border-t border-outline-variant/20 flex items-center gap-space-4 overflow-x-auto text-body-sm font-data-mono">
        <button
          onClick={() => setCurrentView('schema-detection')}
          className={`flex items-center gap-1.5 shrink-0 ${currentView === 'schema-detection' ? 'text-primary font-bold' : 'text-tertiary hover:text-on-surface'}`}
        >
          <span className="material-symbols-outlined text-[14px]">schema</span>
          <span className="font-label-caps uppercase text-[10px]">1: Schema Detection</span>
        </button>

        <span className="text-outline-variant/50">/</span>

        <button
          onClick={() => setCurrentView('quality-and-audit')}
          className={`flex items-center gap-1.5 shrink-0 ${currentView === 'quality-and-audit' ? 'text-primary font-bold' : 'text-tertiary hover:text-on-surface'}`}
        >
          <span className="material-symbols-outlined text-[14px]">verified</span>
          <span className="font-label-caps uppercase text-[10px]">2: Quality & Cleaning</span>
        </button>

        <span className="text-outline-variant/50">/</span>

        <button
          onClick={() => setCurrentView('insights-explorer')}
          className={`flex items-center gap-1.5 shrink-0 ${currentView === 'insights-explorer' ? 'text-primary font-bold' : 'text-tertiary hover:text-on-surface'}`}
        >
          <span className="material-symbols-outlined text-[14px]">analytics</span>
          <span className="font-label-caps uppercase text-[10px]">3: Stats & Correlations</span>
        </button>

        <span className="text-outline-variant/50">/</span>

        <button
          onClick={() => setCurrentView('visualizations')}
          className={`flex items-center gap-1.5 shrink-0 ${currentView === 'visualizations' ? 'text-primary font-bold' : 'text-tertiary hover:text-on-surface'}`}
        >
          <span className="material-symbols-outlined text-[14px]">monitoring</span>
          <span className="font-label-caps uppercase text-[10px]">4: Visualizations</span>
        </button>

        <span className="text-outline-variant/50">/</span>

        <button
          onClick={() => setCurrentView('tabular-explorer')}
          className={`flex items-center gap-1.5 shrink-0 ${currentView === 'tabular-explorer' ? 'text-primary font-bold' : 'text-tertiary hover:text-on-surface'}`}
        >
          <span className="material-symbols-outlined text-[14px]">table_chart</span>
          <span className="font-label-caps uppercase text-[10px]">5: Data Explorer</span>
        </button>
      </div>
    </header>
  );
};

export default Header;
