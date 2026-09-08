import React, { useState } from 'react';
import { useTelemetry } from '../../context/TelemetryContext';

export const TelemetryRibbon = () => {
  const {
    activeDomain,
    activeCohort,
    setActiveCohort,
    dateRange,
    setDateRange,
    selectedCurrency,
    setSelectedCurrency,
    setActiveModal,
    setIsAiDrawerOpen,
    metadata
  } = useTelemetry();

  const [isCohortOpen, setIsCohortOpen] = useState(false);
  const [isDateOpen, setIsDateOpen] = useState(false);

  const cohorts = [
    "Enterprise Tier (>500 seats)",
    "Mid-Market (50-500 seats)",
    "Starter Tier (<50 seats)",
    "All Active Cohorts"
  ];

  const dateRanges = [
    "Jan 01, 2026 – Sep 30, 2026",
    "Q3 2026 (Jul 01 – Sep 30)",
    "Trailing 12 Months (TTM)",
    "Full Fiscal Year 2025-2026"
  ];

  return (
    <div className="w-full flex flex-col font-data-mono print:hidden">
      {/* 1. Pipeline Telemetry Ribbon */}
      <div className="w-full bg-surface-container-lowest border-b border-outline-variant/30 px-space-4 py-2 flex flex-wrap items-center justify-between gap-4 text-body-sm">
        <div className="flex items-center gap-2 overflow-x-auto">
          <div className="flex items-center gap-1.5 px-2 py-0.5 bg-tertiary-container/60 border border-tertiary/40 text-tertiary">
            <span className="material-symbols-outlined text-[14px]">check</span>
            <span className="font-label-caps text-[10px] uppercase font-bold">1: SCHEMA (VALIDATED)</span>
          </div>
          <span className="text-outline-variant/40">›</span>
          <div className="flex items-center gap-1.5 px-2 py-0.5 bg-tertiary-container/60 border border-tertiary/40 text-tertiary">
            <span className="material-symbols-outlined text-[14px]">check</span>
            <span className="font-label-caps text-[10px] uppercase font-bold">2: QUALITY ({metadata.healthScore} HEALTH)</span>
          </div>
          <span className="text-outline-variant/40">›</span>
          <div className="flex items-center gap-1.5 px-2 py-0.5 bg-tertiary-container/60 border border-tertiary/40 text-tertiary">
            <span className="material-symbols-outlined text-[14px]">check</span>
            <span className="font-label-caps text-[10px] uppercase font-bold">3: AUTO-CLEAN (LOSSLESS)</span>
          </div>
          <span className="text-outline-variant/40">›</span>
          <div className="flex items-center gap-1.5 px-2 py-0.5 bg-tertiary-container/60 border border-tertiary/40 text-tertiary">
            <span className="material-symbols-outlined text-[14px]">check</span>
            <span className="font-label-caps text-[10px] uppercase font-bold">4: INFERENCE (18 HYPOTHESES)</span>
          </div>
          <span className="text-outline-variant/40">›</span>
          <div className="flex items-center gap-1.5 px-2.5 py-0.5 bg-primary-container border border-primary text-primary font-semibold shadow-[0_0_12px_rgba(196,193,251,0.15)]">
            <span className="w-2 h-2 bg-primary inline-block animate-pulse"></span>
            <span className="font-label-caps text-[10px] uppercase tracking-wider font-bold">5: SYNTHESIS ACTIVE (100% COMPLETE)</span>
          </div>
        </div>

        <div className="flex items-center gap-3 text-outline text-body-sm">
          <span className="flex items-center gap-1">
            <span className="text-on-surface-variant font-medium">Domain:</span>
            <span className="text-secondary font-semibold">{activeDomain}</span>
            <span className="px-1.5 py-0.2 bg-secondary-container/20 text-secondary text-[10px] border border-secondary/30">
              {metadata.confidence}% Conf
            </span>
          </span>
          <span className="text-outline-variant/40">|</span>
          <span className="text-on-surface-variant">{metadata.modelEngine}</span>
        </div>
      </div>

      {/* 2. Operational Control & Filter Bar */}
      <div className="w-full bg-surface-container-low border-b border-outline-variant/30 px-space-4 py-2.5 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          {/* Date Range Selector */}
          <div className="relative">
            <button
              onClick={() => { setIsDateOpen(!isDateOpen); setIsCohortOpen(false); }}
              className="flex items-center bg-surface-container-lowest border border-outline-variant/40 px-2.5 py-1 text-body-sm font-data-mono gap-2 text-on-surface hover:border-outline"
            >
              <span className="material-symbols-outlined text-[15px] text-outline">calendar_today</span>
              <span className="text-outline text-body-sm">WINDOW:</span>
              <span className="font-semibold text-on-surface">{dateRange}</span>
              <span className="material-symbols-outlined text-[14px] text-outline ml-1">arrow_drop_down</span>
            </button>
            {isDateOpen && (
              <div className="absolute left-0 mt-1 w-64 bg-surface-container-high border border-outline-variant/60 shadow-2xl z-50 py-1">
                {dateRanges.map((range) => (
                  <button
                    key={range}
                    onClick={() => { setDateRange(range); setIsDateOpen(false); }}
                    className={`w-full px-3 py-1.5 text-left text-xs font-data-mono hover:bg-primary-container/40 ${dateRange === range ? 'text-primary font-bold bg-primary-container/20' : 'text-on-surface'}`}
                  >
                    {range}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Cohort Segment Dropdown */}
          <div className="relative">
            <button
              onClick={() => { setIsCohortOpen(!isCohortOpen); setIsDateOpen(false); }}
              className="flex items-center bg-surface-container-lowest border border-outline-variant/40 px-2.5 py-1 text-body-sm font-data-mono gap-2 text-on-surface hover:border-outline"
            >
              <span className="material-symbols-outlined text-[15px] text-outline">group_work</span>
              <span className="text-outline text-body-sm">COHORT:</span>
              <span className="text-secondary font-semibold">{activeCohort}</span>
              <span className="material-symbols-outlined text-[14px] text-outline ml-1">arrow_drop_down</span>
            </button>
            {isCohortOpen && (
              <div className="absolute left-0 mt-1 w-64 bg-surface-container-high border border-outline-variant/60 shadow-2xl z-50 py-1">
                {cohorts.map((c) => (
                  <button
                    key={c}
                    onClick={() => { setActiveCohort(c); setIsCohortOpen(false); }}
                    className={`w-full px-3 py-1.5 text-left text-xs font-data-mono hover:bg-primary-container/40 ${activeCohort === c ? 'text-secondary font-bold bg-secondary-container/20' : 'text-on-surface'}`}
                  >
                    {c}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Currency Switcher */}
          <div className="flex items-center bg-surface-container-lowest border border-outline-variant/40 px-2 py-1 text-body-sm font-data-mono gap-1 text-on-surface">
            <span className="material-symbols-outlined text-[15px] text-outline">attach_money</span>
            <span className="text-on-surface font-semibold">{selectedCurrency}</span>
          </div>

          {/* Filter Matrix Trigger */}
          <button
            onClick={() => alert("Filter Matrix active: Filtering by Subscription Tier in ('Enterprise', 'Mid-Market') AND Utilization > 0.70")}
            className="flex items-center gap-1.5 px-3 py-1 bg-surface-container border border-outline-variant/40 hover:border-outline text-on-surface text-body-sm font-headline-sm transition-colors"
          >
            <span className="material-symbols-outlined text-[15px] text-primary">tune</span>
            <span>Filter Matrix</span>
            <span className="px-1 text-[10px] bg-primary/20 text-primary font-semibold">3 Active</span>
          </button>
        </div>

        {/* Quick Actions Action Bar */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveModal('supabase-sync')}
            className="flex items-center gap-1.5 px-3 py-1 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-body-sm font-headline-sm font-semibold transition-colors"
            title="Push dataset directly into Supabase database"
          >
            <span className="material-symbols-outlined text-[15px]">database</span>
            <span>Push to DB</span>
          </button>
          <button
            onClick={() => setActiveModal('csv-export')}
            className="flex items-center gap-1.5 px-3 py-1 bg-surface-container-lowest border border-outline-variant/40 hover:bg-surface-container text-on-surface text-body-sm font-headline-sm transition-colors"
          >
            <span className="material-symbols-outlined text-[15px]">file_download</span>
            <span>Export CSV</span>
          </button>
          <button
            onClick={() => window.print()}
            className="flex items-center gap-1.5 px-3 py-1 bg-surface-container-lowest border border-outline-variant/40 hover:bg-surface-container text-on-surface text-body-sm font-headline-sm transition-colors"
          >
            <span className="material-symbols-outlined text-[15px]">picture_as_pdf</span>
            <span>PDF Memo</span>
          </button>
          <button
            onClick={() => setIsAiDrawerOpen(true)}
            className="flex items-center gap-1.5 px-3.5 py-1 bg-primary-container hover:bg-primary-container/90 text-primary border border-primary/50 text-body-sm font-headline-sm font-semibold tracking-wide shadow-sm transition-colors"
          >
            <span className="material-symbols-outlined text-[16px] text-tertiary">psychology</span>
            <span>AI Deep Dive</span>
          </button>
        </div>
      </div>
    </div>
  );
};
