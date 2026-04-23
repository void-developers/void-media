'use strict';

/* ── Particles ───────────────────────────────────────── */
const canvas = document.getElementById('particles');
const ctx    = canvas.getContext('2d');
let W, H;

function resizeCanvas() {
  W = canvas.width  = window.innerWidth;
  H = canvas.height = window.innerHeight;
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

const pts = Array.from({ length: 45 }, () => ({
  x:  Math.random() * window.innerWidth,
  y:  Math.random() * window.innerHeight,
  r:  Math.random() * 1.2 + 0.3,
  dx: (Math.random() - 0.5) * 0.22,
  dy: (Math.random() - 0.5) * 0.22,
  o:  Math.random() * 0.35 + 0.08
}));

(function drawParticles() {
  ctx.clearRect(0, 0, W, H);
  pts.forEach(p => {
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(123,92,255,${p.o})`;
    ctx.fill();
    p.x += p.dx; p.y += p.dy;
    if (p.x < 0 || p.x > W) p.dx *= -1;
    if (p.y < 0 || p.y > H) p.dy *= -1;
  });
  requestAnimationFrame(drawParticles);
})();

/* ── Toast ───────────────────────────────────────────── */
const toastEl = document.getElementById('toast');
let toastTimer;

function showToast(msg) {
  toastEl.textContent = msg;
  toastEl.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toastEl.classList.remove('show'), 2600);
}

/* ── Ripple ──────────────────────────────────────────── */
function spawnRipple(el, e) {
  const rect = el.getBoundingClientRect();
  const rip  = document.createElement('span');
  rip.className  = 'ripple';
  rip.style.left = (e.clientX - rect.left) + 'px';
  rip.style.top  = (e.clientY - rect.top)  + 'px';
  el.appendChild(rip);
  setTimeout(() => rip.remove(), 700);
}

/* ── Save button ─────────────────────────────────────── */
const saveBtn   = document.getElementById('saveDescBtn');
const descInput = document.getElementById('desc');

saveBtn.addEventListener('click', function(e) {
  spawnRipple(this, e);

  const orig = this.textContent;
  this.textContent  = '✓ Saved!';
  this.style.background = '#22c55e';

  setTimeout(() => {
    this.textContent  = orig;
    this.style.background = '';
  }, 1800);

  showToast('Description saved ✦');
});

// Ctrl+S / Cmd+S shortcut
document.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    if (document.activeElement === descInput) {
      e.preventDefault();
      saveBtn.click();
    }
  }
});

/* ── Avatar 3D tilt ──────────────────────────────────── */
const avatarImg  = document.querySelector('.profile-top img');
const avatarWrap = document.querySelector('.avatar-wrap');

if (avatarImg && avatarWrap) {
  avatarWrap.addEventListener('mousemove', e => {
    const rect = avatarWrap.getBoundingClientRect();
    const dx   = (e.clientX - rect.left - rect.width  / 2) / (rect.width  / 2);
    const dy   = (e.clientY - rect.top  - rect.height / 2) / (rect.height / 2);
    avatarImg.style.transform = `scale(1.08) rotateY(${dx * 14}deg) rotateX(${-dy * 14}deg)`;
  });
  avatarWrap.addEventListener('mouseleave', () => {
    avatarImg.style.transform = '';
  });
}

/* ── Header hide on scroll down, show on scroll up ───── */
const header = document.querySelector('.header');
let lastScroll = 0;

window.addEventListener('scroll', () => {
  const cur = window.scrollY;
  header.style.transition = 'transform 0.3s ease';
  header.style.transform  = (cur > lastScroll && cur > 60)
    ? 'translateY(-100%)'
    : 'translateY(0)';
  lastScroll = cur;
}, { passive: true });

/* ── Nav link ripple ─────────────────────────────────── */
document.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', e => spawnRipple(link, e));
});

/* ── Button ripple (all buttons) ─────────────────────── */
document.querySelectorAll('button').forEach(btn => {
  btn.addEventListener('click', e => spawnRipple(btn, e));
});