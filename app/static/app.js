const authPanel = document.getElementById("auth-panel");
const dashboardPanel = document.getElementById("dashboard-panel");
const signupForm = document.getElementById("signup-form");
const loginForm = document.getElementById("login-form");
const authTitle = document.getElementById("auth-title");
const showSignupLink = document.getElementById("show-signup-link");
const showLoginLink = document.getElementById("show-login-link");

const state = {
  token: localStorage.getItem("token") || "",
  user: JSON.parse(localStorage.getItem("user") || "null"),
  cargoRows: [],
  pageSize: 5,
  currentPage: 1,
};

function setSession(user, token) {
  state.user = user;
  state.token = token;
  localStorage.setItem("user", JSON.stringify(user));
  localStorage.setItem("token", token);
}

function clearSession() {
  state.user = null;
  state.token = "";
  state.cargoRows = [];
  state.currentPage = 1;
  localStorage.removeItem("user");
  localStorage.removeItem("token");
}

function clearAuthForms() {
  signupForm.reset();
  loginForm.reset();
  for (const field of signupForm.elements) {
    if (field instanceof HTMLInputElement) {
      field.value = "";
    }
  }
  for (const field of loginForm.elements) {
    if (field instanceof HTMLInputElement) {
      field.value = "";
    }
  }
}

function clearMessage(parent) {
  const box = parent.querySelector(".message");
  if (box) {
    box.remove();
  }
}

function showMessage(parent, text) {
  let box = parent.querySelector(".message");
  if (!box) {
    box = document.createElement("div");
    box.className = "message";
    parent.appendChild(box);
  }
  box.textContent = text;
}

async function authRequest(path, payload) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json().then((body) => ({ ok: res.ok, status: res.status, body }));
}

function setButtonLoading(button, isLoading, loadingText, defaultText) {
  button.disabled = isLoading;
  if (isLoading) {
    button.dataset.defaultText = defaultText;
    button.classList.add("btn-loading");
    button.innerHTML = `<span class="spinner"></span>${loadingText}`;
    return;
  }
  button.classList.remove("btn-loading");
  button.textContent = button.dataset.defaultText || defaultText;
}

function sortCargoRows(rows) {
  return [...rows].sort((a, b) => {
    const aEarth = String(a.destination || "").trim().toLowerCase() === "earth";
    const bEarth = String(b.destination || "").trim().toLowerCase() === "earth";
    if (aEarth !== bEarth) {
      return aEarth ? 1 : -1;
    }
    return Number(b.weight_kg) - Number(a.weight_kg);
  });
}

function buildDashboardShell() {
  dashboardPanel.innerHTML = "";

  const toolbar = document.createElement("div");
  toolbar.className = "toolbar";
  toolbar.innerHTML = `
    <div>
      <strong>${state.user.name}</strong> (${state.user.role})
    </div>
    <div>
      <button id="refresh-btn">Refresh Cargo</button>
      <button id="logout-btn">Logout</button>
    </div>
  `;
  dashboardPanel.appendChild(toolbar);

  if (state.user.role === "Admin") {
    const uploadBlock = document.createElement("form");
    uploadBlock.id = "upload-form";
    uploadBlock.className = "stack";
    uploadBlock.innerHTML = `
      <h3>File Upload</h3>
      <input type="file" name="file" accept=".txt" required>
      <button type="submit">Upload manifest.txt</button>
    `;
    dashboardPanel.appendChild(uploadBlock);
  }

  const tableWrap = document.createElement("div");
  tableWrap.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Shipment</th>
          <th>Origin</th>
          <th>Destination</th>
          <th>Weight</th>
          <th>Uploaded At</th>
        </tr>
      </thead>
      <tbody id="cargo-tbody"></tbody>
    </table>
    <div class="pagination" id="pagination"></div>
  `;
  dashboardPanel.appendChild(tableWrap);
}

function renderCargoRows() {
  const tbody = document.getElementById("cargo-tbody");
  const pagination = document.getElementById("pagination");
  const isAdmin = state.user.role === "Admin";
  const totalPages = Math.max(1, Math.ceil(state.cargoRows.length / state.pageSize));

  if (state.currentPage > totalPages) {
    state.currentPage = totalPages;
  }

  const start = (state.currentPage - 1) * state.pageSize;
  const pageRows = state.cargoRows.slice(start, start + state.pageSize);

  tbody.innerHTML = pageRows
    .map((row) => {
      const kg = Number(row.weight_kg);
      const shownWeight = isAdmin
        ? `${kg} KG`
        : `${(kg * 2.20462).toFixed(2)} LBS`;
      return `
        <tr>
          <td>${row.shipment_id || "-"}</td>
          <td>${row.origin || "-"}</td>
          <td>${row.destination}</td>
          <td>${shownWeight}</td>
          <td>${row.uploaded_at}</td>
        </tr>
      `;
    })
    .join("");

  const hasRows = state.cargoRows.length > 0;
  pagination.innerHTML = hasRows
    ? `
      <button id="prev-page-btn" ${state.currentPage === 1 ? "disabled" : ""}>Prev</button>
      <span>Page ${state.currentPage} of ${totalPages}</span>
      <button id="next-page-btn" ${state.currentPage === totalPages ? "disabled" : ""}>Next</button>
    `
    : "<span>No cargo records found.</span>";

  const prevBtn = document.getElementById("prev-page-btn");
  const nextBtn = document.getElementById("next-page-btn");
  if (prevBtn) {
    prevBtn.addEventListener("click", () => {
      state.currentPage -= 1;
      renderCargoRows();
    });
  }
  if (nextBtn) {
    nextBtn.addEventListener("click", () => {
      state.currentPage += 1;
      renderCargoRows();
    });
  }
}

async function loadCargo() {
  const res = await fetch("/api/cargo", {
    headers: { Authorization: `Bearer ${state.token}` },
  });
  const body = await res.json();
  if (!res.ok) {
    showMessage(dashboardPanel, body.message || "Failed to load cargo.");
    return;
  }
  clearMessage(dashboardPanel);
  state.cargoRows = sortCargoRows(body.cargo || []);
  state.currentPage = 1;
  renderCargoRows();
}

async function uploadManifest(form) {
  const file = form.file.files[0];
  const data = new FormData();
  data.append("file", file);

  const res = await fetch("/api/upload", {
    method: "POST",
    headers: { Authorization: `Bearer ${state.token}` },
    body: data,
  });
  const body = await res.json();
  showMessage(
    dashboardPanel,
    body.message ||
      `Inserted: ${body.inserted || 0}, skipped prime: ${body.skipped_prime || 0}`
  );
  if (res.ok) {
    await loadCargo();
    form.reset();
  }
}

function bindDashboardEvents() {
  document.getElementById("logout-btn").addEventListener("click", () => {
    clearSession();
    clearAuthForms();
    clearMessage(authPanel);
    showLoginView();
    authPanel.classList.remove("hidden");
    dashboardPanel.classList.add("hidden");
    dashboardPanel.innerHTML = "";
  });

  document.getElementById("refresh-btn").addEventListener("click", loadCargo);

  const uploadForm = document.getElementById("upload-form");
  if (uploadForm) {
    uploadForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      await uploadManifest(uploadForm);
    });
  }
}

async function renderDashboard() {
  authPanel.classList.add("hidden");
  dashboardPanel.classList.remove("hidden");
  buildDashboardShell();
  bindDashboardEvents();
  await loadCargo();
}

function showLoginView() {
  authTitle.textContent = "Login";
  signupForm.classList.add("hidden");
  loginForm.classList.remove("hidden");
}

function showSignupView() {
  authTitle.textContent = "Signup";
  loginForm.classList.add("hidden");
  signupForm.classList.remove("hidden");
}

showSignupLink.addEventListener("click", (event) => {
  event.preventDefault();
  clearMessage(authPanel);
  showSignupView();
});

showLoginLink.addEventListener("click", (event) => {
  event.preventDefault();
  clearMessage(authPanel);
  showLoginView();
});

signupForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const submitBtn = document.getElementById("signup-btn");
  clearMessage(authPanel);
  setButtonLoading(submitBtn, true, "Creating...", "Create account");
  try {
    const result = await authRequest("/signup", {
      name: form.name.value,
      email: form.email.value,
      password: form.password.value,
    });
    if (!result.ok) {
      showMessage(authPanel, result.body.message || "Signup failed.");
      return;
    }
    setSession(result.body.user, result.body.token);
    clearAuthForms();
    await renderDashboard();
  } finally {
    setButtonLoading(submitBtn, false, "Creating...", "Create account");
  }
});

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const submitBtn = document.getElementById("login-btn");
  clearMessage(authPanel);
  setButtonLoading(submitBtn, true, "Signing in...", "Sign in");
  try {
    const result = await authRequest("/login", {
      email: form.email.value,
      password: form.password.value,
    });
    if (!result.ok) {
      showMessage(authPanel, result.body.message || "Login failed.");
      return;
    }
    setSession(result.body.user, result.body.token);
    clearAuthForms();
    await renderDashboard();
  } finally {
    setButtonLoading(submitBtn, false, "Signing in...", "Sign in");
  }
});

if (state.token && state.user) {
  renderDashboard().catch(() => {
    clearSession();
    clearAuthForms();
    showLoginView();
  });
} else {
  clearAuthForms();
  showLoginView();
}
