import React, { useState } from 'react';
import { useTelemetry } from '../../context/TelemetryContext';

export const ArrowFeatherModal = () => {
  const { activeModal, setActiveModal, records, addAuditLog } = useTelemetry();
  const [batchSize, setBatchSize] = useState(65536);
  const [useDictionaryEncoding, setUseDictionaryEncoding] = useState(true);
  const [isExporting, setIsExporting] = useState(false);

  if (activeModal !== 'arrow-feather') return null;

  const handleExport = () => {
    setIsExporting(true);
    setTimeout(() => {
      setIsExporting(false);
      addAuditLog("Arrow Feather IPC Export", `Generated binary IPC stream (RecordBatches: 1, BatchSize: ${batchSize})`);
      alert("Arrow IPC stream generated successfully. File 'dataset_arrow_v2.arrow' downloaded (1.42 MB - 63% compression ratio vs CSV).");
      setActiveModal(null);
    }, 700);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 select-none font-body-md">
      <div className="w-full max-w-2xl bg-surface-container-high border border-outline-variant/60 shadow-2xl flex flex-col">
        {/* Header */}
        <div className="h-12 px-4 bg-surface-container-highest border-b border-outline-variant/40 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-secondary text-[18px]">memory</span>
            <span className="font-headline-sm text-sm font-semibold text-on-surface">
              Apache Arrow Feather IPC Export (Zero-Copy In-Memory Schema)
            </span>
          </div>
          <button
            onClick={() => setActiveModal(null)}
            className="w-7 h-7 flex items-center justify-center text-outline hover:text-on-surface"
          >
            <span className="material-symbols-outlined text-[18px]">close</span>
          </button>
        </div>

        {/* Body */}
        <div className="p-5 flex flex-col gap-4">
          <div className="grid grid-cols-3 gap-3">
            <div className="p-3 bg-surface-container-low border border-outline-variant/30">
              <span className="font-label-caps text-[10px] text-outline uppercase block">IPC Format</span>
              <span className="font-data-mono text-lg font-bold text-secondary">Feather V2 / IPC</span>
            </div>
            <div className="p-3 bg-surface-container-low border border-outline-variant/30">
              <span className="font-label-caps text-[10px] text-outline uppercase block">Compression</span>
              <span className="font-data-mono text-lg font-bold text-tertiary">LZ4_FRAME</span>
            </div>
            <div className="p-3 bg-surface-container-low border border-outline-variant/30">
              <span className="font-label-caps text-[10px] text-outline uppercase block">Est. Memory Footprint</span>
              <span className="font-data-mono text-lg font-bold text-on-surface">1.42 MB</span>
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <span className="text-xs font-label-caps text-outline uppercase">Schema Dictionary Mapping</span>
            <div className="bg-surface-container-lowest border border-outline-variant/40 p-3 font-data-mono text-xs text-on-surface-variant flex flex-col gap-1">
              <div className="flex justify-between border-b border-outline-variant/20 pb-1 text-primary">
                <span>Field Name</span>
                <span>Arrow DataType</span>
                <span>Metadata</span>
              </div>
              <div className="flex justify-between">
                <span>row_id</span>
                <span className="text-tertiary">int64</span>
                <span className="text-outline">Non-nullable</span>
              </div>
              <div className="flex justify-between">
                <span>timestamp</span>
                <span className="text-tertiary">timestamp[ns, tz=UTC]</span>
                <span className="text-outline">Temporal index</span>
              </div>
              <div className="flex justify-between">
                <span>subscription_tier</span>
                <span className="text-secondary">dictionary&lt;int8, utf8&gt;</span>
                <span className="text-tertiary">Dict-Encoded</span>
              </div>
              <div className="flex justify-between">
                <span>contract_mrr_usd</span>
                <span className="text-tertiary">float64</span>
                <span className="text-outline">Null count: 14</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-label-caps text-outline uppercase">RecordBatch Row Chunking</label>
              <select
                value={batchSize}
                onChange={(e) => setBatchSize(Number(e.target.value))}
                className="bg-surface-container-lowest border border-outline-variant/60 px-3 py-1.5 text-xs font-data-mono text-on-surface focus:border-primary outline-none"
              >
                <option value={16384}>16,384 rows / batch</option>
                <option value={65536}>65,536 rows / batch (Recommended)</option>
                <option value={131072}>131,072 rows / batch</option>
              </select>
            </div>

            <div className="flex items-center gap-2 pt-6">
              <label className="flex items-center gap-2 cursor-pointer text-xs font-data-mono">
                <input
                  type="checkbox"
                  checked={useDictionaryEncoding}
                  onChange={(e) => setUseDictionaryEncoding(e.target.checked)}
                  className="w-4 h-4 bg-surface border border-outline-variant checked:bg-primary"
                />
                <span>Auto-Dictionary String Columns</span>
              </label>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="h-14 px-5 bg-surface-container-low border-t border-outline-variant/30 flex items-center justify-between">
          <span className="text-xs font-data-mono text-outline">
            Compatible with Polars, PyArrow, DuckDB & DuckDB-Wasm
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveModal(null)}
              className="px-4 py-1.5 bg-surface-container hover:bg-surface-container-highest border border-outline-variant/40 text-xs font-headline-sm"
            >
              Cancel
            </button>
            <button
              onClick={handleExport}
              disabled={isExporting}
              className="px-5 py-1.5 bg-secondary-container hover:bg-secondary text-on-secondary font-semibold text-xs font-headline-sm transition-colors flex items-center gap-1.5"
            >
              <span className="material-symbols-outlined text-[16px]">
                {isExporting ? 'hourglass_top' : 'memory'}
              </span>
              <span>{isExporting ? 'Packaging IPC Stream...' : 'Download Arrow IPC'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
