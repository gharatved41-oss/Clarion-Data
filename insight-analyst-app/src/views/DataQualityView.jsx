import React, { useState } from 'react';
import { useTelemetry } from '../context/TelemetryContext';
import api from '../services/api';

export const DataQualityView = () => {
  const {
    activeDatasetId,
    metadata,
    cleaningReport,
    qualityData,
    setCurrentView,
    refreshActiveDataset,
    addAuditLog
  } = useTelemetry();

  const [isCleaningRunning, setIsCleaningRunning] = useState(false);
  const [cleaningStatus, setCleaningStatus] = useState(null);

  const runPipeline = async () => {
    setIsCleaningRunning(true);
    setCleaningStatus(null);
    try {
      const report = await api.getCleaningReport(activeDatasetId, true);
      await refreshActiveDataset();
      addAuditLog("DATA_CLEANING_EXECUTED", `Forced reclean pass on '${activeDatasetId}'. Result: ${report.cleaned_row_count} rows.`);
      setCleaningStatus({
        success: true,
        message: `Cleaning pass complete: ${report.duplicates_removed} duplicates removed, ${report.missing_values_handled} missing values resolved, ${report.numeric_conversions + report.currency_conversions + report.percentage_conversions + report.date_conversions} type normalizations.`
      });
    } catch (err) {
      setCleaningStatus({
        success: false,
        message: `Cleaning pass failed: ${err.message || "Unknown error"}`
      });
    } finally {
      setIsCleaningRunning(false);
    }
  };

  const factors = qualityData?.factors || {
    completeness: 100,
    validity: 100,
    uniqueness: 100,
    consistency: 100
  };

  const totalConversions = (cleaningReport?.numeric_conversions || 0) +
    (cleaningReport?.currency_conversions || 0) +
    (cleaningReport?.percentage_conversions || 0) +
    (cleaningReport?.date_conversions || 0);

  return (
    <div className="w-full flex flex-col gap-4 font-body-md select-none font-data-mono">
      {/* Top Banner */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-4 bg-surface-container-low border border-outline-variant/30 font-body-md">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-tertiary-container border border-tertiary/40 flex items-center justify-center">
            <span className="material-symbols-outlined text-tertiary text-xl">verified</span>
          </div>
          <div>
            <h1 className="font-headline-md text-base font-semibold text-on-surface">
              Data Quality Audit & Automated Lossless Cleaning
            </h1>
            <p className="text-xs font-data-mono text-outline">
              Health Index: {qualityData ? qualityData.score : metadata.healthScore} / 100 (Grade {qualityData?.grade || 'A'}) • {cleaningReport?.missing_values_detected || 0} Missing Cells Flagged
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={runPipeline}
            disabled={isCleaningRunning}
            className="flex items-center gap-1.5 px-4 py-1.5 bg-secondary-container hover:bg-secondary text-on-secondary font-semibold text-xs font-headline-sm transition-colors disabled:opacity-50"
          >
            <span className={`material-symbols-outlined text-[16px] ${isCleaningRunning ? 'animate-spin' : ''}`}>
              {isCleaningRunning ? 'progress_activity' : 'auto_fix_high'}
            </span>
            <span>{isCleaningRunning ? 'Executing Cleaning...' : 'Run Auto-Clean Pass'}</span>
          </button>

          <button
            onClick={() => setCurrentView('visualizations')}
            className="flex items-center gap-1.5 px-4 py-1.5 bg-primary text-on-primary font-semibold text-xs font-headline-sm hover:bg-primary-fixed-dim transition-colors"
          >
            <span>View Visualizations</span>
            <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
          </button>
        </div>
      </div>

      {/* Cleaning Notice / Status Banner */}
      {cleaningStatus && (
        <div className={`p-3 text-xs flex items-center gap-2 border ${
          cleaningStatus.success
            ? 'bg-tertiary-container/30 border-tertiary/50 text-tertiary'
            : 'bg-error-container/30 border-error/50 text-error'
        }`}>
          <span className="material-symbols-outlined text-[18px]">
            {cleaningStatus.success ? 'check_circle' : 'error'}
          </span>
          <span>{cleaningStatus.message}</span>
        </div>
      )}

      {/* 4 Health Dimension Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <div className="p-3.5 bg-surface-container-low border border-outline-variant/30 flex flex-col gap-1">
          <span className="font-label-caps text-[10px] text-outline uppercase font-bold">Completeness Index</span>
          <div className="flex items-baseline justify-between mt-1">
            <span className="text-xl font-bold text-tertiary">{factors.completeness || 100}%</span>
            <span className="text-[10px] text-outline">{cleaningReport?.missing_values_detected || 0} missing cells</span>
          </div>
          <div className="w-full bg-surface-container-lowest h-1.5 mt-2 overflow-hidden">
            <div className="bg-tertiary h-full" style={{ width: `${factors.completeness || 100}%` }}></div>
          </div>
        </div>

        <div className="p-3.5 bg-surface-container-low border border-outline-variant/30 flex flex-col gap-1">
          <span className="font-label-caps text-[10px] text-outline uppercase font-bold">Validity & Type Integrity</span>
          <div className="flex items-baseline justify-between mt-1">
            <span className="text-xl font-bold text-tertiary">{factors.validity || 100}%</span>
            <span className="text-[10px] text-outline">{totalConversions} formatted cells</span>
          </div>
          <div className="w-full bg-surface-container-lowest h-1.5 mt-2 overflow-hidden">
            <div className="bg-tertiary h-full" style={{ width: `${factors.validity || 100}%` }}></div>
          </div>
        </div>

        <div className="p-3.5 bg-surface-container-low border border-outline-variant/30 flex flex-col gap-1">
          <span className="font-label-caps text-[10px] text-outline uppercase font-bold">Uniqueness & Deduplication</span>
          <div className="flex items-baseline justify-between mt-1">
            <span className="text-xl font-bold text-secondary">{factors.uniqueness || 100}%</span>
            <span className="text-[10px] text-outline">{cleaningReport?.duplicates_detected || 0} duplicate rows</span>
          </div>
          <div className="w-full bg-surface-container-lowest h-1.5 mt-2 overflow-hidden">
            <div className="bg-secondary h-full" style={{ width: `${factors.uniqueness || 100}%` }}></div>
          </div>
        </div>

        <div className="p-3.5 bg-surface-container-low border border-outline-variant/30 flex flex-col gap-1">
          <span className="font-label-caps text-[10px] text-outline uppercase font-bold">Consistency Index</span>
          <div className="flex items-baseline justify-between mt-1">
            <span className="text-xl font-bold text-tertiary">{factors.consistency || 100}%</span>
            <span className="text-[10px] text-outline">{metadata.rows} records validated</span>
          </div>
          <div className="w-full bg-surface-container-lowest h-1.5 mt-2 overflow-hidden">
            <div className="bg-tertiary h-full" style={{ width: `${factors.consistency || 100}%` }}></div>
          </div>
        </div>
      </div>

      {/* Two Column Section: Pipeline Actions Summary (Left) & Audit Log of Operations (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Cleaning Breakdown Summary Card */}
        <div className="bg-surface-container-low border border-outline-variant/30 flex flex-col">
          <div className="h-10 px-4 bg-surface-container-high border-b border-outline-variant/30 flex items-center justify-between font-label-caps text-xs text-outline uppercase tracking-wider font-bold">
            <span>Automated Cleaning Summary</span>
            <span className="text-tertiary">Verified Safe</span>
          </div>

          <div className="p-4 flex flex-col gap-3">
            <div className="flex items-center justify-between p-2.5 bg-surface-container-lowest border border-outline-variant/20">
              <span className="text-xs text-on-surface">Original Row Count:</span>
              <span className="text-xs font-bold text-outline">{cleaningReport?.original_row_count ?? metadata.rows}</span>
            </div>
            <div className="flex items-center justify-between p-2.5 bg-surface-container-lowest border border-outline-variant/20">
              <span className="text-xs text-on-surface">Cleaned Row Count:</span>
              <span className="text-xs font-bold text-tertiary">{cleaningReport?.cleaned_row_count ?? metadata.rows}</span>
            </div>
            <div className="flex items-center justify-between p-2.5 bg-surface-container-lowest border border-outline-variant/20">
              <span className="text-xs text-on-surface">Exact Duplicates Purged:</span>
              <span className="text-xs font-bold text-secondary">{cleaningReport?.duplicates_removed ?? 0}</span>
            </div>
            <div className="flex items-center justify-between p-2.5 bg-surface-container-lowest border border-outline-variant/20">
              <span className="text-xs text-on-surface">Missing Values Handled:</span>
              <span className="text-xs font-bold text-tertiary">{cleaningReport?.missing_values_handled ?? 0}</span>
            </div>
            <div className="flex items-center justify-between p-2.5 bg-surface-container-lowest border border-outline-variant/20">
              <span className="text-xs text-on-surface">Numeric & Currency Normalizations:</span>
              <span className="text-xs font-bold text-primary">{(cleaningReport?.numeric_conversions || 0) + (cleaningReport?.currency_conversions || 0)}</span>
            </div>
            <div className="flex items-center justify-between p-2.5 bg-surface-container-lowest border border-outline-variant/20">
              <span className="text-xs text-on-surface">Whitespace & Text Cleanups:</span>
              <span className="text-xs font-bold text-outline">{cleaningReport?.whitespace_fixes ?? 0}</span>
            </div>
          </div>
        </div>

        {/* Audit Trail of Specific Transformations */}
        <div className="bg-surface-container-low border border-outline-variant/30 flex flex-col">
          <div className="h-10 px-4 bg-surface-container-high border-b border-outline-variant/30 flex items-center justify-between font-label-caps text-xs text-outline uppercase tracking-wider font-bold">
            <span>Audit Trail of Transformations</span>
            <span className="text-xs font-normal">{(cleaningReport?.operations || []).length} Operations</span>
          </div>

          <div className="p-4 overflow-y-auto max-h-80 flex flex-col gap-2">
            {cleaningReport?.operations && cleaningReport.operations.length > 0 ? (
              cleaningReport.operations.map((op, idx) => (
                <div key={idx} className="p-2.5 bg-surface-container-lowest border border-outline-variant/20 text-xs flex flex-col gap-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-primary">{op.operation}</span>
                    <span className="text-[10px] text-tertiary">{op.affected_rows} rows affected</span>
                  </div>
                  <span className="text-outline text-[11px]">{op.details || op.method}</span>
                  {op.column && <span className="text-[10px] text-secondary font-semibold">Target: {op.column}</span>}
                </div>
              ))
            ) : (
              <div className="p-8 text-center text-xs text-outline">
                No cleaning transformations were required for this dataset.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataQualityView;
