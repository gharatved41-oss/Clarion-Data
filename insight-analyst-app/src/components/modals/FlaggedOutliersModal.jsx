import React, { useState } from 'react';
import { useTelemetry } from '../../context/TelemetryContext';

export const FlaggedOutliersModal = () => {
  const { activeModal, setActiveModal, records, outlierData, iqrThreshold, addAuditLog } = useTelemetry();
  const [quarantineTag, setQuarantineTag] = useState(`QUARANTINE_IQR_K${iqrThreshold}`);
  const [exportFormat, setExportFormat] = useState("JSON");

  if (activeModal !== 'flagged-outliers') return null;

  const outlierRows = records.filter(r => r.is_outlier);
  const totalOutliers = outlierData?.summary?.total_outliers || outlierRows.length;

  const handleExportOutliers = () => {
    // Generate actual file download
    let dataStr = "";
    let mimeType = "application/json";
    let fileExt = "json";

    if (exportFormat === "CSV") {
      mimeType = "text/csv";
      fileExt = "csv";
      if (outlierRows.length > 0) {
        const headers = Object.keys(outlierRows[0]);
        const csvRows = [headers.join(',')];
        outlierRows.forEach(row => {
          csvRows.push(headers.map(h => JSON.stringify(row[h] ?? '')).join(','));
        });
        dataStr = csvRows.join('\n');
      }
    } else {
      dataStr = JSON.stringify(outlierRows, null, 2);
    }

    const blob = new Blob([dataStr], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `outliers_export_${Date.now()}.${fileExt}`;
    a.click();
    URL.revokeObjectURL(url);

    addAuditLog("EXPORT_FLAGGED_OUTLIERS", `Exported ${outlierRows.length} statistical anomaly rows (${quarantineTag})`);
    setActiveModal(null);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 select-none font-body-md">
      <div className="w-full max-w-2xl bg-surface-container-high border border-anomaly/50 shadow-2xl flex flex-col">
        {/* Header */}
        <div className="h-12 px-4 bg-anomaly/20 border-b border-anomaly/40 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-anomaly text-[18px]">warning</span>
            <span className="font-headline-sm text-sm font-semibold text-on-surface">
              Export Statistical Outliers & Anomalies ({totalOutliers} Detected)
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
          <div className="p-3 bg-anomaly/10 border border-anomaly/30 flex items-center gap-3">
            <span className="material-symbols-outlined text-anomaly text-2xl">report_problem</span>
            <div className="text-xs font-data-mono leading-relaxed">
              <span className="font-bold text-on-surface">Threshold: IQR Multiplier k = {iqrThreshold}</span>
              <p className="text-outline">
                These records deviate beyond the statistical tolerance boundary. You can export them separately for manual data hygiene review or quarantine isolation.
              </p>
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <span className="text-xs font-label-caps text-outline uppercase">Flagged Anomaly Sample Rows ({outlierRows.length} in preview)</span>
            <div className="max-h-48 overflow-y-auto border border-outline-variant/40 bg-surface-container-lowest">
              <table className="w-full text-left font-data-mono text-xs border-collapse">
                <thead className="bg-surface-container-high text-outline sticky top-0">
                  <tr>
                    <th className="p-2 border-b border-outline-variant/30">Row ID</th>
                    <th className="p-2 border-b border-outline-variant/30">Sample Data</th>
                    <th className="p-2 border-b border-outline-variant/30">Anomaly Trigger</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant/20">
                  {outlierRows.length > 0 ? (
                    outlierRows.map((r, idx) => {
                      const firstVal = r.customer_id || r.id || r[Object.keys(r)[0]] || `Row ${idx+1}`;
                      const secondVal = r.contract_mrr_usd !== undefined ? `$${r.contract_mrr_usd}` : Object.values(r)[1] ?? '';
                      return (
                        <tr key={r.row_id || idx} className="hover:bg-surface-container-low text-on-surface">
                          <td className="p-2 text-primary font-bold">#{r.row_id || idx + 1}</td>
                          <td className="p-2 text-on-surface truncate max-w-[200px]">
                            {String(firstVal)} • {String(secondVal)}
                          </td>
                          <td className="p-2 text-anomaly text-[11px]">{r.outlier_reason || "IQR/Z-Score Boundary Divergence"}</td>
                        </tr>
                      );
                    })
                  ) : (
                    <tr>
                      <td colSpan={3} className="p-4 text-center text-outline text-xs">
                        No individual outlier sample rows flagged in current preview buffer.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-label-caps text-outline uppercase">Quarantine Meta Tag</label>
              <input
                type="text"
                value={quarantineTag}
                onChange={(e) => setQuarantineTag(e.target.value)}
                className="bg-surface-container-lowest border border-outline-variant/60 px-3 py-1.5 text-xs font-data-mono text-on-surface outline-none focus:border-primary"
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-label-caps text-outline uppercase">Export Format</label>
              <select
                value={exportFormat}
                onChange={(e) => setExportFormat(e.target.value)}
                className="bg-surface-container-lowest border border-outline-variant/60 px-3 py-1.5 text-xs font-data-mono text-on-surface outline-none focus:border-primary"
              >
                <option value="JSON">JSON File (.json)</option>
                <option value="CSV">CSV Outlier Quarantine (.csv)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="h-14 px-5 bg-surface-container-low border-t border-outline-variant/30 flex items-center justify-between">
          <span className="text-xs font-data-mono text-outline">
            {outlierRows.length} anomaly preview records
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveModal(null)}
              className="px-4 py-1.5 bg-surface-container hover:bg-surface-container-highest border border-outline-variant/40 text-xs font-headline-sm"
            >
              Cancel
            </button>
            <button
              onClick={handleExportOutliers}
              disabled={outlierRows.length === 0}
              className="px-5 py-1.5 bg-anomaly hover:bg-red-700 text-white font-semibold text-xs font-headline-sm transition-colors flex items-center gap-1.5 disabled:opacity-50"
            >
              <span className="material-symbols-outlined text-[16px]">file_download</span>
              <span>Export Outliers</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
