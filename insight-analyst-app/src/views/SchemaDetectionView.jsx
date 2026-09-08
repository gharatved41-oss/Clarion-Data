import React, { useState, useMemo } from 'react';
import { useTelemetry } from '../context/TelemetryContext';

export const SchemaDetectionView = () => {
  const { metadata, records, schemaData, analysisData, isLoading, error, setCurrentView, refreshActiveDataset } = useTelemetry();
  const [selectedColumnName, setSelectedColumnName] = useState(null);
  const [isLocked, setIsLocked] = useState(false);

  // Extract columns from live backend schemaData or fallback
  const columns = useMemo(() => {
    if (schemaData && schemaData.columns && schemaData.columns.length > 0) {
      return schemaData.columns.map(c => ({
        id: c.name,
        name: c.name,
        type: c.type,
        original_dtype: c.original_dtype,
        confidence: c.confidence ? Math.round(c.confidence * 100) : 95,
        nulls: c.null_count || 0,
        distinct: c.unique_count || 0,
        status: (c.null_count > 0) ? 'HAS_NULLS' : 'VALID',
      }));
    }
    return [];
  }, [schemaData]);

  // Selected column profile from live schema + live analysisData
  const activeColumnName = selectedColumnName || (columns[0]?.name) || null;
  
  const selectedColumn = useMemo(() => {
    const col = columns.find(c => c.name === activeColumnName) || columns[0] || null;
    if (!col) return null;

    const numStats = analysisData?.numeric_analysis?.[col.name] || {};
    const catStats = analysisData?.categorical_analysis?.[col.name] || {};
    const dtStats = analysisData?.datetime_analysis?.[col.name] || {};
    const txtStats = analysisData?.text_analysis?.[col.name] || {};

    return {
      ...col,
      min: numStats.min ?? dtStats.min_date ?? '—',
      max: numStats.max ?? dtStats.max_date ?? '—',
      mean: numStats.mean ? Number(numStats.mean).toFixed(2) : (txtStats.avg_char_length ? `${txtStats.avg_char_length.toFixed(1)} chars` : '—'),
      median: numStats.median ? Number(numStats.median).toFixed(2) : '—',
      std: numStats.std ? Number(numStats.std).toFixed(2) : '—',
      skewness: numStats.skewness ? Number(numStats.skewness).toFixed(3) : '—',
      histogram: numStats.histogram || [],
      top_categories: catStats.top_categories || [],
    };
  }, [columns, activeColumnName, analysisData]);

  // Dynamic preview headers
  const previewHeaders = useMemo(() => {
    if (records.length > 0) {
      return Object.keys(records[0]);
    }
    return [];
  }, [records]);

  if (isLoading && columns.length === 0) {
    return (
      <div className="p-8 bg-surface-container-low border border-outline-variant/30 flex flex-col items-center justify-center gap-3 font-data-mono">
        <span className="material-symbols-outlined text-4xl text-primary animate-spin">progress_activity</span>
        <span className="text-sm font-semibold text-on-surface">Running Automatic Column Type Inferences...</span>
        <span className="text-xs text-outline">Profiling data types, null ratios, and cardinality</span>
      </div>
    );
  }

  if (error && columns.length === 0) {
    return (
      <div className="p-6 bg-error-container/20 border border-error/50 text-error flex flex-col gap-3 font-data-mono">
        <div className="flex items-center gap-2 font-bold text-sm">
          <span className="material-symbols-outlined">error</span>
          <span>Failed to load dataset schema</span>
        </div>
        <p className="text-xs">{error}</p>
        <button
          onClick={refreshActiveDataset}
          className="self-start px-3 py-1.5 bg-error text-on-error text-xs font-bold"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div className="w-full flex flex-col gap-4 font-body-md select-none">
      {/* Top Banner */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-4 bg-surface-container-low border border-outline-variant/30">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-primary-container border border-primary/40 flex items-center justify-center">
            <span className="material-symbols-outlined text-primary text-xl">schema</span>
          </div>
          <div>
            <h1 className="font-headline-md text-base font-semibold text-on-surface">
              Dataset Schema Detection & Type Profiler
            </h1>
            <p className="text-xs font-data-mono text-outline">
              Target: {metadata.filename} • {columns.length} Columns Detected • {metadata.rows.toLocaleString()} Rows
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsLocked(!isLocked)}
            className={`flex items-center gap-1.5 px-3 py-1.5 border text-xs font-headline-sm transition-colors ${
              isLocked
                ? 'bg-tertiary-container border-tertiary text-tertiary font-bold'
                : 'bg-surface-container border-outline-variant hover:border-outline text-on-surface'
            }`}
          >
            <span className="material-symbols-outlined text-[16px]">
              {isLocked ? 'lock' : 'lock_open'}
            </span>
            <span>{isLocked ? 'Schema Locked' : 'Lock Schema'}</span>
          </button>

          <button
            onClick={() => setCurrentView('quality-and-audit')}
            className="flex items-center gap-1.5 px-4 py-1.5 bg-primary text-on-primary font-semibold text-xs font-headline-sm hover:bg-primary-fixed-dim transition-colors"
          >
            <span>Proceed to Quality Audit</span>
            <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
          </button>
        </div>
      </div>

      {/* Main Grid: Columns Table (Left) + Detail Profiler (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Columns Profiler List (2 cols on large screen) */}
        <div className="lg:col-span-2 bg-surface-container-low border border-outline-variant/30 flex flex-col">
          <div className="h-10 px-4 bg-surface-container-high border-b border-outline-variant/30 flex items-center justify-between font-label-caps text-xs text-outline uppercase tracking-wider">
            <span>Detected Column Inferences</span>
            <span>Confidence & Health</span>
          </div>

          <div className="overflow-x-auto max-h-[500px]">
            <table className="w-full text-left font-data-mono text-xs border-collapse">
              <thead className="bg-surface-container-lowest text-outline border-b border-outline-variant/20 sticky top-0 z-10">
                <tr>
                  <th className="p-2.5">Column Identifier</th>
                  <th className="p-2.5">Inferred Type</th>
                  <th className="p-2.5">Null Count</th>
                  <th className="p-2.5">Distinct</th>
                  <th className="p-2.5">Confidence</th>
                  <th className="p-2.5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/20">
                {columns.map((col) => {
                  const isSelected = activeColumnName === col.name;
                  return (
                    <tr
                      key={col.name}
                      onClick={() => setSelectedColumnName(col.name)}
                      className={`cursor-pointer transition-colors ${
                        isSelected ? 'bg-primary-container/40 border-l-2 border-primary' : 'hover:bg-surface-container'
                      }`}
                    >
                      <td className="p-2.5 font-semibold text-on-surface flex items-center gap-2">
                        <span className="material-symbols-outlined text-[14px] text-outline">
                          {col.type === 'numeric' ? 'tag' : col.type === 'datetime' ? 'schedule' : col.type === 'identifier' ? 'key' : 'abc'}
                        </span>
                        <span className="truncate max-w-[150px]">{col.name}</span>
                      </td>

                      <td className="p-2.5">
                        <span className={`px-2 py-0.5 text-[11px] font-bold uppercase border ${
                          col.type === 'numeric' ? 'bg-secondary-container/30 border-secondary/40 text-secondary' :
                          col.type === 'datetime' ? 'bg-tertiary-container/30 border-tertiary/40 text-tertiary' :
                          col.type === 'identifier' ? 'bg-surface-container border-outline/40 text-outline' :
                          'bg-primary-container/30 border-primary/40 text-primary'
                        }`}>
                          {col.type}
                        </span>
                        <span className="ml-1.5 text-[10px] text-outline">({col.original_dtype})</span>
                      </td>

                      <td className="p-2.5">
                        {col.nulls > 0 ? (
                          <span className="text-anomaly font-bold">
                            {col.nulls} ({metadata.rows ? ((col.nulls / metadata.rows) * 100).toFixed(1) : 0}%)
                          </span>
                        ) : (
                          <span className="text-tertiary font-semibold">0 (0%)</span>
                        )}
                      </td>

                      <td className="p-2.5 text-on-surface">{col.distinct.toLocaleString()}</td>

                      <td className="p-2.5">
                        <div className="flex items-center gap-1.5">
                          <div className="w-12 bg-surface-container-lowest h-1.5 overflow-hidden">
                            <div className="bg-primary h-full" style={{ width: `${col.confidence}%` }}></div>
                          </div>
                          <span className="text-[10px] text-outline">{col.confidence}%</span>
                        </div>
                      </td>

                      <td className="p-2.5 text-right">
                        <button
                          type="button"
                          onClick={(e) => { e.stopPropagation(); setSelectedColumnName(col.name); }}
                          className="px-2 py-1 bg-surface-container hover:bg-surface-container-highest text-[11px] text-primary"
                        >
                          Inspect
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Column Detail Inspector (Right Column) */}
        {selectedColumn && (
          <div className="bg-surface-container-low border border-outline-variant/30 flex flex-col p-4 gap-4 font-data-mono">
            <div className="border-b border-outline-variant/30 pb-3">
              <span className="font-label-caps text-[10px] text-outline uppercase block">Selected Column Inspector</span>
              <h2 className="font-headline-md text-lg font-bold text-primary mt-1 truncate">{selectedColumn.name}</h2>
              <span className="text-xs text-secondary capitalize">{selectedColumn.type} ({selectedColumn.original_dtype})</span>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div className="p-2.5 bg-surface-container-lowest border border-outline-variant/30">
                <span className="text-[10px] text-outline uppercase block">Null Values</span>
                <span className="text-sm font-bold text-on-surface">{selectedColumn.nulls.toLocaleString()}</span>
              </div>
              <div className="p-2.5 bg-surface-container-lowest border border-outline-variant/30">
                <span className="text-[10px] text-outline uppercase block">Distinct Count</span>
                <span className="text-sm font-bold text-on-surface">{selectedColumn.distinct.toLocaleString()}</span>
              </div>
              <div className="p-2.5 bg-surface-container-lowest border border-outline-variant/30">
                <span className="text-[10px] text-outline uppercase block">Min Value</span>
                <span className="text-xs font-bold text-on-surface truncate block" title={String(selectedColumn.min)}>
                  {String(selectedColumn.min)}
                </span>
              </div>
              <div className="p-2.5 bg-surface-container-lowest border border-outline-variant/30">
                <span className="text-[10px] text-outline uppercase block">Max Value</span>
                <span className="text-xs font-bold text-on-surface truncate block" title={String(selectedColumn.max)}>
                  {String(selectedColumn.max)}
                </span>
              </div>
            </div>

            {/* Distribution Representation */}
            {selectedColumn.histogram && selectedColumn.histogram.length > 0 ? (
              <div className="flex flex-col gap-2 pt-2 border-t border-outline-variant/20">
                <span className="text-xs font-label-caps text-outline uppercase">Distribution Histogram</span>
                <div className="h-28 bg-surface-container-lowest border border-outline-variant/40 p-2 flex items-end gap-1 justify-between">
                  {selectedColumn.histogram.map((bin, idx) => {
                    const maxCount = Math.max(...selectedColumn.histogram.map(b => b.count || 0), 1);
                    const pct = Math.max(10, Math.round(((bin.count || 0) / maxCount) * 100));
                    return (
                      <div key={idx} className="flex-1 flex flex-col items-center gap-1 group relative" title={`${bin.bin_start.toFixed(1)} - ${bin.bin_end.toFixed(1)}: ${bin.count}`}>
                        <div
                          style={{ height: `${pct}%` }}
                          className="w-full bg-primary/70 hover:bg-primary transition-all"
                        ></div>
                        <span className="text-[8px] text-outline">B{idx + 1}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : selectedColumn.top_categories && selectedColumn.top_categories.length > 0 ? (
              <div className="flex flex-col gap-1.5 pt-2 border-t border-outline-variant/20">
                <span className="text-xs font-label-caps text-outline uppercase">Top Frequencies</span>
                <div className="flex flex-col gap-1 text-xs">
                  {selectedColumn.top_categories.slice(0, 4).map((cat, idx) => (
                    <div key={idx} className="flex items-center justify-between p-1 bg-surface-container-lowest">
                      <span className="truncate max-w-[120px]">{cat.category}</span>
                      <span className="text-outline">{cat.count} ({cat.percentage}%)</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : null}

            <div className="p-3 bg-surface-container-lowest border border-outline-variant/30 text-[11px] text-outline leading-relaxed">
              <span className="text-on-surface font-semibold block mb-1">Statistical Assessment:</span>
              Mean: {selectedColumn.mean} • Median: {selectedColumn.median} • Skewness: {selectedColumn.skewness}
            </div>
          </div>
        )}
      </div>

      {/* Raw Data Preview Grid (Bottom) */}
      <div className="bg-surface-container-low border border-outline-variant/30 flex flex-col">
        <div className="h-10 px-4 bg-surface-container-high border-b border-outline-variant/30 flex items-center justify-between font-label-caps text-xs text-outline uppercase tracking-wider">
          <span>First {Math.min(8, records.length)} Sample Rows (Live Data Preview)</span>
          <span>Read-Only Buffer</span>
        </div>
        <div className="overflow-x-auto max-h-72">
          {records.length > 0 ? (
            <table className="w-full text-left font-data-mono text-xs border-collapse">
              <thead className="bg-surface-container-lowest text-outline border-b border-outline-variant/20 sticky top-0">
                <tr>
                  {previewHeaders.map((header) => (
                    <th key={header} className="p-2 border-r border-outline-variant/20 whitespace-nowrap">
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/20 text-on-surface">
                {records.slice(0, 8).map((r, rowIdx) => (
                  <tr key={rowIdx} className="hover:bg-surface-container">
                    {previewHeaders.map((header) => (
                      <td key={header} className="p-2 border-r border-outline-variant/20 whitespace-nowrap">
                        {r[header] !== null && r[header] !== undefined ? String(r[header]) : <span className="text-outline italic">null</span>}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-6 text-center text-xs text-outline">
              No preview rows returned for dataset {metadata.filename}.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SchemaDetectionView;
