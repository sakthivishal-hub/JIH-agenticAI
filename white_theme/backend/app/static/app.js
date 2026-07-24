// ===================================================================
// OpportunityOS frontend — talks to the FastAPI backend mounted at
// the same origin this file is served from (see app/main.py).
// ===================================================================
const API_BASE = ""; // same-origin: /auth/login, /opportunities/search, etc.

const state = {
  token: localStorage.getItem("oos_token") || null,
  user: null,
};

// ---------------- low-level fetch helper ----------------
async function api(path, { method = "GET", body, auth = false, isForm = false } = {}) {
  const headers = {};
  if (!isForm) headers["Content-Type"] = "application/json";
  if (auth && state.token) headers["Authorization"] = `Bearer ${state.token}`;

  const res = await fetch(API_BASE + path, {
    method,
    headers,
    body: body ? (isForm ? body : JSON.stringify(body)) : undefined,
  });

  let payload = null;
  try { payload = await res.json(); } catch (_) { /* no body */ }

  if (!res.ok) {
    const msg = (payload && (payload.detail || payload.message)) || `Request failed (${res.status})`;
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }
  return payload;
}

// ---------------- toast ----------------
let toastTimer;
function toast(msg, isError = false) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.classList.toggle("error", isError);
  el.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove("show"), 3200);
}

// ---------------- auth ----------------
function isLoggedIn() { return !!state.token; }

function setToken(token) {
  state.token = token;
  if (token) localStorage.setItem("oos_token", token);
  else localStorage.removeItem("oos_token");
}

async function fetchMe() {
  if (!state.token) return null;
  try {
    const me = await api("/users/me", { auth: true });
    state.user = me;
    return me;
  } catch (e) {
    setToken(null);
    return null;
  }
}

function renderAuthState() {
  const navAuth = document.getElementById("navAuth");
  const navUser = document.getElementById("navUser");
  const navLinks = document.getElementById("navLinks");
  const landing = document.getElementById("landing");
  const app = document.getElementById("app");

  if (isLoggedIn() && state.user) {
    navAuth.classList.add("hidden");
    navUser.classList.remove("hidden");
    navLinks.style.display = "flex";
    document.getElementById("userChip").textContent = (state.user.name || "U").charAt(0).toUpperCase();
    landing.classList.add("hidden");
    app.classList.remove("hidden");
  } else {
    navAuth.classList.remove("hidden");
    navUser.classList.add("hidden");
    navLinks.style.display = "none";
    landing.classList.remove("hidden");
    app.classList.add("hidden");
  }
}

// ---------------- tabs ----------------
function switchTab(tab) {
  document.querySelectorAll(".panel").forEach(p => p.classList.toggle("active", p.dataset.panel === tab));
  document.querySelectorAll(".nav-link").forEach(b => b.classList.toggle("active", b.dataset.tab === tab));
  if (tab === "bookmarks") loadBookmarks();
  if (tab === "profile") loadProfile();
}

document.querySelectorAll(".nav-link").forEach(btn => {
  btn.addEventListener("click", () => switchTab(btn.dataset.tab));
});

// ---------------- auth modal ----------------
const authBackdrop = document.getElementById("authBackdrop");
function openAuth(tab) {
  authBackdrop.classList.remove("hidden");
  setAuthTab(tab);
}
function closeAuth() { authBackdrop.classList.add("hidden"); }
function setAuthTab(tab) {
  document.querySelectorAll(".modal-tab").forEach(t => t.classList.toggle("active", t.dataset.authtab === tab));
  document.querySelectorAll(".modal-form").forEach(f => f.classList.remove("active"));
  document.getElementById(tab === "login" ? "loginForm" : "signupForm").classList.add("active");
}
document.getElementById("btnLogin").addEventListener("click", () => openAuth("login"));
document.getElementById("btnSignup").addEventListener("click", () => openAuth("signup"));
document.getElementById("heroSignup").addEventListener("click", () => openAuth("signup"));
document.getElementById("heroDemo").addEventListener("click", () => document.getElementById("how").scrollIntoView({ behavior: "smooth" }));
document.getElementById("authClose").addEventListener("click", closeAuth);
authBackdrop.addEventListener("click", (e) => { if (e.target === authBackdrop) closeAuth(); });
document.querySelectorAll(".modal-tab").forEach(t => t.addEventListener("click", () => setAuthTab(t.dataset.authtab)));

document.getElementById("loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const errEl = document.getElementById("loginError");
  errEl.textContent = "";
  try {
    const res = await api("/auth/login", {
      method: "POST",
      body: {
        email: document.getElementById("loginEmail").value.trim(),
        password: document.getElementById("loginPassword").value,
      },
    });
    setToken(res.access_token);
    await fetchMe();
    renderAuthState();
    closeAuth();
    toast(`Welcome back, ${state.user?.name || "there"}.`);
  } catch (err) {
    errEl.textContent = err.message;
  }
});

document.getElementById("signupForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const errEl = document.getElementById("signupError");
  errEl.textContent = "";
  try {
    await api("/auth/register", {
      method: "POST",
      body: {
        name: document.getElementById("signupName").value.trim(),
        email: document.getElementById("signupEmail").value.trim(),
        password: document.getElementById("signupPassword").value,
      },
    });
    // auto-login right after register
    const loginRes = await api("/auth/login", {
      method: "POST",
      body: {
        email: document.getElementById("signupEmail").value.trim(),
        password: document.getElementById("signupPassword").value,
      },
    });
    setToken(loginRes.access_token);
    await fetchMe();
    renderAuthState();
    closeAuth();
    toast("Account created. Upload your resume to unlock matches.");
    switchTab("profile");
  } catch (err) {
    errEl.textContent = err.message;
  }
});

document.getElementById("btnLogout").addEventListener("click", () => {
  setToken(null);
  state.user = null;
  renderAuthState();
  toast("Logged out.");
});

document.querySelector(".brand").addEventListener("click", () => {
  if (isLoggedIn()) switchTab("search"); else window.scrollTo({ top: 0, behavior: "smooth" });
});

// ---------------- opportunity card rendering ----------------
function scoreTag(score) {
  if (score === undefined || score === null) return "";
  return `<span class="opp-score">${score}% match</span>`;
}

function oppCard(opp, { showScore = false } = {}) {
  const skills = Array.isArray(opp.skills) ? opp.skills : (opp.skills ? String(opp.skills).split(",") : []);
  const tags = [opp.type, opp.location, opp.salary, opp.deadline ? `Deadline: ${opp.deadline}` : null]
    .filter(Boolean)
    .map(t => `<span class="tag">${escapeHtml(String(t))}</span>`)
    .join("");
  const skillTags = skills.slice(0, 6).map(s => `<span class="tag">${escapeHtml(String(s).trim())}</span>`).join("");

  const payload = encodeURIComponent(JSON.stringify({
    title: opp.title, company: opp.company || "", location: opp.location || "",
    salary: opp.salary || "", deadline: opp.deadline || null, apply_link: opp.apply_link,
    description: opp.description || "", skills: opp.skills || [], source: opp.source || "unknown",
    type: opp.type || "unknown",
  }));

  return `
  <article class="opp-card">
    <div class="opp-top">
      <div>
        <div class="opp-title">${escapeHtml(opp.title || "Untitled opportunity")}</div>
        <div class="opp-company">${escapeHtml(opp.company || "")}</div>
      </div>
      ${showScore ? scoreTag(opp.overall_score) : ""}
    </div>
    <div class="opp-meta">${tags}${skillTags}</div>
    ${opp.description ? `<p class="opp-desc">${escapeHtml(truncate(stripTags(opp.description), 220))}</p>` : ""}
    <div class="opp-actions">
      <a class="btn btn-solid btn-sm" href="${escapeAttr(opp.apply_link || "#")}" target="_blank" rel="noopener">Apply ↗</a>
      <button class="btn btn-outline btn-sm" data-save="${payload}">Save</button>
    </div>
  </article>`;
}

function tavilyCard(item, type) {
  const payload = encodeURIComponent(JSON.stringify({
    title: item.title, company: "", location: "", salary: "", deadline: null,
    apply_link: item.url, description: item.content || "", skills: [],
    source: "tavily", type,
  }));
  return `
  <article class="opp-card">
    <div class="opp-top">
      <div>
        <div class="opp-title">${escapeHtml(item.title || "Untitled")}</div>
      </div>
      <span class="tag">${type}</span>
    </div>
    ${item.content ? `<p class="opp-desc">${escapeHtml(truncate(stripTags(item.content), 220))}</p>` : ""}
    <div class="opp-actions">
      <a class="btn btn-solid btn-sm" href="${escapeAttr(item.url || "#")}" target="_blank" rel="noopener">Open ↗</a>
      <button class="btn btn-outline btn-sm" data-save="${payload}">Save</button>
    </div>
  </article>`;
}

function escapeHtml(s) { return s.replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }
function escapeAttr(s) { return escapeHtml(s); }
function stripTags(s) { return String(s).replace(/<[^>]*>/g, " "); }
function truncate(s, n) { return s.length > n ? s.slice(0, n).trim() + "…" : s; }

function spinnerRow(label) {
  return `<div class="spinner-row"><span class="spinner"></span> ${label}</div>`;
}
function emptyState(label) {
  return `<div class="empty-state">${label}</div>`;
}

// delegated Save-button handling
document.addEventListener("click", async (e) => {
  const btn = e.target.closest("[data-save]");
  if (!btn) return;
  if (!isLoggedIn()) { openAuth("login"); toast("Log in to save opportunities."); return; }
  const opp = JSON.parse(decodeURIComponent(btn.dataset.save));
  btn.disabled = true;
  const original = btn.textContent;
  btn.textContent = "Saving…";
  try {
    const res = await api("/bookmarks/save", { method: "POST", auth: true, body: opp });
    if (res.success === false) throw new Error(res.message || "Could not save.");
    btn.textContent = "Saved ✓";
    toast("Saved to your board.");
  } catch (err) {
    btn.disabled = false;
    btn.textContent = original;
    toast(err.message, true);
  }
});

// ---------------- search (opportunities) ----------------
document.getElementById("searchForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const out = document.getElementById("searchResults");
  const query = document.getElementById("searchQuery").value.trim();
  const location = document.getElementById("searchLocation").value.trim();
  out.innerHTML = spinnerRow("Scanning live sources…");
  try {
    const params = new URLSearchParams({ query, limit: "20" });
    if (location) params.set("location", location);
    const res = await api(`/opportunities/search?${params}`);
    const results = res?.data?.results || [];
    out.innerHTML = results.length
      ? results.map(o => oppCard(o)).join("")
      : emptyState("Nothing matched that search yet — try a broader query.");
  } catch (err) {
    out.innerHTML = emptyState(err.message);
  }
});

// ---------------- hackathons ----------------
document.getElementById("hackForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const out = document.getElementById("hackResults");
  const q = document.getElementById("hackQuery").value.trim();
  out.innerHTML = spinnerRow("Checking open hackathons…");
  try {
    const params = q ? `?q=${encodeURIComponent(q)}` : "";
    const res = await api(`/hackathons/search${params}`);
    const results = res?.results || [];
    if (res.error) throw new Error(res.error);
    out.innerHTML = results.length
      ? results.map(r => tavilyCard(r, "Hackathon")).join("")
      : emptyState("No open hackathons found right now — try a different query.");
  } catch (err) {
    out.innerHTML = emptyState(err.message);
  }
});
// load a first batch automatically
loadHackathonsDefault();
async function loadHackathonsDefault() {
  const out = document.getElementById("hackResults");
  out.innerHTML = spinnerRow("Loading open hackathons…");
  try {
    const res = await api("/hackathons/search");
    const results = res?.results || [];
    out.innerHTML = results.length
      ? results.map(r => tavilyCard(r, "Hackathon")).join("")
      : emptyState("No open hackathons found right now.");
  } catch (err) {
    out.innerHTML = emptyState("Couldn't load hackathons right now.");
  }
}

// ---------------- research ----------------
document.getElementById("researchForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const out = document.getElementById("researchResults");
  const topic = document.getElementById("researchTopic").value;
  const q = document.getElementById("researchQuery").value.trim();
  out.innerHTML = spinnerRow("Searching research positions…");
  try {
    const params = new URLSearchParams({ topic });
    if (q) params.set("q", q);
    const res = await api(`/research/search?${params}`);
    if (res.error) throw new Error(res.error);
    const results = res?.results || [];
    out.innerHTML = results.length
      ? results.map(r => tavilyCard(r, "Research")).join("")
      : emptyState("No research openings found for that topic yet.");
  } catch (err) {
    out.innerHTML = emptyState(err.message);
  }
});

// ---------------- recommendations ----------------
document.getElementById("recommendForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const out = document.getElementById("recommendResults");
  const query = document.getElementById("recommendQuery").value.trim();
  const location = document.getElementById("recommendLocation").value.trim();
  out.innerHTML = spinnerRow("Scoring live opportunities against your resume…");
  try {
    const params = new URLSearchParams({ query, top_k: "10" });
    if (location) params.set("location", location);
    const res = await api(`/recommendations/?${params}`, { method: "POST", auth: true });
    if (res.success === false) throw new Error(res.message);
    const recs = res?.data?.recommendations || [];
    out.innerHTML = recs.length
      ? recs.map(o => oppCard(o, { showScore: true })).join("")
      : emptyState("No strong matches yet — try a different search.");
  } catch (err) {
    out.innerHTML = emptyState(err.message);
  }
});

function refreshRecommendNotice() {
  const el = document.getElementById("recommendNotice");
  el.textContent = state.user && !state.user.has_resume
    ? "Upload a resume in your Profile tab first — recommendations are scored against it."
    : "";
}

// ---------------- bookmarks ----------------
async function loadBookmarks() {
  const out = document.getElementById("bookmarkResults");
  out.innerHTML = spinnerRow("Loading your saved board…");
  try {
    const res = await api("/bookmarks/detailed", { auth: true });
    const items = res?.data?.bookmarks || [];
    if (!items.length) { out.innerHTML = emptyState("Nothing saved yet — hit \u201cSave\u201d on anything you like."); return; }
    out.innerHTML = items.map(b => `
      <article class="opp-card">
        <div class="opp-top">
          <div>
            <div class="opp-title">${escapeHtml(b.title || "")}</div>
            <div class="opp-company">${escapeHtml(b.company || "")}</div>
          </div>
        </div>
        <div class="opp-meta">${[b.type, b.location, b.deadline ? `Deadline: ${b.deadline}` : null].filter(Boolean).map(t => `<span class="tag">${escapeHtml(String(t))}</span>`).join("")}</div>
        <div class="opp-actions">
          <a class="btn btn-solid btn-sm" href="${escapeAttr(b.apply_link || "#")}" target="_blank" rel="noopener">Apply ↗</a>
          <button class="btn btn-outline btn-sm" data-unsave="${b.opportunity_id}">Remove</button>
        </div>
      </article>`).join("");
  } catch (err) {
    out.innerHTML = emptyState(err.message);
  }
}

document.addEventListener("click", async (e) => {
  const btn = e.target.closest("[data-unsave]");
  if (!btn) return;
  try {
    await api(`/bookmarks/${btn.dataset.unsave}`, { method: "DELETE", auth: true });
    toast("Removed.");
    loadBookmarks();
  } catch (err) {
    toast(err.message, true);
  }
});

// ---------------- profile ----------------
async function loadProfile() {
  await fetchMe();
  if (!state.user) return;
  document.getElementById("pfName").value = state.user.name || "";
  document.getElementById("pfRole").value = state.user.preferred_role || "";
  document.getElementById("pfLocation").value = state.user.preferred_location || "";
  document.getElementById("pfSkills").value = state.user.skills || "";
  document.getElementById("resumeStatus").textContent = state.user.has_resume
    ? "Resume on file — recommendations are live."
    : "No resume on file yet — recommendations need one.";
  refreshRecommendNotice();

  try {
    const prefs = await api("/notifications/preferences", { auth: true });
    document.getElementById("notifyEmail").checked = !!prefs.notify_email;
    document.getElementById("notifyWhatsapp").checked = !!prefs.notify_whatsapp;
    document.getElementById("whatsappNumber").value = prefs.whatsapp_number || "";
  } catch (_) { /* ignore */ }
}

document.getElementById("dropzone").addEventListener("click", () => document.getElementById("resumeFile").click());
document.getElementById("resumeFile").addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const label = document.getElementById("dropzoneLabel");
  label.textContent = `Uploading ${file.name}…`;
  const form = new FormData();
  form.append("file", file);
  try {
    const res = await api("/resume/upload", { method: "POST", auth: true, isForm: true, body: form });
    if (res.success === false) throw new Error(res.message);
    label.textContent = `Uploaded: ${file.name}`;
    document.getElementById("resumeStatus").textContent = "Resume on file — recommendations are live.";
    const skills = res?.data?.skills || [];
    document.getElementById("resumeSkills").innerHTML = skills.map(s => `<span class="chip">${escapeHtml(String(s))}</span>`).join("");
    toast("Resume parsed. You're ready for matches.");
    refreshRecommendNotice();
  } catch (err) {
    label.textContent = "Click to upload PDF or DOCX";
    toast(err.message, true);
  }
});

document.getElementById("profileForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await api("/users/me", {
      method: "PUT", auth: true,
      body: {
        name: document.getElementById("pfName").value.trim() || undefined,
        preferred_role: document.getElementById("pfRole").value.trim() || undefined,
        preferred_location: document.getElementById("pfLocation").value.trim() || undefined,
        skills: document.getElementById("pfSkills").value.trim() || undefined,
      },
    });
    toast("Profile saved.");
  } catch (err) {
    toast(err.message, true);
  }
});

document.getElementById("notifyForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await api("/notifications/preferences", {
      method: "PUT", auth: true,
      body: {
        notify_email: document.getElementById("notifyEmail").checked,
        notify_whatsapp: document.getElementById("notifyWhatsapp").checked,
        whatsapp_number: document.getElementById("whatsappNumber").value.trim() || null,
      },
    });
    toast("Alert settings saved.");
  } catch (err) {
    toast(err.message, true);
  }
});

document.getElementById("btnTestNotify").addEventListener("click", async () => {
  const hint = document.getElementById("notifyHint");
  hint.textContent = "Sending…";
  try {
    const res = await api("/notifications/test", { method: "POST", auth: true });
    if (res.success === false) { hint.textContent = res.message; return; }
    const results = res?.data || {};
    hint.textContent = `Email: ${results.email ? "sent" : "skipped"} · WhatsApp: ${results.whatsapp ? "sent" : "skipped"}`;
  } catch (err) {
    hint.textContent = err.message;
  }
});

// ---------------- boot ----------------
(async function boot() {
  if (state.token) {
    await fetchMe();
  }
  renderAuthState();
  switchTab("search");
})();
