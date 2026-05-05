/* ============================================================
   Void Media — sign-log.js
   Handles: tab switching, login, signup, particles, utilities
   ============================================================ */

"use strict";

/* ── Tab switching ───────────────────────────────────────── */
function switchTab(tabName) {
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.tab === tabName);
  });
  document.querySelectorAll(".tab-panel").forEach((panel) => {
    panel.classList.toggle("active", panel.id === "tab-" + tabName);
  });
}

document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => switchTab(btn.dataset.tab));
});

document.querySelectorAll(".switch-tab").forEach((link) => {
  link.addEventListener("click", () => switchTab(link.dataset.tab));
});

/* ── Toast notification ──────────────────────────────────── */
function showToast(message, type = "success") {
  let toast = document.querySelector(".toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.className = "toast";
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.className = `toast ${type}`;
  // Force reflow to restart animation
  void toast.offsetWidth;
  toast.classList.add("show");
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => toast.classList.remove("show"), 3000);
}

/* ── Password visibility toggle ─────────────────────────── */
document.querySelectorAll(".toggle-pw").forEach((btn) => {
  btn.addEventListener("click", () => {
    const input = document.getElementById(btn.dataset.target);
    const icon  = btn.querySelector("i");
    if (!input) return;
    const isPassword = input.type === "password";
    input.type = isPassword ? "text" : "password";
    icon.classList.toggle("fa-eye",        !isPassword);
    icon.classList.toggle("fa-eye-slash",   isPassword);
  });
});

/* ── Enter-key field navigation ─────────────────────────── */
document.getElementById("name")?.addEventListener("keydown", (e) => {
  if (e.key === "Enter") document.getElementById("password")?.focus();
});

document.getElementById("addname")?.addEventListener("keydown", (e) => {
  if (e.key === "Enter") document.getElementById("addpassword")?.focus();
});

/* ── Sign Up ─────────────────────────────────────────────── */
async function handleSignup() {
  const addname     = document.getElementById("addname")?.value.trim();
  const addpassword = document.getElementById("addpassword")?.value.trim();
  const btn         = document.getElementById("signupbtn");

  if (!addname || !addpassword) {
    showToast("Please fill in both fields", "error");
    return;
  }

  btn.classList.add("loading");
  btn.textContent = "Creating...";

  try {
    const res  = await fetch("/add", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ addname, addpassword }),
    });
    const data = await res.json();

    if (data.message === "saved successfully") {
      showToast("Account created! You can now log in.", "success");
      document.getElementById("addname").value     = "";
      document.getElementById("addpassword").value = "";
      setTimeout(() => switchTab("login"), 1200);
    } else {
      showToast(data.error || "Username already taken", "error");
    }
  } catch (err) {
    console.error(err);
    showToast("Could not connect to server", "error");
  } finally {
    btn.classList.remove("loading");
    btn.textContent = "Create Account";
  }
}

document.getElementById("signupbtn")?.addEventListener("click", handleSignup);

document.getElementById("addpassword")?.addEventListener("keydown", (e) => {
  if (e.key === "Enter") handleSignup();
});

/* ── Log In ──────────────────────────────────────────────── */
async function handleLogin() {
  const name     = document.getElementById("name")?.value.trim();
  const password = document.getElementById("password")?.value.trim();
  const btn      = document.getElementById("loginbtn");

  if (!name || !password) {
    showToast("Please fill in both fields", "error");
    return;
  }

  btn.classList.add("loading");
  btn.textContent = "Signing in...";

  try {
    const res  = await fetch("/login", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ name, password }),
    });
    const data = await res.json();

    if (data.message === "login successfull") {
      showToast("Welcome back!", "success");
      setTimeout(() => (window.location.href = "/showposts"), 800);
    } else {
      showToast(data.message || data.error || "Invalid credentials", "error");
    }
  } catch (err) {
    console.error(err);
    showToast("Could not connect to server", "error");
  } finally {
    btn.classList.remove("loading");
    btn.textContent = "Log In";
  }
}

document.getElementById("loginbtn")?.addEventListener("click", handleLogin);

document.getElementById("password")?.addEventListener("keydown", (e) => {
  if (e.key === "Enter") handleLogin();
});

/* ── Floating particles (canvas) ─────────────────────────── */
(function initParticles() {
  const canvas = document.getElementById("particles");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  let W, H;

  const pts = Array.from({ length: 65 }, () => ({
    x:  Math.random() * window.innerWidth,
    y:  Math.random() * window.innerHeight,
    r:  Math.random() * 1.3 + 0.2,
    vx: (Math.random() - 0.5) * 0.22,
    vy: (Math.random() - 0.5) * 0.22,
    a:  Math.random() * 0.32 + 0.05,
  }));

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener("resize", resize);

  function draw() {
    ctx.clearRect(0, 0, W, H);
    pts.forEach((p) => {
      p.x = (p.x + p.vx + W) % W;
      p.y = (p.y + p.vy + H) % H;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(123,92,255,${p.a})`;
      ctx.fill();
    });
    requestAnimationFrame(draw);
  }
  draw();
})();

/* ── Post creation (for /showposts page) ─────────────────── */
document.getElementById("postBtn")?.addEventListener("click", async () => {
  const content = document.getElementById("post")?.value;
  if (!content) return showToast("Write something first!", "error");

  try {
    const res  = await fetch("/posts", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ content }),
    });
    const data = await res.json();
    if (data.error)   return showToast(data.error, "error");
    if (data.message) location.reload();
  } catch (err) {
    console.error(err);
    showToast("Error posting. See console.", "error");
  }
});

document.querySelector(".postInput")?.addEventListener("keydown", async (e) => {
  if (e.key !== "Enter") return;
  const content = document.querySelector(".postInput")?.value;
  if (!content) return showToast("Write something first!", "error");
  try {
    const res  = await fetch("/posts", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ content }),
    });
    const data = await res.json();
    if (data.error)   return showToast(data.error, "error");
    if (data.message) location.reload();
  } catch (err) {
    console.error(err);
    showToast("Error posting.", "error");
  }
});

/* ── Friend requests ─────────────────────────────────────── */
document.getElementById("sendRequestBtn")?.addEventListener("click", async () => {
  const friendId = document.getElementById("friendId")?.value.trim();
  if (!friendId) return showToast("Enter a valid friend ID!", "error");
  const res  = await fetch("/send_friend_request", {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ friendId }),
  });
  const data = await res.json();
  showToast(data.message || data.error, data.message ? "success" : "error");
});

document.getElementById("acceptRequestBtn")?.addEventListener("click", async () => {
  const requestId = document.getElementById("requestId")?.value.trim();
  if (!requestId) return showToast("Enter a valid request ID!", "error");
  const res  = await fetch("/accept_friend_request", {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ requestId }),
  });
  const data = await res.json();
  showToast(data.message || data.error, data.message ? "success" : "error");
});

/* ── Search ──────────────────────────────────────────────── */
document.getElementById("who")?.addEventListener("input", async (e) => {
  const query            = e.target.value.trim();
  const resultsContainer = document.getElementById("searchResults");
  if (!query) { resultsContainer.innerHTML = ""; return; }

  const res  = await fetch(`/searchbar?who=${encodeURIComponent(query)}`);
  const data = await res.json();

  resultsContainer.innerHTML =
    data && data.length > 0
      ? data
          .map(
            (user) => `
        <div class="search-result">
          <img src="static/images/${user.imgpath}" alt="Profile">
          <p>${user.name}</p>
          <button onclick="sendFriendRequest(${user.user_id})">Add Friend</button>
        </div>`
          )
          .join("")
      : "<p>No users found</p>";
});

/* ── Edit name ───────────────────────────────────────────── */
document.getElementById("saveNameBtn")?.addEventListener("click", async () => {
  const newname = document.getElementById("newname")?.value.trim();
  if (!newname) return showToast("Enter a name!", "error");
  const res  = await fetch("/editname", {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ newname }),
  });
  const data = await res.json();
  showToast(data.message || data.error, data.message ? "success" : "error");
  if (data.message) setTimeout(() => (window.location.href = "/profile"), 1000);
});

/* ── Edit description ────────────────────────────────────── */
async function saveDesc() {
  const desc = document.getElementById("desc")?.value.trim();
  if (!desc) return showToast("Description cannot be empty!", "error");
  const res  = await fetch("/descupdate", {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ desc }),
  });
  const data = await res.json();
  showToast(data.message || data.error || "Failed to update", data.message ? "success" : "error");
}

document.getElementById("saveDescBtn")?.addEventListener("click", saveDesc);
document.getElementById("desc")?.addEventListener("keydown", (e) => {
  if (e.key === "Enter") saveDesc();
});

/* ── Auto-refresh on posts page ──────────────────────────── */
setInterval(() => {
  if (window.location.pathname === "/showposts") location.reload();
}, 25000);

console.log("Void Media — sign-log.js loaded ✓");
