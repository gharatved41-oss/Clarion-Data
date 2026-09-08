import React, { useState, useRef, useMemo } from 'react';
import { useTelemetry } from '../../context/TelemetryContext';

const MAX_FILE_SIZE_GB = 2;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_GB * 1024 * 1024 * 1024;
const MAX_FILE_COUNT = 1000; // Scaled to 1,000 files for maximum batch ingestion capacity
const ALLOWED_EXTENSIONS = ['csv', 'xlsx', 'xls'];

export const UploadDatasetModal = () => {
  const { activeModal, setActiveModal, uploadDatasetFiles } = useTelemetry();
  const [dragActive, setDragActive] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [fileFilterQuery, setFileFilterQuery] = useState('');
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

    if (selectedFiles.length + newFiles.length > MAX_FILE_COUNT) {
      setUploadError(`Maximum ${MAX_FILE_COUNT.toLocaleString()} files can be uploaded at once. Current selection: ${selectedFiles.length}, New files: ${newFiles.length}.`);
      return;
    }

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
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndAddFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndAddFiles(Array.from(e.target.files));
    }
    // reset input so same files can be reselected if removed
    e.target.value = null;
  };

  const removeFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
    setUploadError(null);
  };

  const clearAllFiles = () => {
    setSelectedFiles([]);
    setFileFilterQuery('');
    setUploadError(null);
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const totalBatchSize = selectedFiles.reduce((acc, f) => acc + f.size, 0);

  // Filtered files for performance view if batch size is large
  const filteredFiles = useMemo(() => {
    if (!fileFilterQuery.trim()) return selectedFiles;
    const q = fileFilterQuery.toLowerCase();
    return selectedFiles.filter(f => f.name.toLowerCase().includes(q));
  }, [selectedFiles, fileFilterQuery]);

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      setUploadError('Please choose or drop at least one dataset file.');
      return;
    }

    setIsUploading(true);
    setUploadError(null);
    setUploadSuccess(null);
    setUploadProgress(5);
    setUploadStatusText(`Preparing to ingest ${selectedFiles.length.toLocaleString()} file(s)...`);

    try {
      const uploadRes = await uploadDatasetFiles(selectedFiles, (prog) => {
        setUploadProgress(prog.percent);
        setUploadStatusText(`Ingesting file ${prog.current} of ${prog.total}: ${prog.file}`);
      });

      const resList = uploadRes?.results || uploadRes || [];
      const failed = uploadRes?.failedFiles || [];

      setUploadProgress(100);
      if (failed.length > 0) {
        setUploadSuccess(`Ingested ${resList.length} file(s). Warning: ${failed.length} file(s) encountered issues.`);
      } else {
        setUploadSuccess(`Successfully ingested all ${resList.length.toLocaleString()} dataset file(s). Active dataset switched.`);
      }

      setTimeout(() => {
        handleClose();
      }, 1400);
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
    setFileFilterQuery('');
    setUploadError(null);
    setUploadSuccess(null);
    setUploadProgress(0);
    setUploadStatusText('');
    setActiveModal(null);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 select-none font-body-md">
      <div className="w-full max-w-xl bg-surface-container-low border border-outline-variant/50 shadow-2xl flex flex-col font-data-mono animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="h-12 px-5 bg-surface-container-high border-b border-outline-variant/40 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-primary text-[20px]">upload_file</span>
            <span className="font-headline-sm text-sm font-semibold text-on-surface">
              Ingest Telemetry Datasets
            </span>
          </div>
          <button
            onClick={handleClose}
            disabled={isUploading}
            className="w-7 h-7 flex items-center justify-center text-outline hover:text-on-surface disabled:opacity-30 transition-colors"
          >
            <span className="material-symbols-outlined text-[18px]">close</span>
          </button>
        </div>

        {/* Body */}
        <div className="p-5 flex flex-col gap-4">
          {/* Maximum limits badge */}
          <div className="flex items-center justify-between text-[11px] px-3 py-1.5 bg-surface-container-lowest border border-outline-variant/30 text-outline">
            <span className="flex items-center gap-1.5">
              <span className="material-symbols-outlined text-[15px] text-secondary">info</span>
              Supported: <strong>.csv, .xlsx, .xls</strong>
            </span>
            <span>Limit: <strong>{MAX_FILE_SIZE_GB}GB/file</strong> • Max <strong>{MAX_FILE_COUNT.toLocaleString()} files/batch</strong></span>
          </div>

          {/* Drag & Drop Zone */}
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed p-6 flex flex-col items-center justify-center gap-2.5 cursor-pointer transition-all ${
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
            <div className="w-12 h-12 bg-primary-container/60 border border-primary/50 flex items-center justify-center rounded-sm shadow-sm">
              <span className="material-symbols-outlined text-primary text-2xl">cloud_upload</span>
            </div>
            <div className="text-center flex flex-col items-center gap-1">
              <p className="text-xs font-semibold text-on-surface">
                Drag & drop your dataset here, or click to browse
              </p>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  fileInputRef.current?.click();
                }}
                className="mt-1 px-3 py-1 bg-primary text-on-primary text-xs font-semibold hover:bg-primary-fixed-dim transition-colors rounded-sm shadow-sm flex items-center gap-1.5 cursor-pointer"
              >
                <span className="material-symbols-outlined text-[15px]">folder_open</span>
                <span>Browse Files</span>
              </button>
              <p className="text-[11px] text-outline mt-1">
                Supports CSV or Excel (.xlsx, .xls) up to {MAX_FILE_SIZE_GB}GB
              </p>
            </div>
          </div>

          {/* Selected Files List */}
          {selectedFiles.length > 0 && (
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between text-xs text-outline font-label-caps uppercase">
                <span className="flex items-center gap-2">
                  <span>Selected Datasets ({selectedFiles.length.toLocaleString()})</span>
                  {selectedFiles.length > 15 && (
                    <span className="text-[10px] text-outline/80 lowercase">
                      (showing {Math.min(filteredFiles.length, 100)})
                    </span>
                  )}
                </span>
                <div className="flex items-center gap-3">
                  <span className="text-secondary font-semibold">Total: {formatBytes(totalBatchSize)}</span>
                  {!isUploading && (
                    <button
                      type="button"
                      onClick={clearAllFiles}
                      className="text-[11px] text-outline hover:text-anomaly underline transition-colors cursor-pointer"
                      title="Clear all selected files"
                    >
                      Clear All
                    </button>
                  )}
                </div>
              </div>

              {/* Quick filter if list is long */}
              {selectedFiles.length > 15 && (
                <div className="relative">
                  <span className="material-symbols-outlined text-[14px] text-outline absolute left-2.5 top-1/2 -translate-y-1/2">
                    search
                  </span>
                  <input
                    type="text"
                    value={fileFilterQuery}
                    onChange={(e) => setFileFilterQuery(e.target.value)}
                    placeholder="Search in selected files..."
                    className="w-full bg-surface-container-lowest border border-outline-variant/30 pl-7 pr-3 py-1 text-xs text-on-surface focus:outline-none focus:border-primary placeholder:text-outline/60"
                  />
                </div>
              )}

              {/* Scrollable list with optimized DOM slice */}
              <div className="max-h-40 overflow-y-auto flex flex-col gap-1.5 border border-outline-variant/30 p-2 bg-surface-container-lowest">
                {filteredFiles.slice(0, 100).map((file, idx) => (
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
                        className="text-outline hover:text-anomaly transition-colors"
                        title="Remove file"
                      >
                        <span className="material-symbols-outlined text-[16px]">delete</span>
                      </button>
                    )}
                  </div>
                ))}

                {filteredFiles.length > 100 && (
                  <div className="text-center py-1.5 text-[11px] text-outline bg-surface-container-high/40 border border-dashed border-outline-variant/40">
                    ... and {(filteredFiles.length - 100).toLocaleString()} more files queued in batch
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Upload Progress Bar */}
          {isUploading && (
            <div className="flex flex-col gap-1.5 p-3 bg-surface-container-lowest border border-outline-variant/40">
              <div className="flex items-center justify-between text-xs font-semibold text-on-surface">
                <span className="truncate max-w-[320px]">{uploadStatusText || 'Ingesting files...'}</span>
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
            <div className="p-3 bg-anomaly/10 border border-anomaly/50 flex items-start gap-2.5 text-xs text-anomaly">
              <span className="material-symbols-outlined text-[18px] shrink-0 mt-0.5">error</span>
              <div className="flex-1 leading-relaxed">{uploadError}</div>
            </div>
          )}

          {/* Success Banner */}
          {uploadSuccess && (
            <div className="p-3 bg-tertiary-container/30 border border-tertiary/50 flex items-center gap-2.5 text-xs text-tertiary">
              <span className="material-symbols-outlined text-[18px] shrink-0">check_circle</span>
              <div className="flex-1 font-semibold">{uploadSuccess}</div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="h-14 px-5 bg-surface-container-high border-t border-outline-variant/30 flex items-center justify-between">
          <button
            onClick={handleClose}
            disabled={isUploading}
            className="px-4 py-1.5 bg-surface-container hover:bg-surface-container-highest border border-outline-variant/40 text-xs font-headline-sm transition-colors disabled:opacity-40 cursor-pointer"
          >
            Cancel
          </button>
          <button
            onClick={() => {
              if (selectedFiles.length === 0) {
                fileInputRef.current?.click();
              } else {
                handleUpload();
              }
            }}
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
                    : `Upload & Ingest (${selectedFiles.length.toLocaleString()})`
                  )
              }
            </span>
          </button>
        </div>
      </div>
    </div>
  );
};
