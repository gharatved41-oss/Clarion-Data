import React, { useState, useRef, useMemo } from 'react';
import { useTelemetry } from '../../context/TelemetryContext';

const MAX_FILE_SIZE_GB = 2;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_GB * 1024 * 1024 * 1024;
const ALLOWED_EXTENSIONS = ['csv', 'xlsx', 'xls'];

export const UploadDatasetModal = () => {
  const { activeModal, setActiveModal, uploadDatasetFiles } = useTelemetry();
  const [dragActive, setDragActive] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatusText, setUploadStatusText] = useState('');
  const [uploadError, setUploadError] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(null);
  const fileInputRef = useRef(null);

  if (activeModal !== 'upload-dataset') return null;

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const validateAndAddFiles = (newFiles) => {
    setUploadError(null);
    const valid = [];
    const existingNames = new Set(selectedFiles.map(f => f.name));

    for (const file of newFiles) {
      const ext = file.name.split('.').pop().toLowerCase();
      if (!ALLOWED_EXTENSIONS.includes(ext)) {
        setUploadError(`'${file.name}' is not supported. Only CSV and Excel (.xlsx, .xls) files are allowed.`);
        return;
      }
      if (file.size === 0) {
        setUploadError(`'${file.name}' is empty (0 bytes).`);
        return;
      }
      if (file.size > MAX_FILE_SIZE_BYTES) {
        setUploadError(`'${file.name}' exceeds the ${MAX_FILE_SIZE_GB}GB maximum file size limit.`);
        return;
      }
      if (!existingNames.has(file.name)) {
        valid.push(file);
      }
    }

    if (valid.length > 0) {
      setSelectedFiles(prev => [...prev, ...valid]);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndAddFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleChange = (e) => {
    if (e.target && e.target.files && e.target.files.length > 0) {
      validateAndAddFiles(Array.from(e.target.files));
    }
    if (e.target) {
      e.target.value = '';
    }
  };

  const removeFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
    setUploadError(null);
  };

  const clearAllFiles = () => {
    setSelectedFiles([]);
    setUploadError(null);
  };

  const formatBytes = (bytes) => {
    if (!bytes || bytes <= 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + (sizes[i] || 'B');
  };

  const totalBatchSize = selectedFiles.reduce((acc, f) => acc + (f?.size || 0), 0);

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      if (fileInputRef.current) {
        fileInputRef.current.click();
      }
      return;
    }

    setIsUploading(true);
    setUploadError(null);
    setUploadSuccess(null);
    setUploadProgress(10);
    setUploadStatusText(`Preparing to ingest ${selectedFiles.length} file(s)...`);

    try {
      if (typeof uploadDatasetFiles === 'function') {
        const uploadRes = await uploadDatasetFiles(selectedFiles, (prog) => {
          setUploadProgress(prog?.percent || 50);
          setUploadStatusText(`Ingesting file ${prog?.current || 1} of ${prog?.total || selectedFiles.length}: ${prog?.file || ''}`);
        });

        const resList = uploadRes?.results || (Array.isArray(uploadRes) ? uploadRes : [uploadRes]);
        const failed = uploadRes?.failedFiles || [];

        setUploadProgress(100);
        if (failed.length > 0) {
          setUploadSuccess(`Ingested ${resList.length} file(s). Warning: ${failed.length} encountered issues.`);
        } else {
          setUploadSuccess(`Successfully ingested dataset! Switching active view...`);
        }
      }

      setTimeout(() => {
        handleClose();
      }, 1200);
    } catch (err) {
      setUploadError(err.message || 'Failed to upload dataset files.');
      setUploadProgress(0);
    } finally {
      setIsUploading(false);
    }
  };

  const handleClose = () => {
    if (isUploading) return;
    setSelectedFiles([]);
    setUploadError(null);
    setUploadSuccess(null);
    setUploadProgress(0);
    setUploadStatusText('');
    setActiveModal(null);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="w-full max-w-xl bg-surface-container-low border border-outline-variant/40 shadow-2xl flex flex-col font-data-mono my-auto">
        {/* Header */}
        <div className="h-13 px-5 bg-surface-container-high border-b border-outline-variant/30 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-primary/20 border border-primary/40 text-primary flex items-center justify-center font-bold">
              <span className="material-symbols-outlined text-lg">upload_file</span>
            </div>
            <div>
              <h2 className="font-headline-sm text-sm font-bold text-on-surface">
                Ingest New Dataset
              </h2>
              <p className="text-[11px] text-outline">
                Upload CSV or Excel spreadsheets for automatic AI & ML analysis
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={handleClose}
            disabled={isUploading}
            className="w-7 h-7 flex items-center justify-center text-outline hover:text-on-surface disabled:opacity-30 transition-colors cursor-pointer"
          >
            <span className="material-symbols-outlined text-[18px]">close</span>
          </button>
        </div>

        {/* Body */}
        <div className="p-5 flex flex-col gap-4">
          {/* Format Info Banner */}
          <div className="flex items-center justify-between text-[11px] px-3 py-1.5 bg-surface-container-lowest border border-outline-variant/30 text-outline">
            <span className="flex items-center gap-1.5">
              <span className="material-symbols-outlined text-[15px] text-secondary">info</span>
              Supported: <strong>.csv, .xlsx, .xls</strong>
            </span>
            <span>Max Size: <strong>{MAX_FILE_SIZE_GB}GB per file</strong></span>
          </div>

          {/* Drag & Drop Zone */}
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => {
              if (fileInputRef.current) {
                fileInputRef.current.click();
              }
            }}
            className={`border-2 border-dashed p-7 flex flex-col items-center justify-center gap-3 cursor-pointer transition-all ${
              dragActive
                ? 'border-primary bg-primary-container/30 scale-[1.01]'
                : 'border-outline-variant/60 hover:border-primary/80 bg-surface-container-lowest'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".csv,.xlsx,.xls,text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel"
              onChange={handleChange}
              className="hidden"
            />
            <div className="w-12 h-12 bg-primary-container/60 border border-primary/50 flex items-center justify-center rounded-sm shadow-sm text-primary">
              <span className="material-symbols-outlined text-2xl">cloud_upload</span>
            </div>
            <div className="text-center flex flex-col items-center gap-1">
              <p className="text-xs font-semibold text-on-surface">
                Drag & drop your CSV or Excel dataset here
              </p>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  if (fileInputRef.current) {
                    fileInputRef.current.click();
                  }
                }}
                className="mt-1 px-4 py-1.5 bg-primary text-on-primary text-xs font-bold hover:bg-primary-fixed-dim transition-all rounded-sm shadow-sm flex items-center gap-1.5 cursor-pointer"
              >
                <span className="material-symbols-outlined text-[15px]">folder_open</span>
                <span>Browse Files</span>
              </button>
              <p className="text-[11px] text-outline mt-1">
                Click anywhere in this box to open file browser
              </p>
            </div>
          </div>

          {/* Selected Files List */}
          {selectedFiles.length > 0 && (
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between text-xs text-outline font-label-caps uppercase">
                <span>Selected File(s) ({selectedFiles.length})</span>
                <div className="flex items-center gap-3">
                  <span className="text-secondary font-semibold">Total: {formatBytes(totalBatchSize)}</span>
                  {!isUploading && (
                    <button
                      type="button"
                      onClick={clearAllFiles}
                      className="text-[11px] text-outline hover:text-anomaly underline transition-colors cursor-pointer"
                    >
                      Clear All
                    </button>
                  )}
                </div>
              </div>

              <div className="max-h-36 overflow-y-auto flex flex-col gap-1.5 border border-outline-variant/30 p-2 bg-surface-container-lowest">
                {selectedFiles.map((file, idx) => (
                  <div
                    key={`${file.name}-${idx}`}
                    className="flex items-center justify-between p-2 bg-surface-container border border-outline-variant/30 text-xs"
                  >
                    <div className="flex items-center gap-2 truncate max-w-[340px]">
                      <span className="material-symbols-outlined text-[16px] text-primary">description</span>
                      <span className="font-semibold text-on-surface truncate" title={file.name}>{file.name}</span>
                      <span className="text-[10px] text-outline bg-surface-container-lowest px-1.5 py-0.5 border border-outline-variant/20">
                        {formatBytes(file.size)}
                      </span>
                    </div>
                    {!isUploading && (
                      <button
                        type="button"
                        onClick={(e) => { e.stopPropagation(); removeFile(idx); }}
                        className="text-outline hover:text-anomaly transition-colors p-1"
                        title="Remove file"
                      >
                        <span className="material-symbols-outlined text-[16px]">delete</span>
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Upload Progress Bar */}
          {isUploading && (
            <div className="flex flex-col gap-1.5 p-3 bg-surface-container-lowest border border-outline-variant/40">
              <div className="flex items-center justify-between text-xs font-semibold text-on-surface">
                <span className="truncate max-w-[320px]">{uploadStatusText || 'Ingesting dataset...'}</span>
                <span className="text-secondary">{uploadProgress}%</span>
              </div>
              <div className="w-full bg-surface-container-high h-2 overflow-hidden rounded-sm">
                <div
                  className="bg-primary h-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
            </div>
          )}

          {/* Error Banner */}
          {uploadError && (
            <div className="p-3 bg-red-500/10 border border-red-500/50 flex items-start gap-2.5 text-xs text-red-400">
              <span className="material-symbols-outlined text-[18px] shrink-0 mt-0.5">error</span>
              <div className="flex-1 leading-relaxed">{uploadError}</div>
            </div>
          )}

          {/* Success Banner */}
          {uploadSuccess && (
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/50 flex items-center gap-2.5 text-xs text-emerald-400">
              <span className="material-symbols-outlined text-[18px] shrink-0">check_circle</span>
              <div className="flex-1 font-semibold">{uploadSuccess}</div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="h-14 px-5 bg-surface-container-high border-t border-outline-variant/30 flex items-center justify-between">
          <button
            type="button"
            onClick={handleClose}
            disabled={isUploading}
            className="px-4 py-1.5 bg-surface-container hover:bg-surface-container-highest border border-outline-variant/40 text-xs font-headline-sm transition-colors disabled:opacity-40 cursor-pointer"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleUpload}
            disabled={isUploading}
            className="px-5 py-1.5 bg-primary text-on-primary font-semibold text-xs font-headline-sm hover:bg-primary-fixed-dim transition-colors flex items-center gap-1.5 disabled:opacity-40 cursor-pointer shadow-sm active:scale-95"
          >
            <span className="material-symbols-outlined text-[16px]">
              {isUploading ? 'sync' : (selectedFiles.length === 0 ? 'folder_open' : 'upload')}
            </span>
            <span>
              {isUploading
                ? 'Ingesting...'
                : (selectedFiles.length === 0
                    ? 'Select File to Upload'
                    : `Upload & Ingest (${selectedFiles.length})`
                  )
              }
            </span>
          </button>
        </div>
      </div>
    </div>
  );
};
