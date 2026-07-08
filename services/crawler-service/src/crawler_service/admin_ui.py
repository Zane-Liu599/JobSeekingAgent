ADMIN_HTML = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Job Crawler Admin</title>
    <style>
      :root {
        color: #17202a;
        background: #f5f7fb;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }
      * { box-sizing: border-box; }
      body { margin: 0; background: #f5f7fb; }
      .shell { min-height: 100vh; display: grid; grid-template-columns: 300px 1fr; }
      aside { background: #101827; color: #f8fafc; padding: 22px; }
      main { padding: 28px; min-width: 0; }
      h1, h2 { margin: 0; }
      h1 { font-size: 1.55rem; }
      h2 { font-size: 1.05rem; margin-bottom: 14px; }
      label { display: grid; gap: 6px; font-size: 0.84rem; color: #526071; }
      input, select, textarea {
        width: 100%;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 10px 12px;
        background: #fff;
        color: #17202a;
        font: inherit;
      }
      textarea { min-height: 120px; resize: vertical; }
      .compact-textarea { min-height: 92px; }
      button, .link-button {
        border: 0;
        border-radius: 8px;
        padding: 10px 14px;
        background: #0f766e;
        color: #fff;
        font-weight: 700;
        cursor: pointer;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
      }
      button.secondary, .link-button.secondary { background: #334155; }
      button.danger { background: #b42318; }
      button:disabled { opacity: 0.55; cursor: wait; }
      .brand { display: grid; gap: 8px; margin-bottom: 24px; }
      .brand span { color: #94a3b8; line-height: 1.5; }
      .panel {
        background: #fff;
        border: 1px solid #dce5ef;
        border-radius: 8px;
        padding: 18px;
        box-shadow: 0 12px 26px rgba(15, 23, 42, 0.06);
      }
      .stack { display: grid; gap: 14px; }
      .grid { display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }
      .layout { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(360px, 0.9fr); gap: 18px; align-items: start; }
      .toolbar { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 14px; flex-wrap: wrap; }
      .jobs { display: grid; gap: 10px; max-height: 70vh; overflow: auto; padding-right: 4px; }
      .job-card {
        border: 1px solid #e2e8f0;
        background: #f8fafc;
        border-radius: 8px;
        padding: 12px;
        cursor: pointer;
        display: grid;
        grid-template-columns: auto minmax(0, 1fr);
        gap: 10px;
        align-items: start;
      }
      .job-card.active { border-color: #0f766e; background: #ecfdf5; }
      .job-card.selected { border-color: #2563eb; background: #eff6ff; }
      .job-select {
        width: 18px;
        height: 18px;
        margin-top: 2px;
        accent-color: #0f766e;
      }
      .job-summary { display: grid; gap: 5px; min-width: 0; }
      .job-title { font-weight: 800; }
      .muted { color: #64748b; font-size: 0.88rem; }
      .badge { display: inline-flex; width: fit-content; padding: 3px 8px; border-radius: 999px; background: #e2e8f0; color: #334155; font-size: 0.75rem; }
      .notice { color: #334155; background: #eaf2f8; border: 1px solid #cfe0ee; border-radius: 8px; padding: 10px 12px; }
      .error { color: #842029; background: #f8d7da; border-color: #f5c2c7; }
      .actions { display: flex; gap: 8px; flex-wrap: wrap; }
      .bulk-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        margin-bottom: 12px;
        padding: 10px 12px;
        border: 1px solid #dbe5f0;
        border-radius: 8px;
        background: #f8fafc;
      }
      .bulk-bar .muted { white-space: nowrap; }
      .small-button {
        padding: 7px 10px;
        font-size: 0.82rem;
      }
      .check-grid { display: flex; gap: 8px; flex-wrap: wrap; }
      .check-pill {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        border: 1px solid #cbd5e1;
        border-radius: 999px;
        padding: 8px 11px;
        background: #fff;
        color: #334155;
        font-size: 0.88rem;
        cursor: pointer;
      }
      .check-pill input { width: auto; }
      .empty { color: #64748b; padding: 22px; text-align: center; border: 1px dashed #cbd5e1; border-radius: 8px; }
      @media (max-width: 980px) {
        .shell, .layout { grid-template-columns: 1fr; }
        aside { position: static; }
      }
    </style>
  </head>
  <body>
    <div class="shell">
      <aside>
        <div class="brand">
          <h1>Job Crawler Admin</h1>
          <span>Private backend console for crawling, reviewing, and editing saved jobs.</span>
        </div>
        <div class="stack">
          <label>Admin token
            <input id="token" type="password" placeholder="Optional X-Crawler-Token" />
          </label>
          <button class="secondary" onclick="saveToken()">Save Token</button>
          <a class="link-button secondary" href="/docs" target="_blank" rel="noreferrer">API Docs</a>
        </div>
      </aside>
      <main class="stack">
        <section class="panel stack">
          <div class="toolbar">
            <div>
              <h2>Crawl Search Queue</h2>
              <div class="muted">Enter keywords, locations, and platforms here. The crawler will use this task payload instead of editing .env.</div>
            </div>
            <div class="actions">
              <button id="savePlan" class="secondary" onclick="saveCrawlPlan()">Save Plan</button>
              <button id="runBatch" onclick="crawlBatch()">Run Queue</button>
            </div>
          </div>
          <div class="grid">
            <label>Keywords, one per line
              <textarea id="keywordsList" class="compact-textarea" placeholder="software engineer&#10;backend engineer&#10;full stack developer"></textarea>
            </label>
            <label>Locations, one per line
              <textarea id="locationsList" class="compact-textarea" placeholder="Sydney&#10;Melbourne&#10;Remote"></textarea>
            </label>
          </div>
          <div class="stack">
            <label>Platforms</label>
            <div class="check-grid" id="platformList">
              <label class="check-pill"><input type="checkbox" value="linkedin" checked /> LinkedIn</label>
              <label class="check-pill"><input type="checkbox" value="indeed" checked /> Indeed</label>
              <label class="check-pill"><input type="checkbox" value="google" checked /> Google Jobs</label>
              <label class="check-pill"><input type="checkbox" value="seek" /> SEEK</label>
              <label class="check-pill"><input type="checkbox" value="glassdoor" /> Glassdoor</label>
              <label class="check-pill"><input type="checkbox" value="zip_recruiter" /> ZipRecruiter</label>
            </div>
            <div id="crawlerConfig" class="muted">Loading crawler configuration...</div>
          </div>
          <div id="message" class="notice" hidden></div>
        </section>

        <section class="layout">
          <div class="panel">
            <div class="toolbar">
              <div>
                <h2>Saved Jobs</h2>
                <div class="muted"><span id="count">0</span> loaded</div>
              </div>
              <div class="actions">
                <input id="filter" placeholder="Filter title, company, location" oninput="renderJobs()" />
                <button class="secondary" onclick="loadJobs()">Refresh</button>
              </div>
            </div>
            <div class="bulk-bar">
              <div class="muted"><span id="selectedCount">0</span> selected</div>
              <div class="actions">
                <button type="button" class="secondary small-button" onclick="selectVisibleJobs()">Select Visible</button>
                <button type="button" class="secondary small-button" onclick="clearSelectedJobs()">Clear</button>
                <button id="deleteSelectedButton" type="button" class="danger small-button" onclick="deleteSelectedJobs()" disabled>Delete Selected</button>
              </div>
            </div>
            <div id="jobs" class="jobs"></div>
          </div>

          <form class="panel stack" onsubmit="saveJob(event)">
            <div class="toolbar">
              <div>
                <h2>Job Detail</h2>
                <div id="selectedMeta" class="muted">Select a job to edit.</div>
              </div>
              <button id="deleteButton" type="button" class="danger" onclick="deleteJob()" disabled>Delete</button>
            </div>
            <input id="jobId" type="hidden" />
            <div class="grid">
              <label>Title <input id="title" required /></label>
              <label>Company <input id="company" required /></label>
              <label>Location <input id="jobLocation" /></label>
              <label>Employment Type <input id="employmentType" /></label>
              <label>Salary <input id="salary" /></label>
              <label>Status <input id="status" /></label>
              <label>Platform <input id="jobPlatform" /></label>
              <label>Match Score <input id="matchScore" type="number" step="0.01" /></label>
            </div>
            <label>Source URL <input id="jobUrl" /></label>
            <label>Official Apply URL <input id="officialApplyUrl" /></label>
            <label>Description / enrichment notes <textarea id="description"></textarea></label>
            <div class="actions">
              <button id="saveButton" disabled>Save Changes</button>
              <a id="sourceLink" class="link-button secondary" href="#" target="_blank" rel="noreferrer">Open Source</a>
              <a id="applyLink" class="link-button" href="#" target="_blank" rel="noreferrer">Open Apply</a>
            </div>
          </form>
        </section>
      </main>
    </div>

    <script>
      let jobs = [];
      let selectedId = null;
      let selectedJobIds = new Set();
      const crawlPlanKey = "crawlerSearchPlan";

      const fields = [
        "title", "company", "jobLocation", "employmentType", "salary", "status",
        "jobPlatform", "matchScore", "jobUrl", "officialApplyUrl", "description"
      ];

      function headers() {
        const token = localStorage.getItem("crawlerToken") || "";
        return {
          "Content-Type": "application/json",
          ...(token ? { "X-Crawler-Token": token } : {})
        };
      }

      function showMessage(text, isError = false) {
        const element = document.getElementById("message");
        element.textContent = text;
        element.hidden = false;
        element.className = isError ? "notice error" : "notice";
      }

      function saveToken() {
        localStorage.setItem("crawlerToken", document.getElementById("token").value);
        showMessage("Admin token saved in this browser.");
      }

      function saveCrawlPlan() {
        localStorage.setItem(crawlPlanKey, JSON.stringify(readCrawlPlan()));
        showMessage("Crawl plan saved in this browser.");
      }

      async function api(path, options = {}) {
        const response = await fetch(path, { ...options, headers: { ...headers(), ...(options.headers || {}) } });
        if (!response.ok) throw new Error(await response.text());
        return response.json();
      }

      async function loadJobs() {
        try {
          const data = await api("/jobs?limit=500");
          jobs = data.jobs || [];
          selectedJobIds = new Set(Array.from(selectedJobIds).filter(id => jobs.some(job => job.id === id)));
          document.getElementById("count").textContent = String(jobs.length);
          renderJobs();
          if (!selectedId && jobs[0]) selectJob(jobs[0].id);
        } catch (error) {
          showMessage(error.message || "Failed to load jobs.", true);
        }
      }

      function renderJobs() {
        const filter = document.getElementById("filter").value.toLowerCase();
        const container = document.getElementById("jobs");
        const filtered = jobs.filter(job => [job.title, job.company, job.location, job.platform, job.status].join(" ").toLowerCase().includes(filter));
        container.innerHTML = "";
        updateBulkActions();
        if (!filtered.length) {
          container.innerHTML = '<div class="empty">No jobs found.</div>';
          return;
        }
        for (const job of filtered) {
          const card = document.createElement("article");
          const isSelected = selectedJobIds.has(job.id);
          card.className = `job-card ${job.id === selectedId ? "active" : ""} ${isSelected ? "selected" : ""}`;
          card.onclick = () => selectJob(job.id);
          card.innerHTML = `
            <input class="job-select" type="checkbox" ${isSelected ? "checked" : ""} aria-label="Select ${escapeHtml(job.title || "job")}" />
            <div class="job-summary">
              <div class="job-title">${escapeHtml(job.title || "Untitled")}</div>
              <div>${escapeHtml(job.company || "Unknown company")}</div>
              <div class="muted">${escapeHtml([job.location, job.employment_type, job.salary].filter(Boolean).join(" · ") || "Details pending")}</div>
              <span class="badge">${escapeHtml(job.platform || "manual")} · ${escapeHtml(job.status || "found")}</span>
            </div>
          `;
          const checkbox = card.querySelector(".job-select");
          checkbox.onclick = event => event.stopPropagation();
          checkbox.onchange = () => toggleJobSelection(job.id, checkbox.checked);
          container.appendChild(card);
        }
      }

      function visibleJobIds() {
        const filter = document.getElementById("filter").value.toLowerCase();
        return jobs
          .filter(job => [job.title, job.company, job.location, job.platform, job.status].join(" ").toLowerCase().includes(filter))
          .map(job => job.id)
          .filter(Boolean);
      }

      function toggleJobSelection(id, checked) {
        if (!id) return;
        if (checked) selectedJobIds.add(id);
        else selectedJobIds.delete(id);
        updateBulkActions();
        renderJobs();
      }

      function selectVisibleJobs() {
        for (const id of visibleJobIds()) selectedJobIds.add(id);
        renderJobs();
      }

      function clearSelectedJobs() {
        selectedJobIds.clear();
        renderJobs();
      }

      function updateBulkActions() {
        document.getElementById("selectedCount").textContent = String(selectedJobIds.size);
        document.getElementById("deleteSelectedButton").disabled = selectedJobIds.size === 0;
      }

      async function selectJob(id) {
        try {
          const job = await api(`/jobs/${id}`);
          selectedId = job.id;
          document.getElementById("jobId").value = job.id || "";
          document.getElementById("title").value = job.title || "";
          document.getElementById("company").value = job.company || "";
          document.getElementById("jobLocation").value = job.location || "";
          document.getElementById("employmentType").value = job.employment_type || "";
          document.getElementById("salary").value = job.salary || "";
          document.getElementById("status").value = job.status || "";
          document.getElementById("jobPlatform").value = job.platform || "";
          document.getElementById("matchScore").value = job.match_score ?? "";
          document.getElementById("jobUrl").value = job.job_url || "";
          document.getElementById("officialApplyUrl").value = job.official_apply_url || "";
          document.getElementById("description").value = job.description || "";
          document.getElementById("selectedMeta").textContent = `#${job.id} · ${job.created_at || ""}`;
          document.getElementById("saveButton").disabled = false;
          document.getElementById("deleteButton").disabled = false;
          setLink("sourceLink", job.job_url);
          setLink("applyLink", job.official_apply_url || job.job_url);
          renderJobs();
        } catch (error) {
          showMessage(error.message || "Failed to load job.", true);
        }
      }

      async function saveJob(event) {
        event.preventDefault();
        const id = Number(document.getElementById("jobId").value);
        if (!id) return;
        const payload = {
          title: document.getElementById("title").value,
          company: document.getElementById("company").value,
          location: document.getElementById("jobLocation").value,
          employment_type: document.getElementById("employmentType").value,
          salary: document.getElementById("salary").value,
          status: document.getElementById("status").value || "found",
          platform: document.getElementById("jobPlatform").value || "manual",
          match_score: optionalNumber(document.getElementById("matchScore").value),
          job_url: document.getElementById("jobUrl").value,
          official_apply_url: document.getElementById("officialApplyUrl").value,
          description: document.getElementById("description").value
        };
        try {
          await api(`/jobs/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
          showMessage("Job saved.");
          await loadJobs();
          await selectJob(id);
        } catch (error) {
          showMessage(error.message || "Failed to save job.", true);
        }
      }

      async function deleteJob() {
        const id = Number(document.getElementById("jobId").value);
        if (!id || !confirm("Delete this job?")) return;
        try {
          await api(`/jobs/${id}`, { method: "DELETE" });
          showMessage("Job deleted.");
          selectedJobIds.delete(id);
          selectedId = null;
          clearForm();
          await loadJobs();
        } catch (error) {
          showMessage(error.message || "Failed to delete job.", true);
        }
      }

      async function deleteSelectedJobs() {
        const ids = Array.from(selectedJobIds);
        if (!ids.length || !confirm(`Delete ${ids.length} selected job(s)?`)) return;
        try {
          const result = await api("/jobs", { method: "DELETE", body: JSON.stringify({ job_ids: ids }) });
          showMessage(`Deleted ${result.deleted} job(s).`);
          if (selectedId && selectedJobIds.has(selectedId)) {
            selectedId = null;
            clearForm();
          }
          selectedJobIds.clear();
          await loadJobs();
        } catch (error) {
          showMessage(error.message || "Failed to delete selected jobs.", true);
        }
      }

      async function crawlBatch() {
        const payload = readCrawlPlan();
        if (!payload.keywords.length || !payload.locations.length || !payload.platforms.length) {
          showMessage("Please enter at least one keyword, one location, and one platform.", true);
          return;
        }
        setBusy(true);
        try {
          localStorage.setItem(crawlPlanKey, JSON.stringify(payload));
          const results = await api("/crawl/run", { method: "POST", body: JSON.stringify(payload) });
          const saved = results.reduce((total, item) => total + item.saved_count, 0);
          const found = results.reduce((total, item) => total + item.found_count, 0);
          showMessage(`Queue finished. Found ${found}, saved ${saved} result(s) across ${results.length} crawl(s).`);
          await loadJobs();
        } catch (error) {
          showMessage(error.message || "Crawl queue failed.", true);
        } finally {
          setBusy(false);
        }
      }

      async function loadConfig() {
        try {
          const config = await api("/config");
          document.getElementById("crawlerConfig").textContent = `Provider: ${config.provider || "auto"} · official apply only: ${config.official_apply_only ? "yes" : "no"}`;
          restoreCrawlPlan(config);
        } catch (error) {
          document.getElementById("crawlerConfig").textContent = "Could not load crawler configuration.";
        }
      }

      function readCrawlPlan() {
        return {
          keywords: parseLines(document.getElementById("keywordsList").value),
          locations: parseLines(document.getElementById("locationsList").value),
          platforms: Array.from(document.querySelectorAll("#platformList input:checked")).map(input => input.value)
        };
      }

      function restoreCrawlPlan(config) {
        const saved = JSON.parse(localStorage.getItem(crawlPlanKey) || "null");
        const plan = saved || {
          keywords: config.default_keywords || ["software engineer", "backend engineer"],
          locations: config.default_locations || ["Sydney", "Remote"],
          platforms: ["linkedin", "indeed", "google"]
        };
        document.getElementById("keywordsList").value = (plan.keywords || []).join("\\n");
        document.getElementById("locationsList").value = (plan.locations || []).join("\\n");
        const platforms = new Set(plan.platforms || []);
        for (const input of document.querySelectorAll("#platformList input")) {
          input.checked = platforms.has(input.value);
        }
      }

      function parseLines(value) {
        return value.split(/[\\n,]+/).map(item => item.trim()).filter(Boolean);
      }

      function clearForm() {
        for (const id of fields) document.getElementById(id).value = "";
        document.getElementById("jobId").value = "";
        document.getElementById("selectedMeta").textContent = "Select a job to edit.";
        document.getElementById("saveButton").disabled = true;
        document.getElementById("deleteButton").disabled = true;
      }

      function setBusy(value) {
        document.getElementById("runBatch").disabled = value;
        document.getElementById("savePlan").disabled = value;
      }

      function setLink(id, url) {
        const link = document.getElementById(id);
        if (url) {
          link.href = url;
          link.style.pointerEvents = "auto";
          link.style.opacity = "1";
        } else {
          link.href = "#";
          link.style.pointerEvents = "none";
          link.style.opacity = "0.45";
        }
      }

      function optionalNumber(value) {
        if (value === "") return null;
        const number = Number(value);
        return Number.isFinite(number) ? number : null;
      }

      function escapeHtml(value) {
        return String(value).replace(/[&<>"']/g, char => ({
          "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
        }[char]));
      }

      document.getElementById("token").value = localStorage.getItem("crawlerToken") || "";
      loadConfig();
      loadJobs();
    </script>
  </body>
</html>
"""
