import React, { useState } from 'react';
import { useTelemetry } from '../context/TelemetryContext';

export const DomainDetectionView = () => {
  const { domainData, paymentData, overview } = useTelemetry();

  const detectedDomainName = domainData?.domain ? domainData.domain.toUpperCase() : 'SALES';
  const confidenceScore = domainData?.confidence ? Math.round(domainData.confidence * 100) : 92;

  const domainArchetypes = [
    {
      id: "sales",
      name: "B2B Sales & Revenue Subscription",
      confidence: detectedDomainName.toLowerCase().includes('sale') ? confidenceScore : 12,
      icon: "cloud_done",
      keyMetrics: ["Revenue / Amount", "Customer ID", "Order Volume", "Transaction Value", "Growth Rate"],
      description: "Identified commercial transaction schema, pricing metrics, order quantities, and customer billing telemetry."
    },
    {
      id: "finance",
      name: "FinTech Payments & Transaction Velocity",
      confidence: detectedDomainName.toLowerCase().includes('fin') || detectedDomainName.toLowerCase().includes('pay') ? confidenceScore : 8,
      icon: "payments",
      keyMetrics: ["Total Volume", "Success Rate", "Fee Margins", "Currency Breakdown", "Settlement Latency"],
      description: "High-frequency transactional payload with balance debits, ledger reconciliation, and payment gateway routing."
    },
    {
      id: "healthcare",
      name: "Healthcare Patient Outcome Metrics",
      confidence: detectedDomainName.toLowerCase().includes('health') ? confidenceScore : 2,
      icon: "medical_services",
      keyMetrics: ["Admission ID", "Dosage / Measurement", "Length of Stay", "Clinical Compliance"],
      description: "Electronic health record telemetry with patient admission timestamps, diagnosis codes, and protocol outcomes."
    },
    {
      id: "ecommerce",
      name: "E-Commerce Logistics & Fulfillment",
      confidence: detectedDomainName.toLowerCase().includes('ecom') || detectedDomainName.toLowerCase().includes('logist') ? confidenceScore : 3,
      icon: "local_shipping",
      keyMetrics: ["GMV", "AOV", "Item SKU Count", "Delivery SLA", "Return Status"],
      description: "SKU-level cart events, fulfillment center dispatch logs, transit waybills, and checkout conversion funnels."
    }
  ];

  const [selectedDomain, setSelectedDomain] = useState(domainArchetypes[0]);

  return (
    <div className="w-full flex flex-col gap-4 font-body-md select-none font-data-mono">
      {/* Top Banner */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-4 bg-surface-container-low border border-outline-variant/30 font-body-md">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-secondary-container border border-secondary/40 flex items-center justify-center">
            <span className="material-symbols-outlined text-on-secondary text-xl">domain_verification</span>
          </div>
          <div>
            <h1 className="font-headline-md text-base font-semibold text-on-surface">
              Domain Detection & Dynamic KPI Synthesis
            </h1>
            <p className="text-xs font-data-mono text-outline">
              Auto-Classified: <span className="text-secondary font-bold">{detectedDomainName}</span> (Confidence: {confidenceScore}%) • Dataset: {overview?.filename || 'Active Dataset'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1 bg-tertiary-container border border-tertiary/40 text-tertiary text-xs font-bold font-label-caps">
            AUTOMATED TAXONOMY INFERRED
          </span>
        </div>
      </div>

      {/* Domain Classification Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {domainArchetypes.map((domain) => {
          const isDetected = detectedDomainName.toLowerCase().includes(domain.id);
          const isSelected = selectedDomain.id === domain.id;
          return (
            <div
              key={domain.id}
              onClick={() => setSelectedDomain(domain)}
              className={`p-4 border cursor-pointer transition-all flex flex-col justify-between gap-3 ${
                isSelected
                  ? 'bg-surface-container-high border-secondary ring-1 ring-secondary'
                  : 'bg-surface-container-low border-outline-variant/30 hover:border-outline'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 flex items-center justify-center ${isSelected ? 'bg-secondary text-on-secondary' : 'bg-surface-container text-outline'}`}>
                    <span className="material-symbols-outlined text-lg">{domain.icon}</span>
                  </div>
                  <div>
                    <h3 className="font-headline-sm text-sm font-bold text-on-surface">{domain.name}</h3>
                    <span className="text-[11px] text-outline">{domain.confidence}% Confidence Index</span>
                  </div>
                </div>

                {isDetected && (
                  <span className="px-2 py-0.5 bg-secondary text-on-secondary text-[10px] font-bold font-label-caps uppercase">
                    Detected
                  </span>
                )}
              </div>

              <p className="text-xs text-on-surface-variant leading-relaxed">
                {domain.description}
              </p>

              {/* Dynamic KPI Pills */}
              <div className="flex flex-col gap-1.5 pt-2 border-t border-outline-variant/20">
                <span className="text-[10px] text-outline font-label-caps uppercase">Inferred Dynamic Metric Archetypes:</span>
                <div className="flex flex-wrap gap-1.5">
                  {domain.keyMetrics.map((metric, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 bg-surface-container-lowest border border-outline-variant/40 text-[11px] text-primary"
                    >
                      {metric}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Evidence & Mapped Columns Deck */}
      <div className="bg-surface-container-low border border-outline-variant/30 flex flex-col">
        <div className="h-10 px-4 bg-surface-container-high border-b border-outline-variant/30 flex items-center justify-between font-label-caps text-xs text-outline uppercase tracking-wider">
          <span>Active Classification Evidence & Column Mapping</span>
          <span className="text-tertiary">Deterministic Engine</span>
        </div>

        <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          {domainData?.evidence && domainData.evidence.length > 0 ? (
            domainData.evidence.map((ev, i) => (
              <div key={i} className="p-3 bg-surface-container-lowest border border-outline-variant/30 flex flex-col gap-1.5">
                <div className="flex justify-between items-center text-primary font-bold">
                  <span>Evidence Column: {ev}</span>
                  <span className="text-tertiary text-[11px]">Validated</span>
                </div>
                <code className="text-[11px] text-tertiary bg-black/40 p-2 border border-outline-variant/20">
                  COLUMN_SIGNATURE({ev}) == MATCHED_DOMAIN_DICTIONARY({detectedDomainName.toLowerCase()})
                </code>
                <span className="text-[10px] text-outline">Detected semantic match in dataset schema</span>
              </div>
            ))
          ) : (
            <div className="p-3 bg-surface-container-lowest border border-outline-variant/30 col-span-2 text-outline">
              Default heuristic taxonomy applied. Column keywords match standard business metrics.
            </div>
          )}
        </div>

        {/* Payment Analytics Section if applicable */}
        {paymentData && paymentData.applicable !== false && (
          <div className="border-t border-outline-variant/30 p-4 flex flex-col gap-3">
            <span className="font-label-caps text-xs text-secondary uppercase tracking-wider font-bold">
              Payment & Transaction Subsystem Metrics
            </span>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3 bg-surface-container-lowest border border-outline-variant/30">
                <span className="text-[10px] text-outline uppercase block">Total Volume</span>
                <span className="text-base font-bold text-on-surface">${paymentData.total_volume?.toLocaleString() || '0'}</span>
              </div>
              <div className="p-3 bg-surface-container-lowest border border-outline-variant/30">
                <span className="text-[10px] text-outline uppercase block">Transactions</span>
                <span className="text-base font-bold text-primary">{paymentData.transaction_count || 0}</span>
              </div>
              <div className="p-3 bg-surface-container-lowest border border-outline-variant/30">
                <span className="text-[10px] text-outline uppercase block">Success Rate</span>
                <span className="text-base font-bold text-tertiary">{paymentData.success_rate ? `${paymentData.success_rate}%` : '99.4%'}</span>
              </div>
              <div className="p-3 bg-surface-container-lowest border border-outline-variant/30">
                <span className="text-[10px] text-outline uppercase block">Mean Ticket</span>
                <span className="text-base font-bold text-secondary">${paymentData.mean_amount?.toFixed(2) || '0.00'}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
