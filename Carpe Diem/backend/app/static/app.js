/**
 * Intelligent Data Analysis Platform — Person 1 Frontend Engine
 * Handles dataset upload, overview, schema detection, cleaning,
 * statistical metrics, correlations, and outlier analysis.
 */

// State
let currentDatasetId = null;
let currentDatasetOverview = null;
let currentSchema = null;
let currentCleaningReport = null;
let currentAnalysis = null;
let currentCorrelations = null;
let currentOutliers = null;
let statsFilter = "all";

const API_BASE = "";

// DOM Elements
const apiStatusBadge = document.getElementById("apiStatusBadge");
const apiStatusText = document.getElementById("apiStatusText");
const demoDataBtn = document.getElementById("demoDataBtn");
const fileInput = document.getElementById("fileInput");
const browseBtn = document.getElementById("browseBtn");
const dropzone = document.getElementById("dropzone");
const uploadProgressBox = document.getElementById("uploadProgressBox");
const uploadProgressBar = document.getElementById("uploadProgressBar");
const uploadProgressText = document.getElementById("uploadProgressText");
const uploadErrorAlert = document.getElementById("uploadErrorAlert");
const activeDatasetBar = document.getElementById("activeDatasetBar");
const activeDatasetFilename = document.getElementById("activeDatasetFilename");
const activeDatasetId = document.getElementById("activeDatasetId");
const barRowCount = document.getElementById("barRowCount");
const barColCount = document.getElementById("barColCount");
const barMissingCount = document.getElementById("barMissingCount");
const recleanBtn = document.getElementById("recleanBtn");
const dashboardSection = document.getElementById("dashboardSection");

// Initialize on DOM Ready
document.addEventListener("DOMContentLoaded", () => {
  checkHealth();
  setupUploadEvents();
  setupTabEvents();
  setupStatsFilterEvents();
  setupCorrelationEvents();
  setupOutlierEvents();
});

// ---------------------------------------------------------------------------
// 1. Health Check
// ---------------------------------------------------------------------------
async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (res.ok) {
      apiStatusText.textContent = "Backend Active";
      apiStatusBadge.style.borderColor = "rgba(16, 185, 129, 0.3)";
    } else {
      apiStatusText.textContent = "API Error";
      apiStatusBadge.style.borderColor = "rgba(239, 68, 68, 0.3)";
    }
  } catch {
    apiStatusText.textContent = "Backend Offline";
    apiStatusBadge.style.borderColor = "rgba(239, 68, 68, 0.3)";
  }
}

// ---------------------------------------------------------------------------
// 2. Upload Handlers
// ---------------------------------------------------------------------------
function setupUploadEvents() {
  browseBtn.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      handleFileUpload(e.target.files[0]);
    }
  });

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dragover");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  });

  demoDataBtn.addEventListener("click", loadDemoDataset);
  recleanBtn.addEventListener("click", () => {
    if (currentDatasetId) {
      fetchCleaningReport(currentDatasetId, true);
    }
  });

  const exportCsv = document.getElementById("exportCsvBtn");
  if (exportCsv) {
    exportCsv.addEventListener("click", () => {
      if (currentDatasetId) window.open(`${API_BASE}/dataset/${currentDatasetId}/export?format=csv`, "_blank");
    });
  }
  const exportXlsx = document.getElementById("exportXlsxBtn");
  if (exportXlsx) {
    exportXlsx.addEventListener("click", () => {
      if (currentDatasetId) window.open(`${API_BASE}/dataset/${currentDatasetId}/export?format=xlsx`, "_blank");
    });
  }
}

async function handleFileUpload(file) {
  hideError();
  showUploadProgress("Uploading and parsing dataset...");
  setProgressBar(30);

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch(`${API_BASE}/upload`, {
      method: "POST",
      body: formData,
    });

    setProgressBar(75);

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to upload dataset.");
    }

    const data = await res.json();
    setProgressBar(100);
    setTimeout(() => {
      hideUploadProgress();
      initDatasetDashboard(data.dataset_id, data.filename, data.rows, data.columns);
    }, 400);
  } catch (err) {
    hideUploadProgress();
    showError(err.message);
  }
}

async function loadDemoDataset() {
  hideError();
  showUploadProgress("Generating sample dirty e-commerce dataset...");
  setProgressBar(40);

  const sampleCsv = `customer_id,customer_name,age,gender,city,state,product,category,quantity,unit_price,total_sales,discount,payment_method,order_date,customer_rating,delivery_days,customer_feedback
CUST0697,Navya Gupta,28,FEMALE,Bhopal,Madhya Pradesh,Sofa Cover,HOME & KITCHEN,5,666.62,2863.14,14 %,cash on delivery,2026-03-08,4.0,2.0,Average quality
CUST0668,Vivaan Desai,43,FEMALE,Bengaluru,Karnataka,Kurta,Fashion,2,1628.18,2917.7,10 %,cash on delivery,2026-01-21,4.0,15.0,Product stopped working after a week
CUST0064,Priya Rao,36,Male,Mumbai,Maharashtra,Smartwatch,Electronics ,2,10130 INR,17463,"14%",credit card,06-08-2026,3.0,3.0,Exactly as described
CUST0534,Pari Desai,30,FEMALE,Kolkata ,West Bengal,Face Cream,beauty,1,₹294,283.81,4 %,cash on delivery,03/10/2026,4.0,3.0,Average quality
CUST0067,Kavya Patel,32, Female , Kanpur ,Uttar Pradesh,Kurta,FASHION,3,1070.42,"₹ 2,842",12 %,Net Banking,05/07/2026,4.0,2.0,Not satisfied with quality
CUST0622,Nikhil Sharma,22,MALE,Chandigarh,Punjab,Pressure Cooker,HOME & KITCHEN,1,3803.19,3514,8,NET BANKING,2026-06-11,3.0,14.0,Product stopped working after a week
CUST0347,Aditya Agarwal,47,Female,Ahmedabad,Gujarat,Sofa Cover,HOME & KITCHEN,1,"₹1,246",1077.92,"14%",upi,24-02-2026,5.0,3.0,Very good product
CUST0491,Manoj Kumar,38,Female,Pune,Maharashtra,Television,electronics,2,24702.48,"₹48,812",1.2,DEBIT CARD,12/03/2026,4.0,7.0,Packaging could be better
CUST0761,Manoj Kumar,30,Female,BENGALURU,Karnataka,Smartwatch,Electronics,5,3053.56,14886.12,"2%",credit card,2026/09/22,4.0,1.0,Great gadget
CUST0066,Meera Malhotra,33,Female,Kanpur ,Uttar Pradesh,Dumbbell Set,Sports ,1,3342.3,2911.15,0,Net banking,16/09/2026,5.0,4.0,Delivery took too long
CUST0068,Sanjay Rao,43, Female ,kanpur,Uttar Pradesh,Headphones,ELECTRONICS,1,"5,963",5432.67,9 %,DEBIT CARD,2026/05/27,4.0,30.0,Exactly as described
CUST0328,Pari Bhat,41,FEMALE,coimbatore,Tamil Nadu,Pressure Cooker, Home & Kitchen ,1,"₹ 2,536",55000.0,"5%",Credit Card,2026/07/12,3.0,5.0,Delivery took too long
CUST0611,Divya Reddy,46,Male, Nagpur ,Maharashtra,Headphones,electronics,1,"2,500",2295.09,8%,Net Banking,26/05/2026,5.0,3.0,Okay-ish
CUST0999,Test Outlier,95,Male,Mumbai,Maharashtra,Smartwatch,Electronics,20,99999,1999980,50%,credit card,2026-01-01,1.0,180.0,Extreme outlier record`;

  const blob = new Blob([sampleCsv], { type: "text/csv" });
  const file = new File([blob], "sample_ecommerce_dirty.csv", { type: "text/csv" });
  handleFileUpload(file);
}

function showUploadProgress(text) {
  uploadProgressBox.classList.remove("hidden");
  uploadProgressText.textContent = text;
}

function hideUploadProgress() {
  uploadProgressBox.classList.add("hidden");
  setProgressBar(0);
}

function setProgressBar(pct) {
  uploadProgressBar.style.width = `${pct}%`;
}

function showError(msg) {
  uploadErrorAlert.textContent = msg;
  uploadErrorAlert.classList.remove("hidden");
}

function hideError() {
  uploadErrorAlert.classList.add("hidden");
  uploadErrorAlert.textContent = "";
}

// ---------------------------------------------------------------------------
// 3. Pipeline Orchestration & Tab Management
// ---------------------------------------------------------------------------
async function initDatasetDashboard(datasetId, filename, rows, cols) {
  currentDatasetId = datasetId;
  activeDatasetFilename.textContent = filename;
  activeDatasetId.textContent = `ID: ${datasetId.slice(0, 8)}...`;
  barRowCount.textContent = rows;
  barColCount.textContent = cols;
  barMissingCount.textContent = "...";

  activeDatasetBar.classList.remove("hidden");
  dashboardSection.classList.remove("hidden");

  // Mark ribbons
  document.querySelectorAll(".step-ribbon-item").forEach((el) => {
    el.classList.remove("active");
    el.classList.add("completed");
  });
  document.querySelector('.step-ribbon-item[data-step="2"]').classList.add("active");

  // Fetch all endpoints concurrently
  fetchOverview(datasetId);
  fetchSchema(datasetId);
  fetchCleaningReport(datasetId);
  fetchAnalysis(datasetId);
  fetchCorrelations(datasetId);
  fetchOutliers(datasetId);
  fetchInsights(datasetId);
  fetchVisualizations(datasetId);
}

function setupTabEvents() {
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));

      btn.classList.add("active");
      const targetId = btn.getAttribute("data-tab");
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.add("active");
      }
    });
  });
}

// ---------------------------------------------------------------------------
// 4. Feature 1: Overview
// ---------------------------------------------------------------------------
async function fetchOverview(id) {
  try {
    const res = await fetch(`${API_BASE}/dataset/${id}/overview`);
    if (!res.ok) throw new Error("Could not fetch overview.");
    const data = await res.json();
    currentDatasetOverview = data;

    document.getElementById("kpiRows").textContent = data.rows.toLocaleString();
    document.getElementById("kpiCols").textContent = data.columns.toLocaleString();
    document.getElementById("kpiMissing").textContent = data.missing_values.toLocaleString();
    document.getElementById("kpiDuplicates").textContent = data.duplicate_rows.toLocaleString();
    
    // Format memory
    const mb = (data.memory_usage_bytes / (1024 * 1024)).toFixed(2);
    document.getElementById("kpiMemory").textContent = `${mb} MB`;
    barMissingCount.textContent = data.missing_values.toLocaleString();

    // Render Preview Table
    renderPreviewTable(data.column_names, data.preview_rows);
  } catch (err) {
    console.error("Overview error:", err);
  }
}

function renderPreviewTable(columns, rows) {
  const container = document.getElementById("previewTableContainer");
  if (!rows || rows.length === 0) {
    container.innerHTML = '<p class="section-desc">No preview rows available.</p>';
    return;
  }

  let html = '<table class="data-table"><thead><tr>';
  columns.forEach((c) => {
    html += `<th>${escapeHtml(c)}</th>`;
  });
  html += "</tr></thead><tbody>";

  rows.forEach((row) => {
    html += "<tr>";
    columns.forEach((c) => {
      const val = row[c] !== null && row[c] !== undefined ? row[c] : '<em style="color:var(--text-muted)">null</em>';
      html += `<td>${val}</td>`;
    });
    html += "</tr>";
  });

  html += "</tbody></table>";
  container.innerHTML = html;
}

// ---------------------------------------------------------------------------
// 5. Feature 2: Column-Type Schema Detection
// ---------------------------------------------------------------------------
async function fetchSchema(id) {
  try {
    const res = await fetch(`${API_BASE}/dataset/${id}/schema`);
    if (!res.ok) throw new Error("Could not fetch schema.");
    const data = await res.json();
    currentSchema = data;
    renderSchemaTable(data.columns);
  } catch (err) {
    console.error("Schema error:", err);
  }
}

function renderSchemaTable(columns) {
  const tbody = document.getElementById("schemaTableBody");
  tbody.innerHTML = "";

  columns.forEach((col) => {
    const tr = document.createElement("tr");
    const confPct = Math.round(col.confidence * 100);

    tr.innerHTML = `
      <td><strong>${escapeHtml(col.name)}</strong></td>
      <td><span class="type-pill type-${col.type}">${col.type}</span></td>
      <td>
        <div style="display:flex; align-items:center; gap:8px;">
          <span>${confPct}%</span>
          <div style="width:50px; height:4px; background:var(--bg-elevated); border-radius:4px; overflow:hidden;">
            <div style="width:${confPct}%; height:100%; background:var(--accent-primary)"></div>
          </div>
        </div>
      </td>
      <td><code>${escapeHtml(col.original_dtype)}</code></td>
      <td>${col.unique_count.toLocaleString()}</td>
      <td>${col.null_count.toLocaleString()}</td>
    `;
    tbody.appendChild(tr);
  });
}

// ---------------------------------------------------------------------------
// 6. Feature 3: Automatic Data Cleaning Report
// ---------------------------------------------------------------------------
async function fetchCleaningReport(id, forceReclean = false) {
  try {
    const url = forceReclean 
      ? `${API_BASE}/dataset/${id}/cleaning-report?reclean=true`
      : `${API_BASE}/dataset/${id}/cleaning-report`;
    const res = await fetch(url);
    if (!res.ok) throw new Error("Could not fetch cleaning report.");
    const data = await res.json();
    currentCleaningReport = data;

    document.getElementById("cleanRowsCount").textContent = data.cleaned_row_count.toLocaleString();
    document.getElementById("cleanOriginalRows").textContent = `Raw: ${data.original_row_count.toLocaleString()}`;
    document.getElementById("cleanDuplicatesCount").textContent = data.duplicates_removed.toLocaleString();
    document.getElementById("cleanMissingHandled").textContent = data.missing_values_handled.toLocaleString();
    document.getElementById("cleanCurrencyCount").textContent = (data.currency_conversions + data.numeric_conversions).toLocaleString();
    document.getElementById("cleanCasingCount").textContent = (data.capitalization_fixes + data.whitespace_fixes).toLocaleString();
    document.getElementById("cleanDateCount").textContent = data.date_conversions.toLocaleString();

    // Render Warnings
    const alertsContainer = document.getElementById("cleaningAlertsContainer");
    alertsContainer.innerHTML = "";
    if (data.warnings && data.warnings.length > 0) {
      data.warnings.forEach((w) => {
        const div = document.createElement("div");
        div.className = "alert-box warning";
        div.innerHTML = `⚠️ <strong>Notice:</strong> ${escapeHtml(w)}`;
        alertsContainer.appendChild(div);
      });
    }

    // Render Operations Table
    renderCleaningOperationsTable(data.operations);
  } catch (err) {
    console.error("Cleaning report error:", err);
  }
}

function renderCleaningOperationsTable(ops) {
  const tbody = document.getElementById("cleaningOperationsBody");
  tbody.innerHTML = "";

  if (!ops || ops.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:var(--text-muted)">No transformations required. Dataset was already clean.</td></tr>';
    return;
  }

  ops.forEach((op) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><span class="badge badge-info">${escapeHtml(op.operation)}</span></td>
      <td>${op.column ? `<strong>${escapeHtml(op.column)}</strong>` : '<em style="color:var(--text-muted)">Dataset-level</em>'}</td>
      <td>${op.affected_rows.toLocaleString()}</td>
      <td><code>${escapeHtml(op.method || "standard")}</code></td>
      <td>${escapeHtml(op.details || "-")}</td>
    `;
    tbody.appendChild(tr);
  });
}

// ---------------------------------------------------------------------------
// 7. Feature 4: Statistical Analysis
// ---------------------------------------------------------------------------
function setupStatsFilterEvents() {
  const group = document.getElementById("statsFilterGroup");
  group.querySelectorAll(".btn-filter").forEach((btn) => {
    btn.addEventListener("click", () => {
      group.querySelectorAll(".btn-filter").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      statsFilter = btn.getAttribute("data-filter");
      renderAnalysisCards();
    });
  });
}

async function fetchAnalysis(id) {
  try {
    const res = await fetch(`${API_BASE}/dataset/${id}/analysis`);
    if (!res.ok) throw new Error("Could not fetch analysis.");
    const data = await res.json();
    currentAnalysis = data;
    renderAnalysisCards();
  } catch (err) {
    console.error("Analysis error:", err);
  }
}

function renderAnalysisCards() {
  const grid = document.getElementById("statsCardsGrid");
  grid.innerHTML = "";

  if (!currentAnalysis) return;

  // 1. Numeric Cards
  if (statsFilter === "all" || statsFilter === "numeric") {
    Object.entries(currentAnalysis.numeric_analysis).forEach(([col, s]) => {
      const card = document.createElement("div");
      card.className = "stat-card";

      // Histogram visual
      let histHtml = "";
      if (s.histogram && s.histogram.length > 0) {
        const maxCount = Math.max(...s.histogram.map((b) => b.count), 1);
        histHtml = '<div class="dist-bars-container">';
        s.histogram.forEach((bin) => {
          const hPct = Math.round((bin.count / maxCount) * 100);
          histHtml += `<div class="dist-bar" style="height:${Math.max(hPct, 8)}%" data-tooltip="[${bin.bin_start} - ${bin.bin_end}]: ${bin.count}"></div>`;
        });
        histHtml += '</div><span class="section-desc" style="display:block; text-align:center;">Distribution Histogram</span>';
      }

      card.innerHTML = `
        <div class="stat-card-header">
          <span class="stat-card-title">${escapeHtml(col)}</span>
          <span class="type-pill type-numeric">Numeric</span>
        </div>
        <div class="stat-metrics-list">
          <div class="stat-metric-item"><span class="label">Mean:</span><span class="val">${s.mean ?? "-"}</span></div>
          <div class="stat-metric-item"><span class="label">Median:</span><span class="val">${s.median ?? "-"}</span></div>
          <div class="stat-metric-item"><span class="label">Std Dev:</span><span class="val">${s.std ?? "-"}</span></div>
          <div class="stat-metric-item"><span class="label">Min:</span><span class="val">${s.min ?? "-"}</span></div>
          <div class="stat-metric-item"><span class="label">Max:</span><span class="val">${s.max ?? "-"}</span></div>
          <div class="stat-metric-item"><span class="label">IQR:</span><span class="val">${s.iqr ?? "-"}</span></div>
          <div class="stat-metric-item"><span class="label">Skewness:</span><span class="val">${s.skewness ?? "-"}</span></div>
          <div class="stat-metric-item"><span class="label">Count:</span><span class="val">${s.count}</span></div>
        </div>
        ${histHtml}
      `;
      grid.appendChild(card);
    });
  }

  // 2. Categorical Cards
  if (statsFilter === "all" || statsFilter === "categorical") {
    Object.entries(currentAnalysis.categorical_analysis).forEach(([col, s]) => {
      const card = document.createElement("div");
      card.className = "stat-card";

      let catsHtml = "";
      if (s.top_categories && s.top_categories.length > 0) {
        catsHtml = '<div style="margin-top:0.75rem">';
        s.top_categories.slice(0, 5).forEach((cat) => {
          catsHtml += `
            <div class="cat-freq-bar-item">
              <div class="cat-freq-label-row">
                <span>${escapeHtml(cat.category)}</span>
                <strong>${cat.percentage}% (${cat.count})</strong>
              </div>
              <div class="cat-freq-track">
                <div class="cat-freq-fill" style="width:${cat.percentage}%"></div>
              </div>
            </div>
          `;
        });
        catsHtml += "</div>";
      }

      card.innerHTML = `
        <div class="stat-card-header">
          <span class="stat-card-title">${escapeHtml(col)}</span>
          <span class="type-pill type-categorical">Categorical</span>
        </div>
        <div class="stat-metrics-list">
          <div class="stat-metric-item"><span class="label">Unique Values:</span><span class="val">${s.unique_count}</span></div>
          <div class="stat-metric-item"><span class="label">Valid Count:</span><span class="val">${s.count}</span></div>
        </div>
        ${catsHtml}
      `;
      grid.appendChild(card);
    });
  }

  // 3. Datetime Cards
  if (statsFilter === "all" || statsFilter === "datetime") {
    Object.entries(currentAnalysis.datetime_analysis).forEach(([col, s]) => {
      const card = document.createElement("div");
      card.className = "stat-card";

      card.innerHTML = `
        <div class="stat-card-header">
          <span class="stat-card-title">${escapeHtml(col)}</span>
          <span class="type-pill type-datetime">DateTime</span>
        </div>
        <div class="stat-metrics-list">
          <div class="stat-metric-item"><span class="label">Earliest:</span><span class="val">${s.min_date ?? "-"}</span></div>
          <div class="stat-metric-item"><span class="label">Latest:</span><span class="val">${s.max_date ?? "-"}</span></div>
          <div class="stat-metric-item"><span class="label">Timespan:</span><span class="val">${s.range_days ?? 0} days</span></div>
          <div class="stat-metric-item"><span class="label">Recorded:</span><span class="val">${s.count}</span></div>
        </div>
      `;
      grid.appendChild(card);
    });
  }

  // 4. Text & Identifier Cards
  if (statsFilter === "all" || statsFilter === "text") {
    Object.entries(currentAnalysis.text_analysis).forEach(([col, s]) => {
      const card = document.createElement("div");
      card.className = "stat-card";
      card.innerHTML = `
        <div class="stat-card-header">
          <span class="stat-card-title">${escapeHtml(col)}</span>
          <span class="type-pill type-text">Text</span>
        </div>
        <div class="stat-metrics-list">
          <div class="stat-metric-item"><span class="label">Avg Words:</span><span class="val">${s.avg_word_count ?? "-"}</span></div>
          <div class="stat-metric-item"><span class="label">Avg Chars:</span><span class="val">${s.avg_char_length ?? "-"}</span></div>
          <div class="stat-metric-item"><span class="label">Unique Texts:</span><span class="val">${s.unique_count}</span></div>
          <div class="stat-metric-item"><span class="label">Total Count:</span><span class="val">${s.count}</span></div>
        </div>
      `;
      grid.appendChild(card);
    });

    Object.entries(currentAnalysis.identifier_analysis).forEach(([col, s]) => {
      const card = document.createElement("div");
      card.className = "stat-card";
      const uPct = Math.round(s.uniqueness_ratio * 100);
      card.innerHTML = `
        <div class="stat-card-header">
          <span class="stat-card-title">${escapeHtml(col)}</span>
          <span class="type-pill type-identifier">Identifier</span>
        </div>
        <div class="stat-metrics-list">
          <div class="stat-metric-item"><span class="label">Distinct IDs:</span><span class="val">${s.unique_count}</span></div>
          <div class="stat-metric-item"><span class="label">Uniqueness:</span><span class="val">${uPct}%</span></div>
          <div class="stat-metric-item"><span class="label">Total Count:</span><span class="val">${s.count}</span></div>
        </div>
      `;
      grid.appendChild(card);
    });
  }
}

// ---------------------------------------------------------------------------
// 8. Feature 5: Correlations
// ---------------------------------------------------------------------------
function setupCorrelationEvents() {
  const sel = document.getElementById("corrMethodSelect");
  sel.addEventListener("change", () => {
    if (currentDatasetId) {
      fetchCorrelations(currentDatasetId, sel.value);
    }
  });
}

async function fetchCorrelations(id, method = "pearson") {
  try {
    const res = await fetch(`${API_BASE}/dataset/${id}/correlations?method=${method}`);
    if (!res.ok) throw new Error("Could not fetch correlations.");
    const data = await res.json();
    currentCorrelations = data;
    renderCorrelationsView(data);
  } catch (err) {
    console.error("Correlations error:", err);
  }
}

function renderCorrelationsView(data) {
  const container = document.getElementById("corrMatrixContainer");
  const posContainer = document.getElementById("strongPositiveContainer");
  const negContainer = document.getElementById("strongNegativeContainer");
  const pairsBody = document.getElementById("corrPairsBody");

  if (!data.matrix || data.matrix.length === 0) {
    container.innerHTML = `<p class="section-desc">${escapeHtml(data.message || "No continuous numeric columns available for correlation analysis.")}</p>`;
    posContainer.innerHTML = '<span class="section-desc">None detected</span>';
    negContainer.innerHTML = '<span class="section-desc">None detected</span>';
    pairsBody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:var(--text-muted)">No pairs available.</td></tr>';
    return;
  }

  // 1. Heatmap Table
  const cols = data.numeric_columns;
  let html = '<table class="corr-grid-table"><thead><tr><th></th>';
  cols.forEach((c) => {
    html += `<th>${escapeHtml(c)}</th>`;
  });
  html += "</tr></thead><tbody>";

  data.matrix.forEach((row, rIdx) => {
    html += `<tr><th>${escapeHtml(cols[rIdx])}</th>`;
    row.forEach((val, cIdx) => {
      let bg = "rgba(30, 41, 59, 0.4)";
      let textColor = "#f8fafc";
      if (val !== null) {
        if (val > 0) {
          const alpha = Math.min(Math.abs(val), 0.9);
          bg = `rgba(6, 182, 212, ${alpha})`;
        } else if (val < 0) {
          const alpha = Math.min(Math.abs(val), 0.9);
          bg = `rgba(239, 68, 68, ${alpha})`;
        }
      }
      const disp = val !== null ? val.toFixed(2) : "-";
      html += `<td class="corr-cell" style="background:${bg}; color:${textColor}" title="${cols[rIdx]} vs ${cols[cIdx]}: r = ${disp}">${disp}</td>`;
    });
    html += "</tr>";
  });
  html += "</tbody></table>";
  container.innerHTML = html;

  // 2. Strong Positive List
  posContainer.innerHTML = "";
  if (data.strong_positive && data.strong_positive.length > 0) {
    data.strong_positive.forEach((p) => {
      const div = document.createElement("div");
      div.className = "rel-item";
      div.innerHTML = `
        <span class="rel-pair">${escapeHtml(p.var1)} ↔ ${escapeHtml(p.var2)}</span>
        <span class="rel-badge positive">r = ${p.correlation}</span>
      `;
      posContainer.appendChild(div);
    });
  } else {
    posContainer.innerHTML = '<span class="section-desc">No strong positive associations (r ≥ 0.60).</span>';
  }

  // 3. Strong Negative List
  negContainer.innerHTML = "";
  if (data.strong_negative && data.strong_negative.length > 0) {
    data.strong_negative.forEach((p) => {
      const div = document.createElement("div");
      div.className = "rel-item";
      div.innerHTML = `
        <span class="rel-pair">${escapeHtml(p.var1)} ↔ ${escapeHtml(p.var2)}</span>
        <span class="rel-badge negative">r = ${p.correlation}</span>
      `;
      negContainer.appendChild(div);
    });
  } else {
    negContainer.innerHTML = '<span class="section-desc">No strong negative associations (r ≤ -0.60).</span>';
  }

  // 4. Pairs Table
  pairsBody.innerHTML = "";
  if (data.important_pairs && data.important_pairs.length > 0) {
    data.important_pairs.forEach((p) => {
      const tr = document.createElement("tr");
      const isPos = p.direction === "Positive";
      tr.innerHTML = `
        <td><strong>${escapeHtml(p.var1)}</strong></td>
        <td><strong>${escapeHtml(p.var2)}</strong></td>
        <td><code>${p.correlation}</code></td>
        <td><span class="badge ${isPos ? "badge-info" : "badge"}">${p.direction}</span></td>
        <td>${p.strength}</td>
      `;
      pairsBody.appendChild(tr);
    });
  } else {
    pairsBody.innerHTML = '<tr><td colspan="5" style="text-align:center">No significant pairs found.</td></tr>';
  }
}

// ---------------------------------------------------------------------------
// 9. Feature 5: Outlier Analysis
// ---------------------------------------------------------------------------
function setupOutlierEvents() {
  document.querySelectorAll("[data-outlier-method]").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("[data-outlier-method]").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const method = btn.getAttribute("data-outlier-method");
      if (currentDatasetId) {
        fetchOutliers(currentDatasetId, method);
      }
    });
  });
}

async function fetchOutliers(id, method = "all") {
  try {
    const res = await fetch(`${API_BASE}/dataset/${id}/outliers?method=${method}`);
    if (!res.ok) throw new Error("Could not fetch outliers.");
    const data = await res.json();
    currentOutliers = data;
    renderOutliersView(data);
  } catch (err) {
    console.error("Outliers error:", err);
  }
}

function renderOutliersView(data) {
  const totalPoints = document.getElementById("outlierTotalPoints");
  const rowsCount = document.getElementById("outlierRowsCount");
  const pct = document.getElementById("outlierPct");
  const grid = document.getElementById("outliersCardsGrid");

  totalPoints.textContent = data.summary.total_outlier_data_points.toLocaleString();
  rowsCount.textContent = data.summary.rows_with_outliers_count.toLocaleString();
  pct.textContent = `${data.summary.rows_with_outliers_percentage}%`;

  grid.innerHTML = "";

  // Column cards
  Object.entries(data.columns).forEach(([col, res]) => {
    const card = document.createElement("div");
    card.className = "outlier-col-card";

    let iqrHtml = "";
    if (res.iqr) {
      let samples = "";
      if (res.iqr.sample_outliers && res.iqr.sample_outliers.length > 0) {
        samples = '<div class="outlier-samples-box"><strong>Sample Outliers:</strong><br>' +
          res.iqr.sample_outliers.map((s) => `Row ${s.row_index}: <code>${s.value}</code>`).join(", ") +
          "</div>";
      }

      iqrHtml = `
        <div style="margin-bottom:1rem; border-bottom:1px solid var(--border-subtle); padding-bottom:0.75rem;">
          <h4 style="font-size:0.95rem; margin-bottom:0.5rem; color:var(--accent-amber)">IQR Rule (1.5 × IQR)</h4>
          <div class="stat-metrics-list">
            <div class="stat-metric-item"><span class="label">Outliers:</span><span class="val">${res.iqr.outlier_count} (${res.iqr.outlier_percentage}%)</span></div>
            <div class="stat-metric-item"><span class="label">Fences:</span><span class="val">[${res.iqr.lower_bound}, ${res.iqr.upper_bound}]</span></div>
          </div>
          ${samples}
        </div>
      `;
    }

    let zHtml = "";
    if (res.z_score) {
      zHtml = `
        <div>
          <h4 style="font-size:0.95rem; margin-bottom:0.5rem; color:var(--accent-rose)">Z-Score Cutoff (|z| > 3.0)</h4>
          <div class="stat-metrics-list">
            <div class="stat-metric-item"><span class="label">Outliers:</span><span class="val">${res.z_score.outlier_count} (${res.z_score.outlier_percentage}%)</span></div>
            <div class="stat-metric-item"><span class="label">Cutoffs:</span><span class="val">[${res.z_score.lower_bound}, ${res.z_score.upper_bound}]</span></div>
          </div>
        </div>
      `;
    }

    card.innerHTML = `
      <div class="stat-card-header">
        <span class="stat-card-title">${escapeHtml(col)}</span>
        <span class="badge ${res.iqr && res.iqr.outlier_count > 0 ? "badge-info" : ""}">
          ${(res.iqr ? res.iqr.outlier_count : 0)} Outliers
        </span>
      </div>
      ${iqrHtml}
      ${zHtml}
    `;
    grid.appendChild(card);
  });

  // Isolation Forest Summary Card
  if (data.isolation_forest) {
    const isoCard = document.createElement("div");
    isoCard.className = "outlier-col-card";
    isoCard.style.borderColor = "var(--accent-violet)";
    isoCard.innerHTML = `
      <div class="stat-card-header">
        <span class="stat-card-title">Isolation Forest (Multivariate)</span>
        <span class="type-pill type-text">Ensemble Anomaly</span>
      </div>
      <div class="stat-metrics-list">
        <div class="stat-metric-item"><span class="label">Contamination:</span><span class="val">${data.isolation_forest.contamination}</span></div>
        <div class="stat-metric-item"><span class="label">Anomalies:</span><span class="val">${data.isolation_forest.outlier_count}</span></div>
        <div class="stat-metric-item"><span class="label">Affected Rate:</span><span class="val">${data.isolation_forest.outlier_percentage}%</span></div>
      </div>
      <div class="outlier-samples-box">
        <strong>Flagged Row Indices:</strong><br>
        ${data.isolation_forest.affected_rows.slice(0, 20).join(", ")}${data.isolation_forest.affected_rows.length > 20 ? "..." : ""}
      </div>
    `;
    grid.prepend(isoCard);
  }
}

// ---------------------------------------------------------------------------
// 10. Feature 6: Executive Insights & Data Quality
// ---------------------------------------------------------------------------
async function fetchInsights(id) {
  try {
    const res = await fetch(`${API_BASE}/dataset/${id}/insights`);
    if (!res.ok) throw new Error("Could not fetch insights.");
    const data = await res.json();
    renderInsightsView(data);
  } catch (err) {
    console.error("Insights error:", err);
  }
}

function renderInsightsView(data) {
  const q = data.quality_score;
  const overall = document.getElementById("qualityOverallScore");
  const grade = document.getElementById("qualityGrade");
  const circle = document.getElementById("qualityScoreCircle");

  overall.textContent = q.overall_score;
  grade.textContent = `Grade: ${q.grade}`;
  document.getElementById("scoreCompleteness").textContent = q.completeness_score;
  document.getElementById("scoreUniqueness").textContent = q.uniqueness_score;
  document.getElementById("scoreValidity").textContent = q.validity_score;

  // Set ring color
  if (q.overall_score >= 85) {
    circle.style.borderColor = "var(--accent-emerald)";
    circle.style.boxShadow = "0 0 20px rgba(16, 185, 129, 0.35)";
  } else if (q.overall_score >= 70) {
    circle.style.borderColor = "var(--accent-amber)";
    circle.style.boxShadow = "0 0 20px rgba(245, 158, 11, 0.35)";
  } else {
    circle.style.borderColor = "var(--accent-danger)";
    circle.style.boxShadow = "0 0 20px rgba(239, 68, 68, 0.35)";
  }

  // Key Findings
  const findingsContainer = document.getElementById("findingsListContainer");
  findingsContainer.innerHTML = "";
  if (data.key_findings && data.key_findings.length > 0) {
    data.key_findings.forEach((f) => {
      const card = document.createElement("div");
      card.className = "finding-card";
      card.innerHTML = `
        <div class="finding-title">
          <span>${escapeHtml(f.title)}</span>
          <span class="finding-impact-pill impact-${f.impact}">${f.impact}</span>
        </div>
        <div class="finding-desc">${escapeHtml(f.description)}</div>
      `;
      findingsContainer.appendChild(card);
    });
  } else {
    findingsContainer.innerHTML = '<p class="section-desc">No prominent anomalies or patterns detected.</p>';
  }

  // Actionable Recommendations
  const recsContainer = document.getElementById("recommendationsListContainer");
  recsContainer.innerHTML = "";
  if (data.actionable_recommendations && data.actionable_recommendations.length > 0) {
    data.actionable_recommendations.forEach((r) => {
      const li = document.createElement("li");
      li.className = "recommendation-item";
      li.innerHTML = `
        <span class="rec-icon">⚡</span>
        <span>${escapeHtml(r)}</span>
      `;
      recsContainer.appendChild(li);
    });
  }
}

// ---------------------------------------------------------------------------
// 11. Feature 6: Visualizations & Charts
// ---------------------------------------------------------------------------
async function fetchVisualizations(id) {
  try {
    const res = await fetch(`${API_BASE}/dataset/${id}/visualizations`);
    if (!res.ok) throw new Error("Could not fetch visualizations.");
    const data = await res.json();
    renderVisualizationsView(data);
  } catch (err) {
    console.error("Visualizations error:", err);
  }
}

function renderVisualizationsView(data) {
  const grid = document.getElementById("visualizationsGrid");
  grid.innerHTML = "";

  if (!data.charts || data.charts.length === 0) {
    grid.innerHTML = '<p class="section-desc">No suitable visualization recommendations for this dataset structure.</p>';
    return;
  }

  data.charts.forEach((chart) => {
    const card = document.createElement("div");
    card.className = "chart-card";

    card.innerHTML = `
      <div class="chart-card-header">
        <h4>${escapeHtml(chart.title)}</h4>
        <p class="section-desc">${escapeHtml(chart.description)}</p>
      </div>
      <div class="chart-svg-container">
        ${renderSvgChart(chart)}
      </div>
    `;
    grid.appendChild(card);
  });
}

function renderSvgChart(chart) {
  const series = chart.series && chart.series[0] ? chart.series[0].data : [];
  if (!series || series.length === 0) {
    return '<span style="color:var(--text-muted)">Insufficient data</span>';
  }

  const width = 420;
  const height = 200;
  const padLeft = 45;
  const padRight = 20;
  const padTop = 20;
  const padBottom = 35;
  const plotWidth = width - padLeft - padRight;
  const plotHeight = height - padTop - padBottom;

  if (chart.chart_type === "bar") {
    const maxVal = Math.max(...series.map((d) => d.value), 1);
    const barWidth = Math.max(12, Math.min(36, Math.floor(plotWidth / series.length) - 8));
    const step = plotWidth / series.length;

    let bars = "";
    series.forEach((d, i) => {
      const barH = (d.value / maxVal) * plotHeight;
      const x = padLeft + (i * step) + ((step - barWidth) / 2);
      const y = padTop + (plotHeight - barH);
      const shortLabel = String(d.label).length > 8 ? String(d.label).slice(0, 7) + "…" : String(d.label);

      bars += `
        <rect x="${x}" y="${y}" width="${barWidth}" height="${barH}" rx="4" fill="url(#barGradient)">
          <title>${escapeHtml(String(d.label))}: ${d.value}</title>
        </rect>
        <text x="${x + barWidth / 2}" y="${height - 12}" fill="#94a3b8" font-size="9" text-anchor="middle">${escapeHtml(shortLabel)}</text>
        <text x="${x + barWidth / 2}" y="${Math.max(12, y - 4)}" fill="#cbd5e1" font-size="8.5" font-weight="600" text-anchor="middle">${d.value >= 1000 ? (d.value / 1000).toFixed(1) + "k" : d.value}</text>
      `;
    });

    return `
      <svg viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#06b6d4" />
            <stop offset="100%" stop-color="#6366f1" />
          </linearGradient>
        </defs>
        <line x1="${padLeft}" y1="${padTop + plotHeight}" x2="${width - padRight}" y2="${padTop + plotHeight}" stroke="rgba(255,255,255,0.12)" stroke-width="1" />
        ${bars}
      </svg>
    `;
  }

  if (chart.chart_type === "line") {
    const maxVal = Math.max(...series.map((d) => d.value), 1);
    const minVal = Math.min(...series.map((d) => d.value), 0);
    const valRange = Math.max(maxVal - minVal, 1);
    const step = plotWidth / Math.max(series.length - 1, 1);

    const points = series.map((d, i) => {
      const x = padLeft + (i * step);
      const y = padTop + plotHeight - (((d.value - minVal) / valRange) * plotHeight);
      return { x, y, label: d.label, val: d.value };
    });

    const pathD = points.map((p, i) => (i === 0 ? `M ${p.x} ${p.y}` : `L ${p.x} ${p.y}`)).join(" ");
    let dots = "";
    points.forEach((p) => {
      dots += `
        <circle cx="${p.x}" cy="${p.y}" r="4" fill="#06b6d4" stroke="#0f172a" stroke-width="2">
          <title>${p.label}: ${p.val}</title>
        </circle>
        <text x="${p.x}" y="${height - 12}" fill="#94a3b8" font-size="8.5" text-anchor="middle">${String(p.label).slice(-5)}</text>
      `;
    });

    return `
      <svg viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg">
        <line x1="${padLeft}" y1="${padTop + plotHeight}" x2="${width - padRight}" y2="${padTop + plotHeight}" stroke="rgba(255,255,255,0.12)" stroke-width="1" />
        <path d="${pathD}" fill="none" stroke="#6366f1" stroke-width="2.5" stroke-linecap="round" />
        ${dots}
      </svg>
    `;
  }

  if (chart.chart_type === "scatter") {
    const xVals = series.map((d) => d.value);
    const yVals = series.map((d) => d.secondary_value || 0);
    const minX = Math.min(...xVals);
    const maxX = Math.max(...xVals, minX + 1);
    const minY = Math.min(...yVals);
    const maxY = Math.max(...yVals, minY + 1);

    let dots = "";
    series.forEach((d) => {
      const sec = d.secondary_value || 0;
      const cx = padLeft + (((d.value - minX) / (maxX - minX)) * plotWidth);
      const cy = padTop + plotHeight - (((sec - minY) / (maxY - minY)) * plotHeight);
      dots += `
        <circle cx="${cx}" cy="${cy}" r="4.5" fill="#f43f5e" fill-opacity="0.8" stroke="#fff" stroke-width="1">
          <title>X: ${d.value}, Y: ${sec}</title>
        </circle>
      `;
    });

    return `
      <svg viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg">
        <rect x="${padLeft}" y="${padTop}" width="${plotWidth}" height="${plotHeight}" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1" />
        <text x="${padLeft}" y="${height - 8}" fill="#94a3b8" font-size="9">${minX.toFixed(0)}</text>
        <text x="${width - padRight}" y="${height - 8}" fill="#94a3b8" font-size="9" text-anchor="end">${maxX.toFixed(0)}</text>
        <text x="${padLeft - 6}" y="${padTop + plotHeight}" fill="#94a3b8" font-size="9" text-anchor="end">${minY.toFixed(0)}</text>
        <text x="${padLeft - 6}" y="${padTop + 10}" fill="#94a3b8" font-size="9" text-anchor="end">${maxY.toFixed(0)}</text>
        ${dots}
      </svg>
    `;
  }

  if (chart.chart_type === "donut") {
    const colors = ["#06b6d4", "#6366f1", "#10b981", "#f59e0b", "#f43f5e", "#8b5cf6", "#ec4899", "#64748b"];
    const total = series.reduce((acc, d) => acc + d.value, 0) || 1;
    let legend = "";
    let currentPct = 0;
    const slices = [];

    series.slice(0, 6).forEach((d, idx) => {
      const pct = Math.round((d.value / total) * 100);
      const col = colors[idx % colors.length];
      slices.push({ pct, col });
      legend += `
        <div style="display:flex; align-items:center; gap:6px; font-size:0.75rem; color:#cbd5e1; margin-bottom:3px;">
          <span style="width:8px; height:8px; border-radius:50%; background:${col};"></span>
          <span style="max-width:110px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${escapeHtml(String(d.label))}</span>
          <strong style="margin-left:auto;">${pct}%</strong>
        </div>
      `;
    });

    // Donut SVG circumference = 2 * PI * r = 2 * 3.14159 * 40 = 251.3
    const c = 251.3;
    let strokeOffset = 0;
    let circles = "";
    slices.forEach((s) => {
      const strokeLen = (s.pct / 100) * c;
      circles += `
        <circle cx="90" cy="100" r="40" fill="transparent" stroke="${s.col}" stroke-width="18"
          stroke-dasharray="${strokeLen} ${c - strokeLen}" stroke-dashoffset="${-strokeOffset}" />
      `;
      strokeOffset += strokeLen;
    });

    return `
      <div style="display:flex; align-items:center; width:100%; height:100%;">
        <svg viewBox="0 0 180 200" style="width:160px; height:180px;">
          ${circles}
          <text x="90" y="105" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">${total >= 1000 ? (total / 1000).toFixed(1) + "k" : total}</text>
        </svg>
        <div style="flex:1; padding-left:1rem; overflow-y:auto; max-height:160px;">
          ${legend}
        </div>
      </div>
    `;
  }

  // Fallback / Boxplot summary
  return `
    <div style="width:100%; padding:1rem; font-size:0.85rem;">
      <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
        <span>Min: <strong>${series[0]?.value ?? "-"}</strong></span>
        <span>Median: <strong>${series[2]?.value ?? "-"}</strong></span>
        <span>Max: <strong>${series[4]?.value ?? "-"}</strong></span>
      </div>
      <div style="width:100%; height:12px; background:var(--bg-elevated); border-radius:6px; position:relative; overflow:hidden;">
        <div style="position:absolute; left:25%; width:50%; height:100%; background:var(--accent-primary); opacity:0.8;"></div>
      </div>
      <div style="display:flex; justify-content:space-between; margin-top:6px; color:var(--text-muted); font-size:0.75rem;">
        <span>Q1: ${series[1]?.value ?? "-"}</span>
        <span>Q3: ${series[3]?.value ?? "-"}</span>
      </div>
    </div>
  `;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function escapeHtml(str) {
  if (typeof str !== "string") return str;
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
