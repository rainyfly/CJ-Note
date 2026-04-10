---
name: llm-inference-research
description: |
  Produces structured, publication-quality HTML research reports on LLM inference topics and publishes them to a GitHub Pages site (rainyfly.github.io/CJ-Note/).

  USE THIS SKILL whenever the user wants to:
  - Analyze the architecture or source code of an inference framework (vLLM, TensorRT-LLM, SGLang, MLC-LLM, Triton, etc.)
  - Read, summarize, or deep-dive into an inference-related paper (from arXiv, GitHub, or a URL)
  - Explain how a specific inference acceleration feature works (e.g., PagedAttention, continuous batching, speculative decoding, flash attention, quantization, prefix caching)
  - Produce any written technical analysis of LLM serving, deployment, or runtime optimization
  - Update the CJ-Note homepage index with new reports

  The skill outputs a self-contained HTML file with embedded Chart.js charts and Mermaid diagrams, ready for GitHub Pages. It also keeps the index.html homepage up to date.

  Trigger on phrases like: "analyze vLLM", "read this paper", "explain speculative decoding", "write a report on...", "research TRT-LLM architecture", "summarize this inference feature", "add to my notes", "CJ-Note", etc.
---

# LLM Inference Research Skill

You are a senior LLM systems researcher. Your job is to produce well-researched, beautifully structured HTML reports on LLM inference technology and publish them to the user's GitHub Pages site at **rainyfly.github.io/CJ-Note/**.

---

## Step 1 — Understand the Task

Identify which of the three research modes applies:

| Mode | Trigger | Core goal |
|------|---------|-----------|
| **Repo Analysis** | "analyze X repo", "how does X work", "X architecture" | Understand repo structure, key abstractions, data flow, design decisions |
| **Paper Reading** | "read this paper", "summarize X paper", arXiv link | Extract contributions, key ideas, method details, results, and limitations |
| **Feature Deep Dive** | "explain X feature", "how does X acceleration work" | Explain the principle, engineering tradeoffs, implementation, and performance impact |

If ambiguous, ask the user to clarify with a one-line question before proceeding.

---

## Step 2 — Gather Information

Use whatever sources are relevant. Be thorough — a shallow report is worse than no report.

**For Repo Analysis:**
1. Clone or inspect the repo if you have access; otherwise use the GitHub web interface via WebFetch
2. Read key files: `README.md`, top-level directory structure, core modules
3. Trace the critical path (e.g., for an inference engine: request → tokenize → schedule → run → decode → response)
4. Look at issues/PRs for design rationale if helpful

**For Paper Reading:**
1. Fetch the paper (arXiv abstract + PDF, or URL provided by the user)
2. Read Abstract, Introduction, Method, Experiments, and Conclusion sections carefully
3. Note the core contribution, novel technique, experimental setup, and key results
4. Cross-reference with related work the paper cites

**For Feature Deep Dive:**
1. Find the original paper or design doc that introduced the feature
2. Find a concrete implementation in a real codebase (link to relevant file/function)
3. Explain both the theoretical motivation (why it's faster/better) and the engineering reality

**General research tips:**
- Use WebSearch and WebFetch to gather information from GitHub, arXiv, and technical blogs
- When reading source code, focus on the 20% of the code that does 80% of the interesting work
- Note version/commit hashes or paper dates so the report is clearly timestamped

---

## Step 3 — Write the Report

Save the report as an HTML file in the repo at:
```
/root/paddlejob/share-storage/gpfs/system-public/chenjian26/CJ-Note/reports/<slug>.html
```

Where `<slug>` is a concise kebab-case identifier, e.g., `vllm-architecture-2024.html`, `flash-attention-3.html`, `speculative-decoding-deep-dive.html`.

Use the HTML template below. It produces a self-contained file that renders on GitHub Pages without any build step.

### HTML Report Template

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>REPORT_TITLE — CJ-Note</title>
  <!-- Required meta tags — parsed by scripts/update_index.py to auto-update homepage -->
  <meta name="report-title" content="REPORT_TITLE">
  <meta name="report-type"  content="repo | paper | feature">
  <meta name="report-date"  content="YYYY-MM-DD">
  <meta name="report-tags"  content="Tag1, Tag2, Tag3">
  <meta name="report-desc"  content="One-sentence description shown on the homepage card.">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <style>
    :root {
      --bg: #0d1117; --surface: #161b22; --border: #30363d;
      --text: #e6edf3; --muted: #8b949e; --accent: #58a6ff;
      --green: #3fb950; --yellow: #d29922; --red: #f85149;
      --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
      --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: var(--bg); color: var(--text); font-family: var(--font-sans);
           line-height: 1.7; padding: 0 1rem; }
    .page-wrap { max-width: 900px; margin: 0 auto; padding: 2rem 0 4rem; }

    /* Header */
    .report-header { border-bottom: 1px solid var(--border); padding-bottom: 1.5rem; margin-bottom: 2rem; }
    .report-header h1 { font-size: 1.9rem; color: var(--accent); margin-bottom: .5rem; }
    .meta { color: var(--muted); font-size: .85rem; display: flex; gap: 1.5rem; flex-wrap: wrap; }
    .meta span::before { content: "• "; }
    .meta span:first-child::before { content: ""; }
    .back-link { display: inline-block; margin-bottom: 1rem; color: var(--muted);
                 text-decoration: none; font-size: .85rem; }
    .back-link:hover { color: var(--accent); }

    /* Sections */
    h2 { font-size: 1.3rem; color: var(--text); margin: 2.5rem 0 .8rem;
         padding-bottom: .4rem; border-bottom: 1px solid var(--border); }
    h3 { font-size: 1.05rem; color: var(--accent); margin: 1.5rem 0 .5rem; }
    h4 { font-size: .95rem; color: var(--muted); margin: 1rem 0 .3rem; text-transform: uppercase;
         letter-spacing: .05em; }
    p { margin-bottom: 1rem; color: var(--text); }

    /* TL;DR box */
    .tldr { background: var(--surface); border: 1px solid var(--accent);
            border-left: 4px solid var(--accent); border-radius: 6px;
            padding: 1rem 1.2rem; margin: 1.5rem 0; }
    .tldr h3 { color: var(--accent); margin: 0 0 .5rem; font-size: .9rem;
               text-transform: uppercase; letter-spacing: .1em; }
    .tldr ul { padding-left: 1.2rem; }
    .tldr li { margin-bottom: .3rem; }

    /* Key-value info grid */
    .info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                 gap: .75rem; margin: 1rem 0 1.5rem; }
    .info-card { background: var(--surface); border: 1px solid var(--border);
                 border-radius: 6px; padding: .8rem 1rem; }
    .info-card .label { font-size: .75rem; text-transform: uppercase; letter-spacing: .05em;
                        color: var(--muted); margin-bottom: .3rem; }
    .info-card .value { font-size: 1.1rem; font-weight: 600; color: var(--accent);
                        font-family: var(--font-mono); }

    /* Code blocks */
    pre { background: var(--surface); border: 1px solid var(--border); border-radius: 6px;
          padding: 1rem 1.2rem; overflow-x: auto; margin: 1rem 0; font-size: .85rem;
          font-family: var(--font-mono); line-height: 1.5; }
    code { background: var(--surface); border: 1px solid var(--border); border-radius: 3px;
           padding: .15em .4em; font-size: .85em; font-family: var(--font-mono); }
    pre code { background: none; border: none; padding: 0; }

    /* Tables */
    table { width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: .9rem; }
    th { background: var(--surface); color: var(--muted); font-weight: 600; text-align: left;
         padding: .6rem .8rem; border: 1px solid var(--border); font-size: .8rem;
         text-transform: uppercase; letter-spacing: .04em; }
    td { padding: .6rem .8rem; border: 1px solid var(--border); vertical-align: top; }
    tr:nth-child(even) td { background: rgba(255,255,255,.02); }

    /* Chart containers */
    .chart-wrap { background: var(--surface); border: 1px solid var(--border);
                  border-radius: 8px; padding: 1.2rem; margin: 1.2rem 0; }
    .chart-wrap h4 { color: var(--muted); font-size: .8rem; text-transform: uppercase;
                     letter-spacing: .05em; margin-bottom: .8rem; }
    .chart-wrap canvas { max-height: 320px; }

    /* Mermaid diagrams */
    .diagram-wrap { background: var(--surface); border: 1px solid var(--border);
                    border-radius: 8px; padding: 1.5rem; margin: 1.2rem 0;
                    overflow-x: auto; text-align: center; }
    .diagram-wrap h4 { color: var(--muted); font-size: .8rem; text-transform: uppercase;
                       letter-spacing: .05em; margin-bottom: 1rem; text-align: left; }

    /* Callout boxes */
    .callout { border-radius: 6px; padding: .8rem 1rem; margin: 1rem 0;
               border-left: 4px solid; }
    .callout.note { background: rgba(88,166,255,.07); border-color: var(--accent); }
    .callout.tip  { background: rgba(63,185,80,.07);  border-color: var(--green); }
    .callout.warn { background: rgba(210,153,34,.07); border-color: var(--yellow); }
    .callout.key  { background: rgba(248,81,73,.07);  border-color: var(--red); }
    .callout strong { display: block; margin-bottom: .3rem; font-size: .85rem;
                      text-transform: uppercase; letter-spacing: .04em; }

    /* Reference list */
    .refs ol { padding-left: 1.5rem; }
    .refs li { margin-bottom: .5rem; font-size: .9rem; color: var(--muted); }
    .refs a { color: var(--accent); }

    /* TOC */
    .toc { background: var(--surface); border: 1px solid var(--border); border-radius: 6px;
           padding: 1rem 1.2rem; margin: 0 0 2rem; font-size: .9rem; }
    .toc h3 { color: var(--muted); font-size: .8rem; text-transform: uppercase;
              letter-spacing: .1em; margin-bottom: .6rem; }
    .toc ol { padding-left: 1.3rem; }
    .toc li { margin-bottom: .25rem; }
    .toc a { color: var(--muted); text-decoration: none; }
    .toc a:hover { color: var(--accent); }

    /* Footer */
    .report-footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--border);
                     color: var(--muted); font-size: .8rem; display: flex; justify-content: space-between; }
  </style>
</head>
<body>
<div class="page-wrap">

  <a href="../index.html" class="back-link">← Back to CJ-Note</a>

  <header class="report-header">
    <h1>REPORT_TITLE</h1>
    <div class="meta">
      <span>TYPE: REPO_ANALYSIS | PAPER_READING | FEATURE_DEEP_DIVE</span>
      <span>DATE: YYYY-MM-DD</span>
      <span>TOPIC: e.g. Scheduling / Attention / Quantization</span>
    </div>
  </header>

  <!-- TL;DR -->
  <div class="tldr">
    <h3>TL;DR</h3>
    <ul>
      <li>Key finding 1</li>
      <li>Key finding 2</li>
      <li>Key finding 3</li>
    </ul>
  </div>

  <!-- Table of Contents -->
  <nav class="toc">
    <h3>Contents</h3>
    <ol>
      <li><a href="#background">Background</a></li>
      <li><a href="#architecture">Architecture / Method</a></li>
      <li><a href="#implementation">Implementation Details</a></li>
      <li><a href="#performance">Performance</a></li>
      <li><a href="#takeaways">Takeaways</a></li>
      <li><a href="#refs">References</a></li>
    </ol>
  </nav>

  <!-- ── 1. Background ──────────────────────────── -->
  <section id="background">
    <h2>1. Background</h2>
    <p>...</p>
  </section>

  <!-- ── 2. Architecture / Method ──────────────── -->
  <section id="architecture">
    <h2>2. Architecture / Method</h2>

    <!-- Mermaid diagram example -->
    <div class="diagram-wrap">
      <h4>Data Flow</h4>
      <div class="mermaid">
        graph LR
          A[Request] --> B[Scheduler]
          B --> C[KV Cache Manager]
          C --> D[Model Executor]
          D --> E[Sampler]
          E --> F[Response]
      </div>
    </div>

    <p>...</p>
  </section>

  <!-- ── 3. Implementation Details ─────────────── -->
  <section id="implementation">
    <h2>3. Implementation Details</h2>
    <p>...</p>
    <pre><code>// key code snippet with explanation</code></pre>
  </section>

  <!-- ── 4. Performance ─────────────────────────── -->
  <section id="performance">
    <h2>4. Performance</h2>

    <!-- Chart.js example -->
    <div class="chart-wrap">
      <h4>Throughput Comparison (tokens/s)</h4>
      <canvas id="perfChart"></canvas>
    </div>

    <p>...</p>
  </section>

  <!-- ── 5. Takeaways ───────────────────────────── -->
  <section id="takeaways">
    <h2>5. Takeaways</h2>
    <p>...</p>
  </section>

  <!-- ── References ─────────────────────────────── -->
  <section id="refs" class="refs">
    <h2>References</h2>
    <ol>
      <li><a href="...">Source 1</a></li>
    </ol>
  </section>

  <footer class="report-footer">
    <span>CJ-Note · LLM Inference Research</span>
    <span>Generated YYYY-MM-DD</span>
  </footer>
</div>

<script>
  // Initialize Mermaid with dark theme
  mermaid.initialize({ startOnLoad: true, theme: 'dark',
    themeVariables: { background: '#161b22', primaryColor: '#1f6feb',
                      primaryTextColor: '#e6edf3', lineColor: '#8b949e' }});

  // Example Chart.js chart — replace with actual data
  const ctx = document.getElementById('perfChart');
  if (ctx) {
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Baseline', 'Method A', 'Method B'],
        datasets: [{
          label: 'Throughput (tok/s)',
          data: [1000, 2400, 3100],
          backgroundColor: ['#30363d', '#1f6feb', '#58a6ff'],
          borderColor: ['#58a6ff', '#58a6ff', '#58a6ff'],
          borderWidth: 1, borderRadius: 4
        }]
      },
      options: {
        plugins: { legend: { labels: { color: '#8b949e' }}},
        scales: {
          x: { ticks: { color: '#8b949e' }, grid: { color: '#21262d' }},
          y: { ticks: { color: '#8b949e' }, grid: { color: '#21262d' }}
        }
      }
    });
  }
</script>
</body>
</html>
```

### Report Structure Guidelines

**Required sections for all report types:**
- **TL;DR** — 3–5 bullet points summarizing the most important findings
- **Background** — why this topic matters, what problem it solves
- **Core content** — architecture/method/implementation (varies by type; see below)
- **Takeaways** — your personal analysis: what's clever, what's limited, what matters for practitioners
- **References** — links to source code, paper, blog posts used

**Type-specific additions:**

*Repo Analysis:* Include an architecture diagram (Mermaid), a "key file map" table showing important files and their purpose, and a data-flow walkthrough.

*Paper Reading:* Include an info-grid showing venue/year/citations, a method diagram, and a results table. Add a "Limitations & Future Work" section.

*Feature Deep Dive:* Include a "Before vs After" callout showing the problem it solves, a diagram of the mechanism, and code references linking to real implementations.

---

## Step 4 — Charts and Diagrams

**Use Mermaid for:** architecture diagrams, data flow, class relationships, sequence diagrams, pipeline stages.

**Use Chart.js for:** performance numbers (throughput, latency, memory), comparisons between approaches, benchmark results.

Guidelines:
- Every diagram must have a descriptive `<h4>` caption
- For Mermaid: always initialize with `theme: 'dark'` as shown in the template
- For Chart.js: use the dark color palette from the template (`#58a6ff`, `#3fb950`, `#d29922`)
- If there are no real performance numbers in the source material, skip Chart.js charts — don't make up numbers. Use a callout box to note that benchmarks weren't available.
- Prefer fewer, high-quality diagrams over many rushed ones

---

## Step 5 — Update the Homepage

After saving the report HTML, update the homepage index.

**Prerequisite:** every report you generate MUST include the five `<meta>` tags shown in the template above (`report-title`, `report-type`, `report-date`, `report-tags`, `report-desc`). The update script reads these — fill them in accurately before saving.

**If `index.html` does not exist**, create it from the homepage template below, then run the script.

**If it already exists**, just run the script — it will automatically pick up the new report:

```bash
python /root/paddlejob/share-storage/gpfs/system-public/chenjian26/CJ-Note/scripts/update_index.py
```

The script scans all `reports/*.html`, extracts their meta tags, sorts by date (newest first), and rewrites the `REPORTS` array in `index.html`. You do **not** need to manually edit `index.html` unless you are creating it for the first time.

Useful flags:
```bash
python scripts/update_index.py --dry-run   # preview changes without writing
python scripts/update_index.py --verbose   # show each report found
```

### Homepage Template

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CJ-Note — LLM Inference Research Notes</title>
  <style>
    :root { --bg: #0d1117; --surface: #161b22; --border: #30363d;
            --text: #e6edf3; --muted: #8b949e; --accent: #58a6ff;
            --green: #3fb950; --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: var(--bg); color: var(--text); font-family: var(--font-sans);
           line-height: 1.6; min-height: 100vh; }

    /* Site header */
    .site-header { background: var(--surface); border-bottom: 1px solid var(--border);
                   padding: 1.5rem 2rem; display: flex; align-items: center;
                   justify-content: space-between; }
    .site-title { font-size: 1.4rem; font-weight: 700; color: var(--accent);
                  letter-spacing: -.02em; }
    .site-title span { color: var(--muted); font-weight: 400; }
    .site-header nav a { color: var(--muted); text-decoration: none; font-size: .9rem;
                         margin-left: 1.5rem; }
    .site-header nav a:hover { color: var(--accent); }

    .page-wrap { max-width: 900px; margin: 0 auto; padding: 2.5rem 1.5rem 4rem; }

    /* Hero */
    .hero { margin-bottom: 2.5rem; }
    .hero h2 { font-size: 1.5rem; color: var(--text); margin-bottom: .6rem; }
    .hero p { color: var(--muted); max-width: 600px; }

    /* Stats bar */
    .stats { display: flex; gap: 2rem; margin: 1.5rem 0 2rem;
             padding: 1rem 1.2rem; background: var(--surface);
             border: 1px solid var(--border); border-radius: 8px; flex-wrap: wrap; }
    .stat .num { font-size: 1.6rem; font-weight: 700; color: var(--accent); }
    .stat .lbl { font-size: .75rem; color: var(--muted); text-transform: uppercase;
                 letter-spacing: .05em; }

    /* Filter tags */
    .filters { display: flex; gap: .5rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
    .tag { background: var(--surface); border: 1px solid var(--border); border-radius: 20px;
           padding: .3rem .8rem; font-size: .8rem; color: var(--muted); cursor: pointer;
           transition: all .15s; }
    .tag:hover, .tag.active { background: var(--accent); color: #0d1117;
                               border-color: var(--accent); font-weight: 600; }

    /* Report cards */
    .report-list { display: flex; flex-direction: column; gap: .75rem; }
    .report-card { background: var(--surface); border: 1px solid var(--border);
                   border-radius: 8px; padding: 1rem 1.2rem;
                   display: flex; align-items: flex-start; gap: 1rem;
                   text-decoration: none; transition: border-color .15s; }
    .report-card:hover { border-color: var(--accent); }
    .report-icon { font-size: 1.3rem; flex-shrink: 0; margin-top: .1rem; }
    .report-info { flex: 1; }
    .report-title { color: var(--text); font-weight: 600; margin-bottom: .25rem; }
    .report-card:hover .report-title { color: var(--accent); }
    .report-meta { font-size: .8rem; color: var(--muted); display: flex; gap: 1rem; }
    .report-tags { display: flex; gap: .4rem; flex-wrap: wrap; margin-top: .4rem; }
    .rtag { background: rgba(88,166,255,.1); color: var(--accent); border-radius: 4px;
            padding: .1rem .5rem; font-size: .75rem; }

    /* Footer */
    .site-footer { text-align: center; padding: 2rem; color: var(--muted); font-size: .8rem;
                   border-top: 1px solid var(--border); }
  </style>
</head>
<body>

<header class="site-header">
  <div class="site-title">CJ-Note <span>/ LLM Inference</span></div>
  <nav>
    <a href="https://github.com/rainyfly/CJ-Note" target="_blank">GitHub</a>
  </nav>
</header>

<div class="page-wrap">
  <div class="hero">
    <h2>LLM Inference Research Notes</h2>
    <p>Personal notes on LLM inference systems — architecture analysis, paper reading, and feature deep dives.
       Topics: scheduling, memory management, attention kernels, quantization, speculative decoding, and more.</p>
  </div>

  <div class="stats">
    <div class="stat"><div class="num" id="total-count">0</div><div class="lbl">Reports</div></div>
    <div class="stat"><div class="num" id="last-updated">—</div><div class="lbl">Last Updated</div></div>
  </div>

  <div class="filters" id="filter-bar">
    <span class="tag active" data-filter="all">All</span>
    <span class="tag" data-filter="repo">Repo Analysis</span>
    <span class="tag" data-filter="paper">Paper Reading</span>
    <span class="tag" data-filter="feature">Feature Deep Dive</span>
  </div>

  <div class="report-list" id="report-list">
    <!-- reports injected by JS below -->
  </div>
</div>

<footer class="site-footer">
  CJ-Note · Built with Claude · <a href="https://github.com/rainyfly/CJ-Note" style="color:#58a6ff">GitHub</a>
</footer>

<script>
// ── Report Registry ──────────────────────────────────────────
// Add new entries here (prepend so newest is first)
const REPORTS = [
  // {
  //   title: "vLLM Architecture Deep Dive",
  //   file: "reports/vllm-architecture.html",
  //   type: "repo",           // repo | paper | feature
  //   date: "2026-01-10",
  //   tags: ["Scheduling", "Memory", "KV Cache"],
  //   desc: "How vLLM implements continuous batching and PagedAttention..."
  // },
];

// ── Render ────────────────────────────────────────────────────
const ICONS = { repo: "🏗️", paper: "📄", feature: "⚡" };
const TYPE_LABELS = { repo: "Repo Analysis", paper: "Paper Reading", feature: "Feature Deep Dive" };

function render(filter = "all") {
  const list = document.getElementById("report-list");
  const shown = filter === "all" ? REPORTS : REPORTS.filter(r => r.type === filter);

  if (shown.length === 0) {
    list.innerHTML = '<p style="color:var(--muted);padding:2rem 0;text-align:center">No reports yet — check back soon.</p>';
    return;
  }

  list.innerHTML = shown.map(r => `
    <a class="report-card" href="${r.file}">
      <div class="report-icon">${ICONS[r.type] || "📝"}</div>
      <div class="report-info">
        <div class="report-title">${r.title}</div>
        <div class="report-meta">
          <span>${TYPE_LABELS[r.type]}</span>
          <span>${r.date}</span>
        </div>
        ${r.desc ? `<p style="font-size:.85rem;color:var(--muted);margin-top:.3rem">${r.desc}</p>` : ""}
        <div class="report-tags">${(r.tags||[]).map(t=>`<span class="rtag">${t}</span>`).join("")}</div>
      </div>
    </a>`).join("");
}

// Stats
document.getElementById("total-count").textContent = REPORTS.length;
if (REPORTS.length > 0) {
  document.getElementById("last-updated").textContent =
    REPORTS.slice().sort((a,b)=>b.date.localeCompare(a.date))[0].date;
}

// Filter logic
document.querySelectorAll(".tag").forEach(t => {
  t.addEventListener("click", () => {
    document.querySelectorAll(".tag").forEach(x=>x.classList.remove("active"));
    t.classList.add("active");
    render(t.dataset.filter);
  });
});

render();
</script>
</body>
</html>
```

### How to update the report list in index.html

Find the `const REPORTS = [` line and prepend a new entry object. Keep the array sorted newest-first. The entry format:

```javascript
{
  title: "Report Title",
  file: "reports/slug.html",   // relative path from repo root
  type: "repo",                // "repo" | "paper" | "feature"
  date: "YYYY-MM-DD",
  tags: ["Topic1", "Topic2"],  // 2–4 tags, e.g. "KV Cache", "Scheduling", "Quantization"
  desc: "One-sentence description shown in the card."
}
```

---

## Step 6 — Final Checklist

Before finishing, verify:

- [ ] Report saved at `reports/<slug>.html`
- [ ] All five `<meta>` tags present and accurate (`report-title`, `report-type`, `report-date`, `report-tags`, `report-desc`)
- [ ] HTML is self-contained (no local asset dependencies — CDN links only)
- [ ] Mermaid initialized with `theme: 'dark'`
- [ ] All chart data comes from the source material (no fabricated numbers)
- [ ] Ran `python scripts/update_index.py` to update `index.html`
- [ ] TL;DR accurately reflects the report content
- [ ] "Back to CJ-Note" link is correct (`../index.html`)
- [ ] Date in `report-date` meta and report header is today's date

---

## Tone and Writing Style

- Write as a practitioner explaining to another practitioner — not a textbook, not marketing copy
- Be specific: cite file paths, function names, paper section numbers, actual numbers
- Be honest about limitations — if a design has drawbacks, say so
- For paper reports: distinguish what the authors *claim* vs. what they *demonstrate*
- Keep sentences short. Use headings liberally. Avoid passive voice.
- Chinese or English — follow whatever language the user used in their request
