import React, { useState, useEffect } from 'react';
import { useTelemetry } from '../context/TelemetryContext';

export const ProcessingPipelineView = () => {
  const { setCurrentView } = useTelemetry();
  const [progress, setProgress] = useState(100);
  const [activeStage, setActiveStage] = useState(5);

  const logs = [
    "[13:42:01.002] [INIT] Ingesting binary dataset stream 'q3_financials_2026.csv' (4.8 MB)...",
    "[13:42:01.140] [ARROW] Zero-copy record batch initialized. 14,290 rows loaded into memory.",
    "[13:42:02.045] [SCHEMA] Validating 18 typed columns. Inferred Float64 (8), Utf8 (4), Timestamp (2), Int64 (4).",
    "[13:42:02.890] [AUDIT] Health Score computed: 98.6/100. 14 missing cells flagged in contract_mrr_usd.",
    "[13:42:03.412] [CLEAN] Auto-imputing median values for 14 records across cohort sub-groups.",
    "[13:42:04.110] [HYPOTHESIS] Spawning combinatorial search across 42 covariate pairs...",
    "[13:42:05.802] [STATS] Mann-Whitney U test on Seat Utilization vs Expansion: p = 0.000084 (Significant).",
    "[13:42:06.198] [STATS] Cox Proportional Hazard on Onboarding Tickets: Hazard Ratio = 4.81 (p = 0.0012).",
    "[13:42:07.014] [SARIMAX] Fitting SARIMAX(1,1,1)x(1,1,0)[12] on Monthly Recurring Revenue...",
    "[13:42:08.432] [SARIMAX] Model converged in 18 iterations. AIC: 1420.4, BIC: 1468.2. RMSE: 0.042.",
    "[13:42:09.110] [SYNTHESIS] Synthesizing executive narrative cards and dynamic KPI formula trees.",
    "[13:42:09.980] [SUCCESS] Pipeline execution complete in 8.98s. All 5 pipeline stages verified green."
  ];

  return (
    <div className="w-full flex flex-col gap-4 font-body-md select-none">
      {/* Top Banner */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-4 bg-surface-container-low border border-outline-variant/30">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-primary-container border border-primary/40 flex items-center justify-center">
            <span className="material-symbols-outlined text-primary text-xl">memory</span>
          </div>
          <div>
            <h1 className="font-headline-md text-base font-semibold text-on-surface">
              Statistical Analysis & Model Processing Engine
            </h1>
            <p className="text-xs font-data-mono text-outline">
              SARIMAX v4.18 • 18 Hypotheses Converged • Execution Time: 8.98s
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setCurrentView('visualizations')}
            className="flex items-center gap-1.5 px-4 py-1.5 bg-primary text-on-primary font-semibold text-xs font-headline-sm hover:bg-primary-fixed-dim transition-colors"
          >
            <span>View Intelligence Dashboard</span>
            <span className="material-symbols-outlined text-[16px]">monitoring</span>
          </button>
        </div>
      </div>

      {/* Compute Resource Telemetry Gauges */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 font-data-mono">
        <div className="p-3.5 bg-surface-container-low border border-outline-variant/30 flex flex-col gap-1">
          <span className="font-label-caps text-[10px] text-outline uppercase">CPU Parallel Threads</span>
          <div className="flex items-baseline justify-between mt-1">
            <span className="text-xl font-bold text-secondary">8 Cores</span>
            <span className="text-[10px] text-tertiary">94% Utilization</span>
          </div>
          <div className="w-full bg-surface-container-lowest h-1.5 mt-2">
            <div className="bg-secondary h-full" style={{ width: '94%' }}></div>
          </div>
        </div>

        <div className="p-3.5 bg-surface-container-low border border-outline-variant/30 flex flex-col gap-1">
          <span className="font-label-caps text-[10px] text-outline uppercase">Peak In-Memory Buffer</span>
          <div className="flex items-baseline justify-between mt-1">
            <span className="text-xl font-bold text-on-surface">148 MB</span>
            <span className="text-[10px] text-outline">Arrow Zero-Copy</span>
          </div>
          <div className="w-full bg-surface-container-lowest h-1.5 mt-2">
            <div className="bg-primary h-full" style={{ width: '28%' }}></div>
          </div>
        </div>

        <div className="p-3.5 bg-surface-container-low border border-outline-variant/30 flex flex-col gap-1">
          <span className="font-label-caps text-[10px] text-outline uppercase">SARIMAX AIC Score</span>
          <div className="flex items-baseline justify-between mt-1">
            <span className="text-xl font-bold text-tertiary">1420.4</span>
            <span className="text-[10px] text-tertiary">Converged</span>
          </div>
          <div className="w-full bg-surface-container-lowest h-1.5 mt-2">
            <div className="bg-tertiary h-full" style={{ width: '88%' }}></div>
          </div>
        </div>

        <div className="p-3.5 bg-surface-container-low border border-outline-variant/30 flex flex-col gap-1">
          <span className="font-label-caps text-[10px] text-outline uppercase">Hypothesis Discovery</span>
          <div className="flex items-baseline justify-between mt-1">
            <span className="text-xl font-bold text-primary">18 / 18</span>
            <span className="text-[10px] text-tertiary">4 High Significance</span>
          </div>
          <div className="w-full bg-surface-container-lowest h-1.5 mt-2">
            <div className="bg-primary h-full" style={{ width: '100%' }}></div>
          </div>
        </div>
      </div>

      {/* Terminal Log Stream + Stage Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Terminal Live Stream (2 cols) */}
        <div className="lg:col-span-2 bg-surface-container-lowest border border-outline-variant/40 flex flex-col">
          <div className="h-10 px-4 bg-surface-container-high border-b border-outline-variant/30 flex items-center justify-between font-label-caps text-xs text-outline uppercase tracking-wider">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 bg-tertiary inline-block animate-pulse"></span>
              <span className="text-on-surface">Telemetry Log Terminal (stdout/stderr)</span>
            </div>
            <span className="text-outline font-data-mono">Stream: Live</span>
          </div>

          <div className="p-4 font-data-mono text-xs text-on-surface-variant flex flex-col gap-1.5 max-h-96 overflow-y-auto leading-relaxed">
            {logs.map((log, index) => (
              <div
                key={index}
                className={`font-mono text-[11px] ${
                  log.includes('[SUCCESS]')
                    ? 'text-tertiary font-bold bg-tertiary-container/20 p-1'
                    : log.includes('[STATS]') || log.includes('[SARIMAX]')
                    ? 'text-secondary'
                    : log.includes('[CLEAN]') || log.includes('[AUDIT]')
                    ? 'text-primary'
                    : 'text-on-surface-variant'
                }`}
              >
                {log}
              </div>
            ))}
          </div>
        </div>

        {/* Pipeline Stage Checklist (1 col) */}
        <div className="bg-surface-container-low border border-outline-variant/30 flex flex-col p-4 gap-3 font-data-mono">
          <span className="font-label-caps text-[10px] text-outline uppercase block border-b border-outline-variant/30 pb-2">
            Execution Stage Matrix
          </span>

          <div className="flex flex-col gap-2.5 text-xs">
            <div className="p-2.5 bg-surface-container-lowest border border-tertiary/40 flex items-center justify-between">
              <div className="flex items-center gap-2 text-tertiary font-semibold">
                <span className="material-symbols-outlined text-sm">check_circle</span>
                <span>1. Arrow Ingestion</span>
              </div>
              <span className="text-[10px] text-outline">0.14s</span>
            </div>

            <div className="p-2.5 bg-surface-container-lowest border border-tertiary/40 flex items-center justify-between">
              <div className="flex items-center gap-2 text-tertiary font-semibold">
                <span className="material-symbols-outlined text-sm">check_circle</span>
                <span>2. Schema Validation</span>
              </div>
              <span className="text-[10px] text-outline">0.89s</span>
            </div>

            <div className="p-2.5 bg-surface-container-lowest border border-tertiary/40 flex items-center justify-between">
              <div className="flex items-center gap-2 text-tertiary font-semibold">
                <span className="material-symbols-outlined text-sm">check_circle</span>
                <span>3. Deterministic Clean</span>
              </div>
              <span className="text-[10px] text-outline">0.52s</span>
            </div>

            <div className="p-2.5 bg-surface-container-lowest border border-tertiary/40 flex items-center justify-between">
              <div className="flex items-center gap-2 text-tertiary font-semibold">
                <span className="material-symbols-outlined text-sm">check_circle</span>
                <span>4. Hypothesis & Stats</span>
              </div>
              <span className="text-[10px] text-outline">2.68s</span>
            </div>

            <div className="p-2.5 bg-surface-container-lowest border border-primary/50 flex items-center justify-between bg-primary-container/20">
              <div className="flex items-center gap-2 text-primary font-bold">
                <span className="material-symbols-outlined text-sm">check_circle</span>
                <span>5. SARIMAX Synthesis</span>
              </div>
              <span className="text-[10px] text-primary">4.75s</span>
            </div>
          </div>

          <div className="p-3 bg-surface-container-lowest border border-outline-variant/30 text-[11px] text-outline leading-relaxed mt-auto">
            Ready to inspect generated intelligence dashboards and explore hypothesis decomposition trees.
          </div>
        </div>
      </div>
    </div>
  );
};
