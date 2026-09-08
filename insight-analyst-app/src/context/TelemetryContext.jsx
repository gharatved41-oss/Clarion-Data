import React, { createContext, useContext, useState, useEffect, useMemo, useCallback } from 'react';
import api from '../services/api';

const TelemetryContext = createContext(null);

const DEFAULT_BENCHMARKS = [
  { id: 'test-sales', name: 'test-sales (B2B Sales Benchmark)', domain: 'Sales' },
  { id: 'test-payment', name: 'test-payment (FinTech Transactions)', domain: 'Payment' },
  { id: 'test-marketing', name: 'test-marketing (Campaign Conversion)', domain: 'Marketing' },
  { id: 'test-healthcare', name: 'test-healthcare (Clinical Patient Care)', domain: 'Healthcare' },
  { id: 'test-unseen_tabular', name: 'test-unseen_tabular (General Tabular)', domain: 'General' },
  { id: 'test-no_dates', name: 'test-no_dates (No Temporal Dimension)', domain: 'Cross-Sectional' },
  { id: 'test-insufficient_numerics', name: 'test-insufficient_numerics', domain: 'Categorical' },
  { id: 'test-missing_values', name: 'test-missing_values (High Nulls)', domain: 'Data Quality' },
  { id: 'test-outliers', name: 'test-outliers (High Outliers)', domain: 'Anomaly' },
  { id: 'test-unsuitable_clustering', name: 'test-unsuitable_clustering', domain: 'Synthetic' },
  { id: 'test-unsuitable_prediction', name: 'test-unsuitable_prediction', domain: 'Non-Stationary' },
];

export const TelemetryProvider = ({ children }) => {
  const [currentView, setCurrentView] = useState('visualizations');
  const [activeModal, setActiveModal] = useState(null); // 'upload-dataset' | 'csv-export' | 'flagged-outliers' | etc.
  const [isAiDrawerOpen, setIsAiDrawerOpen] = useState(false);

  // --------------------------------------------------------------------------
  // Theme Management (Light | Dark | System Default)
  // --------------------------------------------------------------------------
  const [themeMode, setThemeModeState] = useState(() => {
    return localStorage.getItem('telemetry_theme_mode') || 'dark';
  });

  const [systemPrefersDark, setSystemPrefersDark] = useState(() => {
    return window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)').matches : true;
  });

  useEffect(() => {
    if (!window.matchMedia) return;
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = (e) => setSystemPrefersDark(e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  const resolvedTheme = useMemo(() => {
    if (themeMode === 'system') {
      return systemPrefersDark ? 'dark' : 'light';
    }
    return themeMode === 'light' ? 'light' : 'dark';
  }, [themeMode, systemPrefersDark]);

  useEffect(() => {
    const root = document.documentElement;
    const body = document.body;
    root.setAttribute('data-theme', resolvedTheme);
    body.setAttribute('data-theme', resolvedTheme);
    if (resolvedTheme === 'light') {
      root.classList.remove('dark');
      root.classList.add('light');
      body.classList.remove('dark');
      body.classList.add('light');
    } else {
      root.classList.remove('light');
      root.classList.add('dark');
      body.classList.remove('light');
      body.classList.add('dark');
    }
    localStorage.setItem('telemetry_theme_mode', themeMode);
    localStorage.setItem('telemetry_theme', resolvedTheme);
  }, [resolvedTheme, themeMode]);

  const setTheme = (mode) => {
    setThemeModeState(mode);
  };

  const toggleTheme = () => {
    setThemeModeState((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  // --------------------------------------------------------------------------
  // Dataset Management & Active Context
  // --------------------------------------------------------------------------
  const [activeDatasetId, setActiveDatasetIdState] = useState(() => {
    return localStorage.getItem('active_dataset_id') || 'test-sales';
  });

  const [availableDatasets, setAvailableDatasets] = useState(() => {
    const saved = localStorage.getItem('available_datasets_list');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        // Merge with defaults to prevent losing benchmarks
        const ids = new Set(parsed.map(d => d.id));
        const merged = [...parsed];
        for (const def of DEFAULT_BENCHMARKS) {
          if (!ids.has(def.id)) merged.push(def);
        }
        return merged;
      } catch (e) {
        // Fallback
      }
    }
    return DEFAULT_BENCHMARKS;
  });

  const setActiveDatasetId = (id) => {
    setActiveDatasetIdState(id);
    localStorage.setItem('active_dataset_id', id);
  };

  // --------------------------------------------------------------------------
  // Live Telemetry & Analytical Payloads from Backend
  // --------------------------------------------------------------------------
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const [overview, setOverview] = useState(null);
  const [schemaData, setSchemaData] = useState(null);
  const [cleaningReport, setCleaningReport] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);
  const [correlationData, setCorrelationData] = useState(null);
  const [outlierData, setOutlierData] = useState(null);
  const [domainData, setDomainData] = useState(null);
  const [paymentData, setPaymentData] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [summaryData, setSummaryData] = useState(null);
  const [notificationsData, setNotificationsData] = useState(null);
  const [qualityData, setQualityData] = useState(null);

  // Hyperparameters
  const [iqrThreshold, setIqrThreshold] = useState(1.5);
  const [zScoreThreshold, setZScoreThreshold] = useState(3.0);
  const [contamination, setContamination] = useState(0.05);

  // Audit Logs
  const [auditLogs, setAuditLogs] = useState([]);

  const addAuditLog = useCallback((action, detail) => {
    setAuditLogs((prev) => [
      {
        id: `audit-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        action,
        detail,
      },
      ...prev.slice(0, 49),
    ]);
  }, []);

  // --------------------------------------------------------------------------
  // Hydrate Active Dataset from Backend
  // --------------------------------------------------------------------------
  const loadDatasetData = useCallback(async (datasetId) => {
    setIsLoading(true);
    setError(null);

    try {
      // 1. Fetch Overview & Schema first
      const [ov, sch] = await Promise.all([
        api.getOverview(datasetId).catch(err => {
          console.warn(`Could not load overview for ${datasetId}:`, err);
          return null;
        }),
        api.getSchema(datasetId).catch(err => {
          console.warn(`Could not load schema for ${datasetId}:`, err);
          return null;
        }),
      ]);

      setOverview(ov);
      setSchemaData(sch);

      // 2. Fetch parallel analytical modules
      const [clean, ana, corr, out, dom, dash, sum, notif, qual, pay] = await Promise.all([
        api.getCleaningReport(datasetId).catch(() => null),
        api.getAnalysis(datasetId).catch(() => null),
        api.getCorrelations(datasetId).catch(() => null),
        api.getOutliers(datasetId, 'all', iqrThreshold, contamination).catch(() => null),
        api.getDomain(datasetId).catch(() => null),
        api.getDashboard(datasetId).catch(() => null),
        api.getSummary(datasetId).catch(() => null),
        api.getNotifications(datasetId).catch(() => null),
        api.getDataQuality(datasetId).catch(() => null),
        api.getPaymentAnalytics(datasetId).catch(() => null),
      ]);

      setCleaningReport(clean);
      setAnalysisData(ana);
      setCorrelationData(corr);
      setOutlierData(out);
      setDomainData(dom);
      setDashboardData(dash);
      setSummaryData(sum);
      setNotificationsData(notif);
      setQualityData(qual);
      setPaymentData(pay);

      // Hydrate audit logs from cleaning report if available
      if (clean && clean.operations && clean.operations.length > 0) {
        const ops = clean.operations.map((op, idx) => ({
          id: `clean-op-${idx}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
          action: op.operation || 'CLEANING_TRANSFORM',
          detail: `${op.column ? `[${op.column}] ` : ''}${op.details || op.method || 'Applied'}${op.affected_rows ? ` (${op.affected_rows} rows)` : ''}`,
        }));
        setAuditLogs(ops);
      }

      addAuditLog("DATASET_SYNCHRONIZED", `Loaded dataset telemetry for '${datasetId}'`);
    } catch (err) {
      console.error(`Error hydrating dataset [${datasetId}]:`, err);
      setError(err.message || 'Failed to load dataset details.');
    } finally {
      setIsLoading(false);
    }
  }, [iqrThreshold, contamination, addAuditLog]);

  useEffect(() => {
    loadDatasetData(activeDatasetId);
  }, [activeDatasetId, loadDatasetData]);

  // Upload handler for single dataset file
  const uploadDatasetFile = async (file) => {
    const res = await api.uploadDataset(file);
    if (res && res.dataset_id) {
      const newEntry = {
        id: res.dataset_id,
        name: `${res.filename} (${res.rows} rows)`,
        domain: 'Uploaded',
      };
      setAvailableDatasets((prev) => {
        const updated = [newEntry, ...prev.filter(d => d.id !== res.dataset_id)];
        localStorage.setItem('available_datasets_list', JSON.stringify(updated));
        return updated;
      });
      setActiveDatasetId(res.dataset_id);
      addAuditLog("FILE_INGESTED", `Successfully uploaded ${res.filename} with ${res.rows} rows, ${res.columns} columns`);
      return res;
    }
    throw new Error("Server did not return a valid dataset ID");
  };

  // Batch upload handler for multiple dataset files (supports high-volume batch ingestion)
  const uploadDatasetFiles = async (files, onProgress) => {
    const results = [];
    const newEntries = [];
    const failedFiles = [];

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      if (onProgress) {
        onProgress({
          current: i + 1,
          total: files.length,
          file: file.name,
          percent: Math.round((i / files.length) * 100)
        });
      }
      try {
        const res = await api.uploadDataset(file);
        if (res && res.dataset_id) {
          results.push(res);
          newEntries.push({
            id: res.dataset_id,
            name: `${res.filename} (${res.rows} rows)`,
            domain: 'Uploaded',
          });
          addAuditLog("FILE_INGESTED", `Successfully uploaded ${res.filename} (${res.rows} rows, ${res.columns} cols)`);
        }
      } catch (err) {
        console.error(`Failed to upload ${file.name}:`, err);
        failedFiles.push({ name: file.name, error: err.message });
      }
    }

    if (newEntries.length > 0) {
      setAvailableDatasets((prev) => {
        const updated = [...newEntries, ...prev.filter(d => !newEntries.some(ne => ne.id === d.id))];
        localStorage.setItem('available_datasets_list', JSON.stringify(updated));
        return updated;
      });
      // Activate the first uploaded dataset
      setActiveDatasetId(newEntries[0].id);
    }

    if (failedFiles.length > 0 && results.length === 0) {
      throw new Error(`Failed to upload all selected files: ${failedFiles.map(f => f.name).join(', ')}`);
    }

    if (onProgress) {
      onProgress({ current: files.length, total: files.length, file: 'Completed', percent: 100 });
    }

    return { results, failedFiles };
  };

  // --------------------------------------------------------------------------
  // AI Analyst Chat Integration
  // --------------------------------------------------------------------------
  const [aiMessages, setAiMessages] = useState([
    {
      id: "m0",
      sender: "system",
      text: "👋 Hello! I am your AI Data Analyst. I am connected directly to your active dataset and project analytical services. How can I assist you with this dataset?",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
      suggestions: [
        "Summarize this dataset",
        "What are the strongest correlations?",
        "Which column has the most missing values?",
        "Show outlier breakdown",
        "Recommend a chart",
      ],
    },
  ]);
  const [isAiThinking, setIsAiThinking] = useState(false);

  const addAiMessage = async (text, sender = "user") => {
    const userMsg = {
      id: `msg-${Date.now()}`,
      sender,
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
    };
    setAiMessages((prev) => [...prev, userMsg]);

    if (sender === "user") {
      setIsAiThinking(true);
      try {
        const res = await api.sendChatMessage(activeDatasetId, text);
        const replyText = res.reply || res.message || "I could not retrieve an answer for this query.";
        
        const aiMsg = {
          id: `ai-${Date.now()}`,
          sender: "system",
          text: replyText,
          diff: res.diff || null,
          proposal: res.proposal || null,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        };
        setAiMessages((prev) => [...prev, aiMsg]);
        addAuditLog("AI_QUERY_EXECUTED", `Prompt: "${text.slice(0, 40)}${text.length > 40 ? '...' : ''}"`);
      } catch (err) {
        const errorMsg = {
          id: `ai-err-${Date.now()}`,
          sender: "system",
          text: `⚠️ **Error communicating with AI Assistant:** ${err.message || "Failed to fetch response."}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        };
        setAiMessages((prev) => [...prev, errorMsg]);
      } finally {
        setIsAiThinking(false);
      }
    }
  };

  // --------------------------------------------------------------------------
  // Computed Properties for Backward-Compatible View Rendering
  // --------------------------------------------------------------------------
  const metadata = useMemo(() => {
    if (overview) {
      return {
        filename: overview.filename || `${activeDatasetId}.csv`,
        size: overview.memory_usage_bytes ? `${(overview.memory_usage_bytes / 1024).toFixed(1)} KB` : '4.8 MB',
        rows: overview.rows || overview.row_count || 0,
        columns: overview.columns || overview.column_count || 0,
        validity: (overview.missing_values || 0) === 0 ? '100% VALID' : `${Math.max(1, 100 - Math.round(((overview.missing_values || 0) / (overview.rows * overview.columns || 1)) * 100))}% VALID`,
        healthScore: qualityData ? qualityData.score : (100 - Math.min(50, Math.round(((overview.missing_values || 0) / (overview.rows * overview.columns || 1)) * 100))),
        domain: domainData ? domainData.domain : 'General Tabular',
        confidence: domainData ? Math.round(domainData.confidence * 100) : 95,
        missing_values: overview.missing_values || 0,
        duplicate_rows: overview.duplicate_rows || 0,
      };
    }
    return {
      filename: `${activeDatasetId}.csv`,
      size: '—',
      rows: 0,
      columns: 0,
      validity: 'SYNCING',
      healthScore: 98,
      domain: 'Analyzing...',
      confidence: 90,
      missing_values: 0,
      duplicate_rows: 0,
    };
  }, [overview, qualityData, domainData, activeDatasetId]);

  const records = useMemo(() => {
    return (overview && overview.preview_rows) ? overview.preview_rows : [];
  }, [overview]);

  const columnsList = useMemo(() => {
    if (schemaData && schemaData.columns) {
      if (Array.isArray(schemaData.columns)) {
        return schemaData.columns.map(c => (typeof c === 'string' ? c : c.name || String(c)));
      }
      if (typeof schemaData.columns === 'object') {
        return Object.keys(schemaData.columns);
      }
    }
    if (overview && Array.isArray(overview.columns)) {
      return overview.columns;
    }
    if (records && records.length > 0) {
      return Object.keys(records[0]);
    }
    return [];
  }, [schemaData, overview, records]);

  const outlierCount = useMemo(() => {
    return outlierData?.summary?.total_outliers || 0;
  }, [outlierData]);

  // --------------------------------------------------------------------------
  // Supabase Database Synchronization Handlers
  // --------------------------------------------------------------------------
  const syncToSupabase = async ({ tableName, supabaseUrl, supabaseKey, useCleaned = true, batchSize = 500 }) => {
    const res = await fetch(`http://localhost:8000/supabase/dataset/${activeDatasetId}/push`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        table_name: tableName,
        supabase_url: supabaseUrl,
        supabase_key: supabaseKey,
        use_cleaned: useCleaned,
        batch_size: batchSize
      })
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || data.error || 'Failed to sync dataset to Supabase');
    }
    addAuditLog('SUPABASE_SYNC', `Pushed ${data.rows_pushed || 0} rows to Supabase table '${data.table_name}'`);
    return data;
  };

  const getSupabaseSql = async (tableName) => {
    const query = tableName ? `?table_name=${encodeURIComponent(tableName)}` : '';
    const res = await fetch(`http://localhost:8000/supabase/dataset/${activeDatasetId}/sql${query}`);
    return await res.json();
  };

  const verifySupabaseConnection = async (url, key) => {
    const res = await fetch(`http://localhost:8000/supabase/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ supabase_url: url, supabase_key: key })
    });
    return await res.json();
  };

  const getSupabaseConfig = async () => {
    const res = await fetch(`http://localhost:8000/supabase/config`);
    return await res.json();
  };

  const value = {
    // Navigation & Views
    currentView,
    setCurrentView,
    activeModal,
    setActiveModal,
    isAiDrawerOpen,
    setIsAiDrawerOpen,

    // Supabase Cloud Database Integration
    syncToSupabase,
    getSupabaseSql,
    verifySupabaseConnection,
    getSupabaseConfig,

    // Theme (Light | Dark | System)
    theme: resolvedTheme,
    themeMode,
    setTheme,
    toggleTheme,

    // Dataset Management
    activeDatasetId,
    setActiveDatasetId,
    availableDatasets,
    uploadDatasetFile,
    uploadDatasetFiles,

    // Live Data & Loading State
    isLoading,
    error,
    refreshActiveDataset: () => loadDatasetData(activeDatasetId),

    // Data Objects
    metadata,
    records,
    columnsList,
    overview,
    schemaData,
    cleaningReport,
    analysisData,
    correlationData,
    outlierData,
    outlierCount,
    domainData,
    paymentData,
    dashboardData,
    summaryData,
    notificationsData,
    qualityData,

    // Hyperparameters
    iqrThreshold,
    setIqrThreshold,
    zScoreThreshold,
    setZScoreThreshold,
    contamination,
    setContamination,

    // AI Analyst Chat
    aiMessages,
    addAiMessage,
    isAiThinking,

    // Audit
    auditLogs,
    addAuditLog,
  };

  return (
    <TelemetryContext.Provider value={value}>
      {children}
    </TelemetryContext.Provider>
  );
};

export const useTelemetry = () => {
  const context = useContext(TelemetryContext);
  if (!context) {
    throw new Error('useTelemetry must be used within a TelemetryProvider');
  }
  return context;
};

export default TelemetryContext;
