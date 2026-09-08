import React from 'react';
import { TelemetryProvider, useTelemetry } from './context/TelemetryContext';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { TelemetryRibbon } from './components/layout/TelemetryRibbon';

// Views
import { SchemaDetectionView } from './views/SchemaDetectionView';
import { DataQualityView } from './views/DataQualityView';
import { ProcessingPipelineView } from './views/ProcessingPipelineView';
import { IntelligenceDashboardView } from './views/IntelligenceDashboardView';
import { DomainDetectionView } from './views/DomainDetectionView';
import { InsightsExplorerView } from './views/InsightsExplorerView';
import { TabularExplorerView } from './views/TabularExplorerView';
import { ExecutiveReportView } from './views/ExecutiveReportView';
import { AuditHistoryView } from './views/AuditHistoryView';
import { SettingsTolerancesView } from './views/SettingsTolerancesView';

// Modals & Drawers
import { CsvExportModal } from './components/modals/CsvExportModal';
import { ArrowFeatherModal } from './components/modals/ArrowFeatherModal';
import { FlaggedOutliersModal } from './components/modals/FlaggedOutliersModal';
import { IqrPropagationModal } from './components/modals/IqrPropagationModal';
import { UploadDatasetModal } from './components/modals/UploadDatasetModal';
import { SupabaseSyncModal } from './components/modals/SupabaseSyncModal';
import { AiAnalystDrawer } from './components/drawers/AiAnalystDrawer';

class ViewErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, errorInfo) {
    console.error("View Error Caught:", error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="p-6 bg-surface-container-low border border-anomaly/40 flex flex-col gap-3 font-data-mono">
          <div className="flex items-center gap-2 text-anomaly">
            <span className="material-symbols-outlined text-2xl">error</span>
            <span className="font-bold text-sm">Telemetry View Render Error</span>
          </div>
          <p className="text-xs text-outline leading-relaxed">
            {this.state.error?.message || "An unexpected error occurred while rendering this view."}
          </p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="self-start px-3 py-1.5 bg-primary text-on-primary text-xs font-semibold hover:bg-primary-fixed-dim transition-colors rounded-sm"
          >
            Retry View
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

const MainContent = () => {
  const { currentView, theme } = useTelemetry();

  const renderView = () => {
    switch (currentView) {
      case 'datasets':
      case 'schema-detection':
        return <SchemaDetectionView />;
      case 'quality-and-audit':
        return <DataQualityView />;
      case 'pipeline-engine':
        return <ProcessingPipelineView />;
      case 'visualizations':
        return <IntelligenceDashboardView />;
      case 'domain-detection':
        return <DomainDetectionView />;
      case 'insights-explorer':
        return <InsightsExplorerView />;
      case 'tabular-explorer':
        return <TabularExplorerView />;
      case 'executive-reports':
        return <ExecutiveReportView />;
      case 'audit-history':
        return <AuditHistoryView />;
      case 'settings-and-tolerances':
        return <SettingsTolerancesView />;
      case 'ai-analyst':
        return <IntelligenceDashboardView />;
      default:
        return <IntelligenceDashboardView />;
    }
  };

  const showRibbon = ['visualizations', 'insights-explorer', 'tabular-explorer', 'ai-analyst'].includes(currentView);

  return (
    <div className={`min-h-screen bg-surface flex text-on-surface ${theme} print:bg-white print:text-slate-900 print:min-h-0`} data-theme={theme}>
      {/* Fixed Left Sidebar - Hidden in PDF/Print */}
      <div className="print:hidden">
        <Sidebar />
      </div>

      {/* Main Content Area */}
      <div className="pl-60 print:pl-0 print:m-0 print:w-full flex-1 flex flex-col min-h-screen print:min-h-0 bg-surface print:bg-white text-on-surface print:text-slate-900">
        {/* Global Fixed Header - Hidden in PDF/Print */}
        <div className="print:hidden">
          <Header />
        </div>

        {/* Dynamic Main Workspace */}
        <main className="w-full pt-[88px] print:pt-0 print:m-0 flex-1 flex flex-col bg-surface print:bg-white text-on-surface print:text-slate-900">
          {/* Telemetry Operational Ribbon for active analytical views - Hidden in PDF/Print */}
          {showRibbon && (
            <div className="print:hidden">
              <TelemetryRibbon />
            </div>
          )}

          {/* Active View Container with Error Boundary */}
          <div className="p-space-4 print:p-0 flex-1 pb-16 print:pb-0 bg-surface print:bg-white text-on-surface print:text-slate-900">
            <ViewErrorBoundary key={currentView}>
              {renderView()}
            </ViewErrorBoundary>
          </div>
        </main>
      </div>

      {/* Slide-over Drawers & Modals - Hidden in PDF/Print */}
      <div className="print:hidden">
        <AiAnalystDrawer />
        <UploadDatasetModal />
        <SupabaseSyncModal />
        <CsvExportModal />
        <ArrowFeatherModal />
        <FlaggedOutliersModal />
        <IqrPropagationModal />
      </div>
    </div>
  );
};

export function App() {
  return (
    <TelemetryProvider>
      <MainContent />
    </TelemetryProvider>
  );
}

export default App;
