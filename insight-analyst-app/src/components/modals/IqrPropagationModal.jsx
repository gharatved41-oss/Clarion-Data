import React from 'react';
import { useTelemetry } from '../../context/TelemetryContext';

export const IqrPropagationModal = () => {
  const { activeModal, setActiveModal, iqrThreshold, outlierCount, addAuditLog } = useTelemetry();

  if (activeModal !== 'iqr-propagation') return null;

  const handleConfirm = () => {
    addAuditLog("Propagate IQR Hyperparameters", `Applied k=${iqrThreshold} globally across downstream feature matrix`);
    setActiveModal(null);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 select-none font-body-md">
      <div className="w-full max-w-xl bg-surface-container-high border border-outline-variant/60 shadow-2xl flex flex-col">
        {/* Header */}
        <div className="h-12 px-4 bg-surface-container-highest border-b border-outline-variant/40 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-primary text-[18px]">tune</span>
            <span className="font-headline-sm text-sm font-semibold text-on-surface">
              Propagate IQR Hyperparameters (k = {iqrThreshold})
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
        <div className="p-5 flex flex-col gap-4 font-data-mono text-xs">
          <div className="p-3 bg-tertiary-container/30 border border-tertiary/40 flex items-center gap-3">
            <span className="material-symbols-outlined text-tertiary text-2xl">check_circle</span>
            <div>
              <div className="font-bold text-tertiary">Statistical Parameter Locked</div>
              <p className="text-on-surface-variant text-[11px] mt-0.5">
                Tukey Fences Multiplier k = {iqrThreshold} will propagate to all 18 hypotheses, SARIMAX forecasting models, and downstream tabular filters.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 bg-surface-container-low border border-outline-variant/30">
              <span className="font-label-caps text-[10px] text-outline uppercase block">Active Outliers</span>
              <span className="text-base font-bold text-secondary mt-1 block">{outlierCount} records</span>
            </div>
            <div className="p-3 bg-surface-container-low border border-outline-variant/30">
              <span className="font-label-caps text-[10px] text-outline uppercase block">Distribution Coverage</span>
              <span className="text-base font-bold text-tertiary mt-1 block">99.3% clean</span>
            </div>
          </div>

          <div className="bg-surface-container-lowest border border-outline-variant/40 p-3 text-[11px] text-outline leading-relaxed">
            <span className="text-on-surface font-semibold block mb-1">Impact Summary:</span>
            • contract_mrr_usd: Outlier bounds: [$450.00, $20,400.00]<br/>
            • support_tickets_30d: Upper threshold = 15 tickets<br/>
            • SARIMAX Confidence Interval: Narrowed by ±4.2%
          </div>
        </div>

        {/* Footer */}
        <div className="h-14 px-5 bg-surface-container-low border-t border-outline-variant/30 flex items-center justify-end gap-2">
          <button
            onClick={() => setActiveModal(null)}
            className="px-4 py-1.5 bg-surface-container hover:bg-surface-container-highest border border-outline-variant/40 text-xs font-headline-sm"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            className="px-5 py-1.5 bg-primary hover:bg-primary-fixed-dim text-on-primary font-semibold text-xs font-headline-sm"
          >
            Confirm & Propagate
          </button>
        </div>
      </div>
    </div>
  );
};
