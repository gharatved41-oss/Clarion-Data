import React from 'react';
import { useTelemetry } from '../context/TelemetryContext';

export const SettingsTolerancesView = () => {
  const {
    iqrThreshold,
    setIqrThreshold,
    alphaSignificance,
    setAlphaSignificance,
    maxMissingTolerance,
    setMaxMissingTolerance,
    zScoreThreshold,
    setZScoreThreshold,
    outlierCount,
    setActiveModal,
    theme,
    setTheme,
    addAuditLog
  } = useTelemetry();

  const handleSelectTheme = (newTheme) => {
    setTheme(newTheme);
    addAuditLog("THEME_CHANGE", `Configured UI theme to ${newTheme.toUpperCase()} mode via Settings`);
  };

  return (
    <div className="w-full flex flex-col gap-4 font-body-md select-none font-data-mono">
      {/* Top Banner */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-4 bg-surface-container-low border border-outline-variant/30 font-body-md">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-primary-container border border-primary/40 flex items-center justify-center">
            <span className="material-symbols-outlined text-primary text-xl">tune</span>
          </div>
          <div>
            <h1 className="font-headline-md text-base font-semibold text-on-surface">
              Statistical Tolerances & Workspace Preferences
            </h1>
            <p className="text-xs font-data-mono text-outline">
              Tune Tukey Fences, hypothesis alpha thresholds, live anomaly sensitivity parameters, and visual theme.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveModal('iqr-propagation')}
            className="flex items-center gap-1.5 px-4 py-1.5 bg-primary text-on-primary font-semibold text-xs font-headline-sm hover:bg-primary-fixed-dim transition-colors"
          >
            <span className="material-symbols-outlined text-[16px]">sync</span>
            <span>Propagate to Models</span>
          </button>
        </div>
      </div>

      {/* Theme & Display Mode Section */}
      <div className="bg-surface-container-low border border-outline-variant/30 p-5 flex flex-col gap-4">
        <div className="flex items-center justify-between border-b border-outline-variant/30 pb-2">
          <span className="font-label-caps text-xs text-outline uppercase tracking-wider font-bold">
            Workspace Visual Theme & Appearance
          </span>
          <span className="px-2 py-0.5 bg-primary-container text-primary font-bold text-xs">
            Active: {theme === 'dark' ? 'Obsidian Dark' : 'Technical Light'}
          </span>
        </div>

        <p className="text-xs text-outline leading-relaxed">
          Select your preferred visual mode for operational telemetry, tabular analysis, and statistical charts.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Dark Mode Card */}
          <button
            type="button"
            onClick={() => handleSelectTheme('dark')}
            className={`p-4 text-left border transition-all flex flex-col gap-3 ${
              theme === 'dark'
                ? 'bg-surface-container-high border-primary ring-1 ring-primary'
                : 'bg-surface-container-lowest border-outline-variant/40 hover:border-outline'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-amber-400 text-xl">dark_mode</span>
                <span className="text-sm font-bold text-on-surface">Obsidian Dark Mode</span>
              </div>
              {theme === 'dark' && (
                <span className="material-symbols-outlined text-primary text-base">check_circle</span>
              )}
            </div>
            <p className="text-xs text-outline leading-relaxed">
              Deep telemetry dark palette (#0b1326) engineered for low-light environments, high-contrast glow indicators, and reduced eye strain during long analytical sessions.
            </p>
            {/* Miniature preview palette */}
            <div className="flex items-center gap-1.5 pt-2">
              <span className="w-5 h-5 bg-[#0b1326] border border-[#1e2749]" title="Surface"></span>
              <span className="w-5 h-5 bg-[#171f33] border border-[#1e2749]" title="Container"></span>
              <span className="w-5 h-5 bg-[#c4c1fb]" title="Primary Lavender"></span>
              <span className="w-5 h-5 bg-[#93ccff]" title="Secondary Cyan"></span>
              <span className="w-5 h-5 bg-[#68dba9]" title="Tertiary Emerald"></span>
            </div>
          </button>

          {/* Light Mode Card */}
          <button
            type="button"
            onClick={() => handleSelectTheme('light')}
            className={`p-4 text-left border transition-all flex flex-col gap-3 ${
              theme === 'light'
                ? 'bg-surface-container-high border-primary ring-1 ring-primary'
                : 'bg-surface-container-lowest border-outline-variant/40 hover:border-outline'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-xl">light_mode</span>
                <span className="text-sm font-bold text-on-surface">Technical Light Mode</span>
              </div>
              {theme === 'light' && (
                <span className="material-symbols-outlined text-primary text-base">check_circle</span>
              )}
            </div>
            <p className="text-xs text-outline leading-relaxed">
              Clean slate-white palette (#f8fafc) designed for daytime readability, bright conference room projections, and formal executive print memos.
            </p>
            {/* Miniature preview palette */}
            <div className="flex items-center gap-1.5 pt-2">
              <span className="w-5 h-5 bg-[#f8fafc] border border-[#cbd5e1]" title="Surface"></span>
              <span className="w-5 h-5 bg-[#edf2f7] border border-[#cbd5e1]" title="Container"></span>
              <span className="w-5 h-5 bg-[#4f46e5]" title="Primary Indigo"></span>
              <span className="w-5 h-5 bg-[#0284c7]" title="Secondary Sky"></span>
              <span className="w-5 h-5 bg-[#059669]" title="Tertiary Emerald"></span>
            </div>
          </button>
        </div>
      </div>

      {/* Main Settings Grid: Controls (Left 2 cols) + Live Simulation Impact (Right 1 col) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Sliders & Hyperparameter Controls */}
        <div className="lg:col-span-2 bg-surface-container-low border border-outline-variant/30 flex flex-col p-5 gap-6">
          <span className="font-label-caps text-xs text-outline uppercase tracking-wider font-bold border-b border-outline-variant/30 pb-2">
            Model Engine Parameters
          </span>

          {/* 1. IQR Multiplier Slider */}
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-bold text-on-surface">
                Tukey IQR Outlier Threshold Multiplier (k)
              </label>
              <span className="px-2 py-0.5 bg-primary-container text-primary font-bold text-xs">
                k = {iqrThreshold.toFixed(2)}
              </span>
            </div>
            <p className="text-xs text-outline leading-relaxed">
              Defines the boundary [Q1 - k*IQR, Q3 + k*IQR]. Standard outlier detection uses k=1.5; extreme anomaly isolation uses k=3.0.
            </p>
            <input
              type="range"
              min="1.0"
              max="3.0"
              step="0.1"
              value={iqrThreshold}
              onChange={(e) => setIqrThreshold(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-surface-container-lowest appearance-none cursor-pointer accent-primary"
            />
            <div className="flex justify-between text-[10px] text-outline">
              <span>k = 1.0 (Aggressive Filtering)</span>
              <span>k = 1.5 (Standard)</span>
              <span>k = 3.0 (Conservative / Extreme Only)</span>
            </div>
          </div>

          {/* 2. Alpha Significance Level */}
          <div className="flex flex-col gap-2 pt-4 border-t border-outline-variant/20">
            <div className="flex items-center justify-between">
              <label className="text-sm font-bold text-on-surface">
                Hypothesis Statistical Significance Threshold (Alpha α)
              </label>
              <span className="px-2 py-0.5 bg-secondary-container/30 text-secondary font-bold text-xs">
                α = {alphaSignificance}
              </span>
            </div>
            <p className="text-xs text-outline leading-relaxed">
              Maximum allowable p-value to reject null hypothesis H0 with Bonferroni-Holm family-wise error control.
            </p>
            <div className="flex items-center gap-3">
              {[0.01, 0.05, 0.10].map((val) => (
                <button
                  key={val}
                  onClick={() => setAlphaSignificance(val)}
                  className={`px-3 py-1 text-xs font-semibold border ${
                    alphaSignificance === val
                      ? 'bg-secondary text-on-secondary border-secondary font-bold'
                      : 'bg-surface-container-lowest text-on-surface border-outline-variant/40 hover:border-outline'
                  }`}
                >
                  α = {val} {val === 0.01 ? '(Strict 99%)' : val === 0.05 ? '(Standard 95%)' : '(Exploratory 90%)'}
                </button>
              ))}
            </div>
          </div>

          {/* 3. Z-Score Cutoff */}
          <div className="flex flex-col gap-2 pt-4 border-t border-outline-variant/20">
            <div className="flex items-center justify-between">
              <label className="text-sm font-bold text-on-surface">
                Gaussian Anomaly Z-Score Cutoff (σ)
              </label>
              <span className="px-2 py-0.5 bg-surface-container text-on-surface font-bold text-xs">
                {zScoreThreshold} σ
              </span>
            </div>
            <p className="text-xs text-outline leading-relaxed">
              Z-score threshold for single-variable univariate anomaly isolation.
            </p>
            <input
              type="range"
              min="2.0"
              max="4.0"
              step="0.5"
              value={zScoreThreshold}
              onChange={(e) => setZScoreThreshold(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-surface-container-lowest appearance-none cursor-pointer accent-secondary"
            />
          </div>
        </div>

        {/* Live Simulation Impact Card */}
        <div className="bg-surface-container-low border border-outline-variant/30 flex flex-col p-4 gap-4">
          <span className="font-label-caps text-xs text-outline uppercase tracking-wider font-bold border-b border-outline-variant/30 pb-2">
            Real-Time Parameter Impact Simulation
          </span>

          <div className="p-4 bg-surface-container-lowest border border-outline-variant/30 flex flex-col gap-3">
            <div className="flex justify-between items-center">
              <span className="text-xs text-outline">Active Outlier Rows:</span>
              <span className="text-lg font-bold text-anomaly">{outlierCount} rows</span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-xs text-outline">Dataset Clean Ratio:</span>
              <span className="text-lg font-bold text-tertiary">
                {((1 - outlierCount / 14290) * 100).toFixed(2)}%
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-xs text-outline">Forecasting CI Width:</span>
              <span className="text-xs font-bold text-secondary">
                ±{(4.2 * (iqrThreshold / 1.5)).toFixed(1)}%
              </span>
            </div>
          </div>

          <div className="p-3 bg-surface-container-lowest border border-outline-variant/30 text-xs text-outline leading-relaxed flex flex-col gap-1.5">
            <strong className="text-on-surface">Parameter Propagation:</strong>
            Adjusting `k` immediately shifts outlier detection in the Tabular Explorer, refines SARIMAX confidence intervals, and updates AI Copilot analytical bounds.
          </div>

          <button
            onClick={() => setActiveModal('iqr-propagation')}
            className="w-full py-2 bg-primary-container hover:bg-primary-container/80 text-primary border border-primary/40 font-semibold text-xs font-headline-sm transition-colors mt-auto"
          >
            Review & Lock Parameters (k = {iqrThreshold})
          </button>
        </div>
      </div>
    </div>
  );
};
