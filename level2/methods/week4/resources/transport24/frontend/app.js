const API = "http://localhost:8000/api";
let token = localStorage.getItem("transport24_token");
let currentUser = null;

const app = document.getElementById("app");

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function api(path, options = {}) {
  const headers = {
    ...(options.body instanceof FormData ? {} : {"Content-Type": "application/json"}),
    ...(options.headers || {})
  };

  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(API + path, {...options, headers});

  if (response.status === 401) {
    logout();
    throw new Error("Session expired");
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || "Request failed");
  }

  return data;
}

function renderLogin(message = "") {
  app.innerHTML = `
    <div class="login">
      <form class="login-card" id="loginForm">
        <div class="brand">TRANSPORT24</div>
        <div class="tagline">24 / 7 · PEOPLE & OBJECTS</div>

        <label>Username</label>
        <input id="username" autocomplete="username" required>

        <label>Password</label>
        <input id="password" type="password" autocomplete="current-password" required>

        <div class="error">${escapeHtml(message)}</div>

        <button class="primary full">ENTER SYSTEM</button>
      </form>
    </div>
  `;

  document.getElementById("loginForm").addEventListener("submit", login);
}

async function login(event) {
  event.preventDefault();

  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const body = new URLSearchParams();
  body.set("username", username);
  body.set("password", password);

  try {
    const response = await fetch(API + "/login", {
      method: "POST",
      headers: {"Content-Type": "application/x-www-form-urlencoded"},
      body
    });

    const data = await response.json();

    if (!response.ok) {
      renderLogin(data.detail || "Login failed");
      return;
    }

    token = data.access_token;
    localStorage.setItem("transport24_token", token);
    currentUser = data.user;

    renderApp();
  } catch (error) {
    renderLogin("Cannot connect to the API.");
  }
}

function logout() {
  token = null;
  currentUser = null;
  localStorage.removeItem("transport24_token");
  renderLogin();
}

function renderApp() {
  app.innerHTML = `
    <div class="app-shell">
      <header class="topbar">
        <div class="brand">TRANSPORT24</div>
        <div class="userbox">
          <span id="userLabel"></span>
          <button class="secondary" onclick="logout()">LOGOUT</button>
        </div>
      </header>

      <div class="layout">
        <aside class="sidebar">
          <button class="nav-btn active" data-page="dashboard">Dashboard</button>
          <button class="nav-btn" data-page="customers">Customers</button>
          <button class="nav-btn" data-page="people">People service</button>
          <button class="nav-btn" data-page="objects">Object service</button>
          <button class="nav-btn" data-page="records">Records</button>
          <button class="nav-btn" data-page="employees">Employees</button>
        </aside>

        <main class="content" id="content"></main>
      </div>
    </div>
  `;

  document.getElementById("userLabel").textContent =
    `${currentUser.full_name} · ${currentUser.role}`;

  document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      loadPage(btn.dataset.page);
    });
  });

  loadPage("dashboard");
}

async function loadPage(page) {
  try {
    if (page === "dashboard") await dashboard();
    if (page === "customers") await customers();
    if (page === "people") await serviceForm("people");
    if (page === "objects") await serviceForm("objects");
    if (page === "records") await records();
    if (page === "employees") await employees();
  } catch (error) {
    document.getElementById("content").innerHTML =
      `<div class="error">${escapeHtml(error.message)}</div>`;
  }
}

async function dashboard() {
  const d = await api("/dashboard");

  document.getElementById("content").innerHTML = `
    <h1>Dashboard</h1>
    <p class="muted">Today · 24 / 7 operation</p>

    <div class="cards">
      <div class="card">
        <div class="muted">PEOPLE</div>
        <div class="number">${d.people}</div>
      </div>
      <div class="card">
        <div class="muted">OBJECTS</div>
        <div class="number">${d.objects}</div>
      </div>
      <div class="card">
        <div class="muted">TOTAL</div>
        <div class="number">${d.total}</div>
      </div>
      <div class="card">
        <div class="muted">PENDING PAYMENTS</div>
        <div class="number">${d.pending_payments}</div>
      </div>
    </div>

    <div class="actions">
      <button class="primary" onclick="loadPage('people')">NEW PEOPLE SERVICE</button>
      <button class="secondary" onclick="loadPage('objects')">NEW OBJECT SERVICE</button>
      <button class="secondary" onclick="loadPage('customers')">CUSTOMERS</button>
    </div>

    <div class="form-card">
      <h3>Operating principle</h3>
      <p class="muted">
        Employees register the service and payment information.
        The system does not provide GPS package tracking and has no chatbot.
      </p>
    </div>
  `;
}

async function customers() {
  const data = await api("/customers");

  document.getElementById("content").innerHTML = `
    <h1>Customers</h1>

    <form class="form-card" id="customerForm">
      <div class="grid2">
        <div>
          <label>Full name</label>
          <input id="cName" required>
        </div>
        <div>
          <label>Phone</label>
          <input id="cPhone">
        </div>
        <div>
          <label>Email</label>
          <input id="cEmail" type="email">
        </div>
        <div>
          <label>Notes</label>
          <input id="cNotes">
        </div>
      </div>
      <br>
      <button class="primary">SAVE CUSTOMER</button>
    </form>

    <div class="table-wrap">
      <table>
        <thead><tr><th>ID</th><th>Name</th><th>Phone</th><th>Email</th><th>Notes</th></tr></thead>
        <tbody>
          ${data.map(c => `
            <tr>
              <td>${c.id}</td>
              <td>${escapeHtml(c.full_name)}</td>
              <td>${escapeHtml(c.phone)}</td>
              <td>${escapeHtml(c.email)}</td>
              <td>${escapeHtml(c.notes)}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  `;

  document.getElementById("customerForm").addEventListener("submit", async e => {
    e.preventDefault();

    await api("/customers", {
      method: "POST",
      body: JSON.stringify({
        full_name: document.getElementById("cName").value,
        phone: document.getElementById("cPhone").value || null,
        email: document.getElementById("cEmail").value || null,
        notes: document.getElementById("cNotes").value || null
      })
    });

    customers();
  });
}

async function serviceForm(type) {
  const customers = await api("/customers");
  const title = type === "people" ? "People transportation" : "Object transportation";

  document.getElementById("content").innerHTML = `
    <h1>${title}</h1>
    <p class="muted">Register a new service.</p>

    ${customers.length === 0
      ? `<div class="form-card">
           <p>No customers exist yet.</p>
           <button class="primary" onclick="loadPage('customers')">CREATE CUSTOMER FIRST</button>
         </div>`
      : `
      <form class="form-card" id="serviceForm">
        <div class="grid2">
          <div>
            <label>Customer</label>
            <select id="sCustomer" required>
              ${customers.map(c => `<option value="${c.id}">${escapeHtml(c.full_name)} · ${escapeHtml(c.phone)}</option>`).join("")}
            </select>
          </div>

          <div>
            <label>Date</label>
            <input id="sDate" type="date" required>
          </div>

          <div>
            <label>Time</label>
            <input id="sTime" type="time" required>
          </div>

          <div>
            <label>Price</label>
            <input id="sPrice" type="number" min="0" step="0.01" value="0" required>
          </div>

          <div>
            <label>Origin</label>
            <input id="sOrigin" required>
          </div>

          <div>
            <label>Destination</label>
            <input id="sDestination" required>
          </div>

          ${type === "people" ? `
            <div>
              <label>Passengers</label>
              <input id="sPassengers" type="number" min="1" value="1" required>
            </div>
          ` : `
            <div>
              <label>Object description</label>
              <input id="sObject" required>
            </div>
            <div>
              <label>Quantity</label>
              <input id="sQuantity" type="number" min="1" value="1" required>
            </div>
          `}

          <div>
            <label>Status</label>
            <select id="sStatus">
              <option value="pending">Pending</option>
              <option value="scheduled">Scheduled</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
        </div>

        <label>Notes</label>
        <textarea id="sNotes"></textarea>

        <br>
        <button class="primary">SAVE SERVICE</button>
      </form>
    `}

    <div class="form-card">
      <h3>Important</h3>
      <p class="muted">
        The employee records the service. There is no automatic package GPS tracking.
        Payment is recorded separately and can be marked as paid face-to-face.
      </p>
    </div>
  `;

  const form = document.getElementById("serviceForm");
  if (!form) return;

  const now = new Date();
  document.getElementById("sDate").value = now.toISOString().slice(0, 10);
  document.getElementById("sTime").value =
    now.toTimeString().slice(0, 5);

  form.addEventListener("submit", async e => {
    e.preventDefault();

    const payload = {
      customer_id: Number(document.getElementById("sCustomer").value),
      service_type: type,
      origin: document.getElementById("sOrigin").value,
      destination: document.getElementById("sDestination").value,
      service_date: document.getElementById("sDate").value,
      service_time: document.getElementById("sTime").value,
      price: Number(document.getElementById("sPrice").value),
      status: document.getElementById("sStatus").value,
      notes: document.getElementById("sNotes").value || null
    };

    if (type === "people") {
      payload.passengers = Number(document.getElementById("sPassengers").value);
    } else {
      payload.object_description = document.getElementById("sObject").value;
      payload.quantity = Number(document.getElementById("sQuantity").value);
    }

    await api("/services", {
      method: "POST",
      body: JSON.stringify(payload)
    });

    alert("Service created.");
    loadPage("records");
  });
}

async function records() {
  const data = await api("/services");

  document.getElementById("content").innerHTML = `
    <h1>Service records</h1>
    <p class="muted">${data.length} registered services</p>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Type</th>
            <th>Customer</th>
            <th>Route</th>
            <th>Date</th>
            <th>Employee</th>
            <th>Price</th>
            <th>Status</th>
            <th>Payment</th>
          </tr>
        </thead>
        <tbody>
          ${data.map(s => `
            <tr>
              <td>${s.id}</td>
              <td>${s.service_type}</td>
              <td>${escapeHtml(s.customer_name)}</td>
              <td>${escapeHtml(s.origin)} → ${escapeHtml(s.destination)}</td>
              <td>${s.service_date} ${String(s.service_time).slice(0,5)}</td>
              <td>${escapeHtml(s.employee_name)}</td>
              <td>$${Number(s.price).toLocaleString()}</td>
              <td><span class="badge">${escapeHtml(s.status)}</span></td>
              <td>
                ${s.payment_status === "paid"
                  ? `<span class="success">PAID</span>`
                  : `<button class="secondary" onclick="markPaid(${s.id}, ${Number(s.price)})">MARK PAID</button>`}
              </td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  `;
}

async function markPaid(serviceId, amount) {
  await api(`/services/${serviceId}/payment`, {
    method: "POST",
    body: JSON.stringify({
      amount,
      payment_method: "cash",
      payment_status: "paid"
    })
  });

  records();
}

async function employees() {
  const data = await api("/employees");

  document.getElementById("content").innerHTML = `
    <h1>Employees</h1>
    <p class="muted">8 employee accounts. Passwords are stored only as secure hashes.</p>

    <div class="table-wrap">
      <table>
        <thead><tr><th>ID</th><th>Username</th><th>Name</th><th>Role</th><th>Active</th></tr></thead>
        <tbody>
          ${data.map(e => `
            <tr>
              <td>${e.id}</td>
              <td>${escapeHtml(e.username)}</td>
              <td>${escapeHtml(e.full_name)}</td>
              <td>${escapeHtml(e.role)}</td>
              <td>${e.active ? '<span class="success">YES</span>' : 'NO'}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  `;
}

async function boot() {
  if (!token) {
    renderLogin();
    return;
  }

  try {
    currentUser = await api("/me");
    renderApp();
  } catch {
    logout();
  }
}

boot();
