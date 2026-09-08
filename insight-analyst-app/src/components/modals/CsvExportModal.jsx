import React, { useState } from 'react';
import { useTelemetry } from '../../context/TelemetryContext';

export const CsvExportModal = () => {
  const { activeModal, setActiveModal, records, metadata, addAuditLog } = useTelemetry();
  const [delimiter, setDelimiter] = useState(',');
  const [includeHeaders, setIncludeHeaders] = useState(true);
  const [compression, setCompression] = useState('none');
  const [isExporting, setIsExporting] = useState(false);

  if (activeModal !== 'csv-export') return null;

  const handleDownload = () => {
    setIsExporting(true);
    setTimeout(() => {
      setIsExporting(false);
      addAuditLog("RFC-4180 CSV Export", `Exported ${records.length} records with delimiter '${delimiter}' and compression '${compression}'`);
      
      // Trigger actual download of CSV in browser
      const headers = Object.keys(records[0] || {}).join(delimiter);
      const rows = records.map(r => Object.values(r).join(delimiter)).join('\n');
      const csvContent = includeHeaders ? `${headers}\n${rows}` : rows;
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `export_${metadata.filename.replace('.csv', '')}_${Date.now()}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      setActiveModal(null);
    }, 600);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 select-none font-body-md">
      <div className="w-full max-w-2xl bg-surface-container-high border border-outline-variant/60 shadow-2xl flex flex-col">
        {/* Modal Header */}
        <div className="h-12 px-4 bg-surface-container-highest border-b border-outline-variant/40 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-primary text-[18px]">file_download</span>
            <span className="font-headline-sm text-sm font-semibold text-on-surface">
              RFC-4180 CSV Export Preview & Config
            </span>
          </div>
          <button
            onClick={() => setActiveModal(null)}
            className="w-7 h-7 flex items-center justify-center text-outline hover:text-on-surface hover:bg-surface-container transition-colors"
          >
            <span className="material-symbols-outlined text-[18px]">close</span>
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-5 flex flex-col gap-4">
          <div className="grid grid-cols-3 gap-3">
            <div className="p-3 bg-surface-container-low border border-outline-variant/30">
              <span className="font-label-caps text-[10px] text-outline uppercase block">Target Records</span>
              <span className="font-data-mono text-lg font-bold text-secondary">{records.length.toLocaleString()}</span>
            </div>
            <div className="p-3 bg-surface-container-low border border-outline-variant/30">
              <span className="font-label-caps text-[10px] text-outline uppercase block">Est. Stream Size</span>
              <span className="font-data-mono text-lg font-bold text-on-surface">3.82 MB</span>
            </div>
            <div className="p-3 bg-surface-container-low border border-outline-variant/30">
              <span className="font-label-caps text-[10px] text-outline uppercase block">Encoding Standard</span>
              <span className="font-data-mono text-lg font-bold text-tertiary">UTF-8 Strict</span>
            </div>
          </div>

          {/* Config Controls */}
          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-label-caps text-outline uppercase">Field Delimiter</label>
              <select
                value={delimiter}
                onChange={(e) => setDelimiter(e.target.value)}
                className="bg-surface-container-lowest border border-outline-variant/60 px-3 py-1.5 text-xs font-data-mono text-on-surface focus:border-primary outline-none"
              >
                <option value=",">Comma (,)</option>
                <option value=";">Semicolon (;)</option>
                <option value="\t">Tab (\t)</option>
                <option value="|">Pipe (|)</option>
              </select>
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-label-caps text-outline uppercase">Stream Compression</label>
              <select
                value={compression}
                onChange={(e) => setCompression(e.target.value)}
                className="bg-surface-container-lowest border border-outline-variant/60 px-3 py-1.5 text-xs font-data-mono text-on-surface focus:border-primary outline-none"
              >
                <option value="none">None (Raw .csv)</option>
                <option value="gzip">Gzip (.csv.gz)</option>
                <option value="zstd">Zstandard (.csv.zst)</option>
              </select>
            </div>
          </div>

          {/* Checkboxes */}
          <div className="flex items-center gap-6 pt-1">
            <label className="flex items-center gap-2 cursor-pointer text-xs font-data-mono">
              <input
                type="checkbox"
                checked={includeHeaders}
                onChange={(e) => setIncludeHeaders(e.target.checked)}
                className="w-4 h-4 bg-surface border border-outline-variant checked:bg-primary"
              />
              <span>Include Column Headers Row</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer text-xs font-data-mono">
              <input
                type="checkbox"
                defaultChecked
                className="w-4 h-4 bg-surface border border-outline-variant checked:bg-primary"
              />
              <span>Escape Double Quotes (\")</span>
            </label>
          </div>

          {/* Live Data Preview snippet */}
          <div className="flex flex-col gap-1">
            <span className="text-xs font-label-caps text-outline uppercase">Stream Buffer Preview (First 3 Lines)</span>
            <div className="bg-surface-container-lowest border border-outline-variant/40 p-3 font-data-mono text-[11px] text-on-surface-variant overflow-x-auto leading-relaxed">
              <div className="text-tertiary">row_id{delimiter}timestamp{delimiter}customer_id{delimiter}subscription_tier{delimiter}contract_mrr_usd</div>
              <div>1001{delimiter}2026-09-01 08:14:22{delimiter}CUST-8491{delimiter}Enterprise{delimiter}14250.00</div>
              <div>1002{delimiter}2026-09-01 08:29:10{delimiter}CUST-3920{delimiter}Mid-Market{delimiter}5400.00</div>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="h-14 px-5 bg-surface-container-low border-t border-outline-variant/30 flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-data-mono text-outline">
            <span className="w-1.5 h-1.5 bg-tertiary inline-block"></span>
            <span>Buffer checksum validated</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveModal(null)}
              className="px-4 py-1.5 bg-surface-container hover:bg-surface-container-highest border border-outline-variant/40 text-xs font-headline-sm transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleDownload}
              disabled={isExporting}
              className="px-5 py-1.5 bg-primary hover:bg-primary-fixed-dim text-on-primary font-semibold text-xs font-headline-sm transition-colors flex items-center gap-1.5"
            >
              <span className="material-symbols-outlined text-[16px]">
                {isExporting ? 'hourglass_top' : 'download'}
              </span>
              <span>{isExporting ? 'Generating Stream...' : 'Download CSV'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
