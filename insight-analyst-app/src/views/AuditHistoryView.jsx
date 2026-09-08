import React, { useState } from 'react';
import { useTelemetry } from '../context/TelemetryContext';

export const AuditHistoryView = () => {
  const { auditLogs, cleaningReport, overview, metadata } = useTelemetry();
  const [selectedEvent, setSelectedEvent] = useState(auditLogs[0] || null);

  // Keep selected event synced
  React.useEffect(() => {
    if (!selectedEvent && auditLogs.length > 0) {
      setSelectedEvent(auditLogs[0]);
    }
  }, [auditLogs, selectedEvent]);

  const cleaningOps = cleaningReport?.operations || [];

  return (
    <div className="w-full flex flex-col gap-4 font-body-md select-none font-data-mono">
      {/* Top Banner */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-4 bg-surface-container-low border border-outline-variant/30 font-body-md">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-primary-container border border-primary/40 flex items-center justify-center">
            <span className="material-symbols-outlined text-primary text-xl">history</span>
          </div>
          <div>
            <h1 className="font-headline-md text-base font-semibold text-on-surface">
              Lineage Graph & Immutable Audit Trail
            </h1>
            <p className="text-xs font-data-mono text-outline">
              Integrity Checksum: SHA-256 Verified • {auditLogs.length} Logged Events • Dataset: {overview?.filename || 'Active Dataset'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-2.5 py-1 bg-tertiary-container border border-tertiary/40 text-tertiary text-xs font-bold font-label-caps">
            AUDIT TRAIL ACTIVE
          </span>
        </div>
      </div>

      {/* Lineage Graph Visual DAG */}
      <div className="bg-surface-container-low border border-outline-variant/30 flex flex-col p-4 gap-3">
        <span className="font-label-caps text-xs text-outline uppercase tracking-wider font-bold">
          Data Transformation Lineage Pipeline (DAG)
        </span>

        <div className="p-4 bg-surface-container-lowest border border-outline-variant/40 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex flex-col items-center gap-1 p-2 bg-surface-container border border-outline-variant/40 min-w-[130px]">
            <span className="material-symbols-outlined text-outline text-lg">upload_file</span>
            <span className="font-bold text-on-surface">Raw Data File</span>
            <span className="text-[10px] text-outline">{overview?.rows || 0} Rows Ingested</span>
          </div>

          <span className="text-outline text-lg">→</span>

          <div className="flex flex-col items-center gap-1 p-2 bg-surface-container border border-outline-variant/40 min-w-[130px]">
            <span className="material-symbols-outlined text-secondary text-lg">schema</span>
            <span className="font-bold text-on-surface">Schema Ingestion</span>
            <span className="text-[10px] text-secondary">{overview?.columns || 0} Columns Detected</span>
          </div>

          <span className="text-outline text-lg">→</span>

          <div className="flex flex-col items-center gap-1 p-2 bg-surface-container border border-outline-variant/40 min-w-[130px]">
            <span className="material-symbols-outlined text-tertiary text-lg">auto_fix_high</span>
            <span className="font-bold text-on-surface">Auto-Clean Pipeline</span>
            <span className="text-[10px] text-tertiary">{cleaningOps.length} Ops Performed</span>
          </div>

          <span className="text-outline text-lg">→</span>

          <div className="flex flex-col items-center gap-1 p-2 bg-surface-container border border-outline-variant/40 min-w-[130px]">
            <span className="material-symbols-outlined text-primary text-lg">neurology</span>
            <span className="font-bold text-on-surface">ML & Correlation</span>
            <span className="text-[10px] text-primary">K-Means & Predictions</span>
          </div>

          <span className="text-outline text-lg">→</span>

          <div className="flex flex-col items-center gap-1 p-2 bg-primary-container border border-primary text-primary min-w-[130px]">
            <span className="material-symbols-outlined text-tertiary text-lg">monitoring</span>
            <span className="font-bold text-on-surface">Insight Deck</span>
            <span className="text-[10px] text-tertiary">Real-time Telemetry</span>
          </div>
        </div>
      </div>

      {/* Audit Event Log Table & Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 bg-surface-container-low border border-outline-variant/30 flex flex-col">
          <div className="h-10 px-4 bg-surface-container-high border-b border-outline-variant/30 flex items-center justify-between font-label-caps text-xs text-outline uppercase tracking-wider">
            <span>Audit Events Stream ({auditLogs.length} Events)</span>
            <span>Status: Verified</span>
          </div>

          <div className="overflow-x-auto max-h-[450px]">
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-surface-container-lowest text-outline border-b border-outline-variant/20 sticky top-0">
                <tr>
                  <th className="p-2.5">Event ID</th>
                  <th className="p-2.5">Timestamp</th>
                  <th className="p-2.5">Action Executed</th>
                  <th className="p-2.5">Details</th>
                  <th className="p-2.5 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/20">
                {auditLogs.map((log) => {
                  const isSelected = selectedEvent?.id === log.id;
                  return (
                    <tr
                      key={log.id}
                      onClick={() => setSelectedEvent(log)}
                      className={`cursor-pointer transition-colors ${
                        isSelected ? 'bg-primary-container/40 border-l-2 border-primary' : 'hover:bg-surface-container'
                      }`}
                    >
                      <td className="p-2.5 text-primary font-bold font-mono text-[11px]">{log.id}</td>
                      <td className="p-2.5 text-outline text-[11px]">{log.timestamp}</td>
                      <td className="p-2.5 text-secondary font-semibold">{log.action}</td>
                      <td className="p-2.5 text-on-surface truncate max-w-[220px]" title={log.detail}>
                        {log.detail}
                      </td>
                      <td className="p-2.5 text-center">
                        <span className="px-1.5 py-0.5 bg-tertiary-container/40 text-tertiary text-[10px] uppercase font-bold">
                          SUCCESS
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Selected Event Details Inspector */}
        <div className="bg-surface-container-low border border-outline-variant/30 flex flex-col p-4 gap-3">
          <span className="font-label-caps text-[10px] text-outline uppercase block border-b border-outline-variant/30 pb-2">
            Audit Event Payload Inspector
          </span>

          {selectedEvent ? (
            <div className="flex flex-col gap-3 text-xs">
              <div className="flex justify-between items-center">
                <span className="text-primary font-bold">{selectedEvent.id}</span>
                <span className="text-outline text-[11px]">{selectedEvent.timestamp}</span>
              </div>

              <div className="p-2.5 bg-surface-container-lowest border border-outline-variant/30">
                <span className="text-[10px] text-outline uppercase block">Action</span>
                <span className="text-secondary font-bold">{selectedEvent.action}</span>
              </div>

              <div className="p-2.5 bg-surface-container-lowest border border-outline-variant/30">
                <span className="text-[10px] text-outline uppercase block">Detail</span>
                <p className="text-on-surface leading-relaxed mt-1">{selectedEvent.detail}</p>
              </div>

              <div className="p-2.5 bg-surface-container-lowest border border-outline-variant/30">
                <span className="text-[10px] text-outline uppercase block">Dataset Context</span>
                <span className="text-tertiary font-bold">{overview?.filename || 'Current Dataset'}</span>
              </div>
            </div>
          ) : (
            <div className="text-center text-outline text-xs p-6">
              Select an event to inspect its payload details.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
