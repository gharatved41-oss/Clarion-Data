import React, { useState, useMemo } from 'react';
import { useTelemetry } from '../context/TelemetryContext';
import { api } from '../services/api';

export const TabularExplorerView = () => {
  const { 
    records = [], 
    columnsList = [], 
    overview,
    activeDatasetId,
    setActiveModal, 
    iqrThreshold = 1.5, 
    outlierData,
    outlierCount = 0 
  } = useTelemetry();

  const [searchTerm, setSearchTerm] = useState('');
  const [onlyOutliers, setOnlyOutliers] = useState(false);
  const [sortField, setSortField] = useState('');
  const [sortAsc, setSortAsc] = useState(true);
  const [selectedRow, setSelectedRow] = useState(null);

  // Dynamic columns detection - strictly mapped to clean string names
  const detectedColumns = useMemo(() => {
    let raw = [];
    if (columnsList && columnsList.length > 0) {
      raw = columnsList;
    } else if (records && records.length > 0) {
      raw = Object.keys(records[0]);
    }
    return raw.map(c => (typeof c === 'string' ? c : (c && c.name) ? c.name : String(c)));
  }, [columnsList, records]);

  // Default sort to first column
  React.useEffect(() => {
    if (!sortField && detectedColumns.length > 0) {
      setSortField(detectedColumns[0]);
    }
  }, [detectedColumns, sortField]);

  const handleSort = (field) => {
    if (typeof field !== 'string') field = String(field);
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(true);
    }
  };

  const safeRecords = useMemo(() => {
    return Array.isArray(records) ? records : [];
  }, [records]);

  const filteredData = useMemo(() => {
    if (safeRecords.length === 0) return [];

    return safeRecords
      .filter((r) => {
        if (!r || typeof r !== 'object') return false;
        if (onlyOutliers && !r.is_outlier) return false;
        if (searchTerm) {
          const term = searchTerm.toLowerCase();
          return Object.values(r).some(val => 
            val !== null && val !== undefined && String(val).toLowerCase().includes(term)
          );
        }
        return true;
      })
      .sort((a, b) => {
        if (!sortField) return 0;
        let valA = a[sortField];
        let valB = b[sortField];
        if (valA === null || valA === undefined) return sortAsc ? 1 : -1;
        if (valB === null || valB === undefined) return sortAsc ? -1 : 1;
        if (typeof valA === 'string') {
          return sortAsc ? valA.localeCompare(String(valB)) : String(valB).localeCompare(valA);
        }
        return sortAsc ? Number(valA) - Number(valB) : Number(valB) - Number(valA);
      });
  }, [safeRecords, searchTerm, onlyOutliers, sortField, sortAsc]);

  const handleDownloadCsv = () => {
    const url = api.getExportUrl(activeDatasetId, 'csv');
    window.open(url, '_blank');
  };

  const totalRowsCount = overview?.rows || safeRecords.length;

  return (
    <div className="w-full flex flex-col gap-4 font-body-md select-none font-data-mono">
      {/* Top Banner & Modal Action Triggers */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-4 bg-surface-container-low border border-outline-variant/30 font-body-md">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-primary-container border border-primary/40 flex items-center justify-center">
            <span className="material-symbols-outlined text-primary text-xl">table_chart</span>
          </div>
          <div>
            <h1 className="font-headline-md text-base font-semibold text-on-surface">
              Tabular Data Explorer & Telemetry Matrix
            </h1>
            <p className="text-xs font-data-mono text-outline">
              Showing {filteredData.length.toLocaleString()} matching records of {totalRowsCount} total • {outlierCount} Outliers Flagged (IQR k={iqrThreshold})
            </p>
          </div>
        </div>

        {/* Action Triggers */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleDownloadCsv}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-surface-container hover:bg-surface-container-high border border-outline-variant/40 text-xs font-headline-sm transition-colors text-on-surface"
          >
            <span className="material-symbols-outlined text-[15px] text-primary">download</span>
            <span>Export Cleaned CSV</span>
          </button>

          <button
            onClick={() => setActiveModal('flagged-outliers')}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-anomaly/15 hover:bg-anomaly/30 border border-anomaly/50 text-xs font-headline-sm transition-colors text-anomaly font-semibold"
          >
            <span className="material-symbols-outlined text-[15px]">warning</span>
            <span>Outliers ({outlierCount})</span>
          </button>

          <button
            onClick={() => setActiveModal('iqr-propagation')}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-primary-container hover:bg-primary-container/80 text-primary border border-primary/40 text-xs font-headline-sm font-semibold transition-colors"
          >
            <span className="material-symbols-outlined text-[15px]">tune</span>
            <span>IQR k={iqrThreshold}</span>
          </button>
        </div>
      </div>

      {/* Control Filter Bar */}
      <div className="p-3 bg-surface-container-low border border-outline-variant/30 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex flex-wrap items-center gap-3">
          {/* Search Box */}
          <div className="flex items-center bg-surface-container-lowest border border-outline-variant/50 px-2.5 py-1 text-on-surface">
            <span className="material-symbols-outlined text-[16px] text-outline mr-1.5">search</span>
            <input
              type="text"
              placeholder="Search across all columns..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-transparent text-xs text-on-surface outline-none w-56 placeholder:text-outline"
            />
          </div>

          {/* Outliers Only Toggle */}
          <label className="flex items-center gap-1.5 cursor-pointer text-xs">
            <input
              type="checkbox"
              checked={onlyOutliers}
              onChange={(e) => setOnlyOutliers(e.target.checked)}
              className="w-4 h-4 bg-surface border border-outline-variant"
            />
            <span className={onlyOutliers ? 'text-anomaly font-bold' : 'text-outline'}>
              Show Outliers Only ({outlierCount})
            </span>
          </label>
        </div>

        <div className="text-outline text-[11px]">
          Click column to sort • Click row to inspect telemetry
        </div>
      </div>

      {/* Main High Density Dynamic Table */}
      <div className="bg-surface-container-low border border-outline-variant/30 flex flex-col overflow-hidden">
        <div className="overflow-x-auto max-h-[520px]">
          <table className="w-full text-left font-data-mono text-xs border-collapse">
            <thead className="bg-surface-container-high text-outline sticky top-0 z-10 border-b border-outline-variant/40">
              <tr>
                <th className="p-2.5 w-12 text-center border-r border-outline-variant/20">#</th>
                {detectedColumns.map((colName) => (
                  <th 
                    key={colName} 
                    onClick={() => handleSort(colName)} 
                    className="p-2.5 cursor-pointer hover:text-on-surface border-r border-outline-variant/20 whitespace-nowrap"
                  >
                    <div className="flex items-center gap-1">
                      <span>{colName}</span>
                      {sortField === colName && <span>{sortAsc ? '▲' : '▼'}</span>}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/20">
              {filteredData.length > 0 ? (
                filteredData.map((row, rowIdx) => {
                  const isSelected = selectedRow === row;
                  return (
                    <tr
                      key={row.row_id || row.id || rowIdx}
                      onClick={() => setSelectedRow(row)}
                      className={`cursor-pointer transition-colors ${
                        row.is_outlier
                          ? 'bg-anomaly/10 hover:bg-anomaly/20'
                          : isSelected
                          ? 'bg-primary-container/40 border-l-2 border-primary'
                          : 'hover:bg-surface-container'
                      }`}
                    >
                      <td className="p-2.5 border-r border-outline-variant/20 text-center text-outline">
                        {rowIdx + 1}
                      </td>
                      {detectedColumns.map((colName) => {
                        const val = row[colName];
                        const isNumeric = typeof val === 'number';
                        return (
                          <td 
                            key={colName} 
                            className={`p-2.5 border-r border-outline-variant/20 truncate max-w-[200px] ${
                              isNumeric ? 'text-right font-mono text-on-surface' : 'text-on-surface'
                            }`}
                            title={String(val ?? '')}
                          >
                            {val === null || val === undefined 
                              ? <span className="text-outline-variant/50">—</span> 
                              : isNumeric && !Number.isInteger(val)
                              ? val.toFixed(2)
                              : typeof val === 'object'
                              ? JSON.stringify(val)
                              : String(val)}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={detectedColumns.length + 1 || 1} className="p-8 text-center text-outline text-xs">
                    {safeRecords.length === 0
                      ? "Loading tabular dataset records from analytical engine..."
                      : "No matching records found for the active search filter."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Row Telemetry Detail Inspector */}
      {selectedRow && (
        <div className="p-4 bg-surface-container-low border border-outline-variant/30 flex flex-col gap-3">
          <div className="flex items-center justify-between border-b border-outline-variant/20 pb-2">
            <span className="font-label-caps text-xs text-primary uppercase font-bold">
              Record Telemetry Inspector
            </span>
            <button 
              onClick={() => setSelectedRow(null)}
              className="text-xs text-outline hover:text-on-surface"
            >
              Close
            </button>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-3">
            {Object.entries(selectedRow).map(([key, val]) => (
              <div key={key} className="p-2 bg-surface-container-lowest border border-outline-variant/30 flex flex-col">
                <span className="text-[10px] text-outline uppercase truncate" title={key}>{key}</span>
                <span className="text-xs font-bold text-on-surface mt-1 truncate" title={String(val ?? '')}>
                  {val === null || val === undefined ? '—' : typeof val === 'object' ? JSON.stringify(val) : String(val)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
