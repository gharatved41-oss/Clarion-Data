import React, { useState, useEffect } from 'react';
import { useTelemetry } from '../../context/TelemetryContext';

export const SupabaseSyncModal = () => {
  const {
    activeModal,
    setActiveModal,
    activeDatasetId,
    overview,
    records,
    syncToSupabase,
    getSupabaseSql,
    verifySupabaseConnection,
    addAuditLog
  } = useTelemetry();

  const [supabaseUrl, setSupabaseUrl] = useState('');
  const [supabaseKey, setSupabaseKey] = useState('');
  const [tableName, setTableName] = useState('');
  const [showKey, setShowKey] = useState(false);
  const [useCleaned, setUseCleaned] = useState(true);
  const [batchSize, setBatchSize] = useState(500);

  // States for actions
  const [isVerifying, setIsVerifying] = useState(false);
  const [verifyStatus, setVerifyStatus] = useState(null);

  const [isPushing, setIsPushing] = useState(false);
  const [pushResult, setPushResult] = useState(null);
  const [pushError, setPushError] = useState(null);

  const [sqlSchema, setSqlSchema] = useState('');
  const [showSql, setShowSql] = useState(false);
  const [copiedSql, setCopiedSql] = useState(false);

  // Load saved credentials from localStorage or set defaults
  useEffect(() => {
    if (activeModal === 'supabase-sync') {
      const savedUrl = localStorage.getItem('clarion_supabase_url') || '';
      const savedKey = localStorage.getItem('clarion_supabase_key') || '';
      setSupabaseUrl(savedUrl);
      setSupabaseKey(savedKey);

      // Default table name based on dataset filename
      const base = (overview?.filename || activeDatasetId || 'dataset')
        .replace(/\.[^/.]+$/, '')
        .replace(/[^a-zA-Z0-9_]/g, '_')
        .toLowerCase();
      setTableName(`clarion_${base}`);

      // Fetch generated SQL schema
      if (getSupabaseSql) {
        getSupabaseSql(`clarion_${base}`)
          .then(data => {
            if (data?.sql_schema) setSqlSchema(data.sql_schema);
          })
          .catch(() => {});
      }
      setPushResult(null);
      setPushError(null);
      setVerifyStatus(null);
    }
  }, [activeModal, activeDatasetId, overview]);

  if (activeModal !== 'supabase-sync') return null;

  const handleVerify = async () => {
    if (!supabaseUrl.trim() || !supabaseKey.trim()) {
      setVerifyStatus({ valid: false, message: 'Please enter both Supabase Project URL and API Key.' });
      return;
    }
    setIsVerifying(true);
    setVerifyStatus(null);
    try {
      const res = await verifySupabaseConnection(supabaseUrl, supabaseKey);
      setVerifyStatus(res);
      if (res.valid) {
        localStorage.setItem('clarion_supabase_url', supabaseUrl.trim());
        localStorage.setItem('clarion_supabase_key', supabaseKey.trim());
      }
    } catch (e) {
      setVerifyStatus({ valid: false, message: e.message || 'Verification failed' });
    } finally {
      setIsVerifying(false);
    }
  };

  const handlePush = async () => {
    if (!supabaseUrl.trim() || !supabaseKey.trim()) {
      setPushError('Supabase Project URL and API Key are required to push data.');
      return;
    }
    if (!tableName.trim()) {
      setPushError('Please specify a target table name.');
      return;
    }

    setIsPushing(true);
    setPushError(null);
    setPushResult(null);

    // Persist credentials locally for convenience
    localStorage.setItem('clarion_supabase_url', supabaseUrl.trim());
    localStorage.setItem('clarion_supabase_key', supabaseKey.trim());

    try {
      const res = await syncToSupabase({
        tableName: tableName.trim(),
        supabaseUrl: supabaseUrl.trim(),
        supabaseKey: supabaseKey.trim(),
        useCleaned,
        batchSize: Number(batchSize) || 500
      });

      if (res.status === 'table_missing') {
        setPushError(res.error);
        if (res.sql_schema) {
          setSqlSchema(res.sql_schema);
          setShowSql(true);
        }
      } else if (res.status === 'error') {
        setPushError(res.error || 'Failed to push data to Supabase.');
      } else {
        setPushResult(res);
      }
    } catch (e) {
      setPushError(e.message || 'An unexpected error occurred while pushing data.');
    } finally {
      setIsPushing(false);
    }
  };

  const handleCopySql = () => {
    if (sqlSchema) {
      navigator.clipboard.writeText(sqlSchema);
      setCopiedSql(true);
      setTimeout(() => setCopiedSql(false), 2000);
    }
  };

  const totalRows = overview?.rows || records?.length || 0;
  const totalCols = overview?.columns || 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-surface-container-low border border-outline-variant/40 shadow-2xl w-full max-w-2xl font-data-mono flex flex-col my-auto max-h-[90vh]">
        {/* Header */}
        <div className="h-13 px-5 bg-surface-container-high border-b border-outline-variant/30 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 flex items-center justify-center font-bold">
              <span className="material-symbols-outlined text-lg">database</span>
            </div>
            <div>
              <h2 className="font-headline-sm text-sm font-bold text-on-surface">
                Push Dataset to Supabase Cloud Database
              </h2>
              <p className="text-[11px] text-outline">
                Synchronize active records directly into a PostgreSQL table
              </p>
            </div>
          </div>
          <button
            onClick={() => setActiveModal(null)}
            className="w-7 h-7 flex items-center justify-center text-outline hover:text-on-surface transition-colors"
          >
            <span className="material-symbols-outlined text-[18px]">close</span>
          </button>
        </div>

        {/* Content Body */}
        <div className="p-5 flex flex-col gap-4 overflow-y-auto">
          {/* Active Dataset Summary Banner */}
          <div className="p-3 bg-surface-container-lowest border border-outline-variant/30 flex flex-wrap items-center justify-between gap-2 text-xs">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-[17px]">dataset</span>
              <span className="font-bold text-on-surface">{overview?.filename || activeDatasetId}</span>
            </div>
            <div className="flex items-center gap-3 text-outline">
              <span><strong>{totalRows.toLocaleString()}</strong> rows</span>
              <span>•</span>
              <span><strong>{totalCols}</strong> columns</span>
              <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] uppercase font-bold">
                Ready to Sync
              </span>
            </div>
          </div>

          {/* Form Fields */}
          <div className="grid grid-cols-1 gap-3 text-xs">
            {/* Supabase URL */}
            <div className="flex flex-col gap-1">
              <label className="text-[11px] font-bold uppercase text-outline flex items-center justify-between">
                <span>Supabase Project URL</span>
                <span className="text-[10px] font-normal text-outline-variant">e.g. https://xyzcompany.supabase.co</span>
              </label>
              <input
                type="text"
                value={supabaseUrl}
                onChange={(e) => setSupabaseUrl(e.target.value)}
                placeholder="https://your-project-id.supabase.co"
                className="w-full px-3 py-2 bg-surface-container-lowest border border-outline-variant/50 focus:border-primary text-on-surface outline-none transition-colors"
              />
            </div>

            {/* Supabase API Key */}
            <div className="flex flex-col gap-1">
              <label className="text-[11px] font-bold uppercase text-outline flex items-center justify-between">
                <span>Supabase API Key (Anon or Service Role)</span>
                <button
                  type="button"
                  onClick={() => setShowKey(!showKey)}
                  className="text-primary hover:underline text-[10px] lowercase"
                >
                  {showKey ? 'Hide key' : 'Show key'}
                </button>
              </label>
              <div className="relative">
                <input
                  type={showKey ? 'text' : 'password'}
                  value={supabaseKey}
                  onChange={(e) => setSupabaseKey(e.target.value)}
                  placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                  className="w-full px-3 py-2 bg-surface-container-lowest border border-outline-variant/50 focus:border-primary text-on-surface outline-none transition-colors pr-10 font-mono text-xs"
                />
                <button
                  type="button"
                  onClick={handleVerify}
                  disabled={isVerifying}
                  className="absolute right-1 top-1 bottom-1 px-2.5 bg-surface-container hover:bg-surface-container-high text-primary text-[11px] font-semibold border border-outline-variant/40 flex items-center gap-1 transition-colors disabled:opacity-50"
                  title="Test authentication credentials"
                >
                  <span className="material-symbols-outlined text-[14px]">
                    {isVerifying ? 'sync' : 'verified_user'}
                  </span>
                  <span>{isVerifying ? 'Testing...' : 'Test'}</span>
                </button>
              </div>
            </div>

            {/* Verification Status Feedback */}
            {verifyStatus && (
              <div className={`p-2.5 text-xs border flex items-center gap-2 ${
                verifyStatus.valid 
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' 
                  : 'bg-anomaly/10 border-anomaly/30 text-anomaly'
              }`}>
                <span className="material-symbols-outlined text-[16px]">
                  {verifyStatus.valid ? 'check_circle' : 'error'}
                </span>
                <span>{verifyStatus.message}</span>
              </div>
            )}

            {/* Target Table & Batch Size */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="sm:col-span-2 flex flex-col gap-1">
                <label className="text-[11px] font-bold uppercase text-outline">
                  Target PostgreSQL Table Name
                </label>
                <input
                  type="text"
                  value={tableName}
                  onChange={(e) => setTableName(e.target.value)}
                  placeholder="clarion_dataset"
                  className="w-full px-3 py-2 bg-surface-container-lowest border border-outline-variant/50 focus:border-primary text-on-surface outline-none transition-colors"
                />
              </div>

              <div className="flex flex-col gap-1">
                <label className="text-[11px] font-bold uppercase text-outline">
                  Batch Chunk Size
                </label>
                <select
                  value={batchSize}
                  onChange={(e) => setBatchSize(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-surface-container-lowest border border-outline-variant/50 focus:border-primary text-on-surface outline-none transition-colors"
                >
                  <option value={250}>250 rows / batch</option>
                  <option value={500}>500 rows / batch</option>
                  <option value={1000}>1,000 rows / batch</option>
                </select>
              </div>
            </div>

            {/* Clean Data Checkbox */}
            <label className="flex items-center gap-2 pt-1 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={useCleaned}
                onChange={(e) => setUseCleaned(e.target.checked)}
                className="w-4 h-4 accent-primary"
              />
              <span className="text-xs text-on-surface">
                Apply data hygiene pipeline first (impute nulls, sanitize columns & remove duplicates)
              </span>
            </label>
          </div>

          {/* Success Banner */}
          {pushResult && (
            <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex flex-col gap-2">
              <div className="flex items-center gap-2 font-bold text-sm">
                <span className="material-symbols-outlined text-[20px]">check_circle</span>
                <span>{pushResult.message}</span>
              </div>
              <div className="text-xs text-emerald-300 flex items-center gap-4 pt-1 border-t border-emerald-500/20">
                <span>Rows Synchronized: <strong>{pushResult.rows_pushed?.toLocaleString()}</strong></span>
                <span>Batches: <strong>{pushResult.batches}</strong></span>
                <span>Table: <strong>public.{pushResult.table_name}</strong></span>
              </div>
            </div>
          )}

          {/* Error Banner */}
          {pushError && (
            <div className="p-4 bg-anomaly/10 border border-anomaly/30 text-anomaly flex flex-col gap-2 text-xs">
              <div className="flex items-center gap-2 font-bold text-sm">
                <span className="material-symbols-outlined text-[18px]">error</span>
                <span>Database Sync Notification</span>
              </div>
              <p>{pushError}</p>
            </div>
          )}

          {/* SQL DDL Generator Accordion */}
          <div className="border border-outline-variant/30 bg-surface-container-lowest flex flex-col">
            <button
              type="button"
              onClick={() => setShowSql(!showSql)}
              className="px-3 py-2 flex items-center justify-between text-xs font-bold text-outline hover:text-on-surface transition-colors"
            >
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-[16px] text-primary">terminal</span>
                <span>PostgreSQL Table DDL Script (SQL)</span>
              </div>
              <div className="flex items-center gap-1.5 text-[11px] text-primary">
                <span>{showSql ? 'Hide SQL' : 'View SQL'}</span>
                <span className="material-symbols-outlined text-[14px]">
                  {showSql ? 'expand_less' : 'expand_more'}
                </span>
              </div>
            </button>

            {showSql && (
              <div className="p-3 border-t border-outline-variant/30 flex flex-col gap-2">
                <div className="flex items-center justify-between text-[10px] text-outline">
                  <span>Run this query in your Supabase SQL Editor if the table does not exist:</span>
                  <button
                    type="button"
                    onClick={handleCopySql}
                    className="flex items-center gap-1 text-primary hover:underline font-bold uppercase"
                  >
                    <span className="material-symbols-outlined text-[13px]">
                      {copiedSql ? 'check' : 'content_copy'}
                    </span>
                    <span>{copiedSql ? 'Copied!' : 'Copy SQL'}</span>
                  </button>
                </div>
                <pre className="p-3 bg-surface-container-high border border-outline-variant/40 text-[11px] text-on-surface overflow-x-auto max-h-40 font-mono select-text">
                  {sqlSchema || 'Generating schema...'}
                </pre>
              </div>
            )}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="h-14 px-5 bg-surface-container border-t border-outline-variant/30 flex items-center justify-between">
          <div className="text-[11px] text-outline">
            <span>Powered by Supabase PostgREST Engine</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setActiveModal(null)}
              className="px-4 py-1.5 bg-surface-container-high hover:bg-surface-container-highest text-outline hover:text-on-surface text-xs font-semibold transition-colors"
            >
              Close
            </button>
            <button
              type="button"
              onClick={handlePush}
              disabled={isPushing}
              className="px-5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold font-headline-sm flex items-center gap-2 shadow-sm transition-all disabled:opacity-50 active:scale-98 cursor-pointer"
            >
              <span className="material-symbols-outlined text-[16px] animate-spin" style={{ display: isPushing ? 'inline-block' : 'none' }}>
                sync
              </span>
              <span className="material-symbols-outlined text-[16px]" style={{ display: !isPushing ? 'inline-block' : 'none' }}>
                cloud_upload
              </span>
              <span>{isPushing ? 'Pushing Data...' : 'Push to Supabase'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SupabaseSyncModal;
