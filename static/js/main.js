/* ============================================================
   PlacementAI – Main JavaScript
   Global utilities, theme, toast, dropdown, sidebar
   ============================================================ */

// ── Toast Notifications ──────────────────────────────────
function showToast(message, type = 'info', duration = 4000) {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const icons = { success: '✅', danger: '❌', warning: '⚠️', info: 'ℹ️' };
  const colors = { success: 'var(--accent-green)', danger: 'var(--accent-red)', warning: 'var(--accent-orange)', info: 'var(--primary-light)' };

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.style.cssText = `pointer-events: all; border-left: 3px solid ${colors[type] || colors.info};`;
  toast.innerHTML = `
    <span style="font-size:1.1rem; flex-shrink:0;">${icons[type] || icons.info}</span>
    <span style="flex:1; font-size:0.875rem; color:var(--text-primary); line-height:1.4;">${message}</span>
    <button onclick="dismissToast(this.parentElement)" style="background:none; border:none; color:var(--text-muted); cursor:pointer; font-size:1rem; padding:0; line-height:1;">✕</button>
  `;

  container.appendChild(toast);

  // Auto-dismiss
  const timer = setTimeout(() => dismissToast(toast), duration);
  toast._timer = timer;
}

function dismissToast(toast) {
  if (!toast || toast._dismissed) return;
  toast._dismissed = true;
  if (toast._timer) clearTimeout(toast._timer);
  toast.classList.add('leaving');
  setTimeout(() => toast.remove(), 350);
}

// ── Theme Toggle ─────────────────────────────────────────
const THEME_KEY = 'placementai-theme';

function getTheme() { return localStorage.getItem(THEME_KEY) || 'dark'; }

function setTheme(theme) {
  localStorage.setItem(THEME_KEY, theme);
  document.documentElement.setAttribute('data-theme', theme);
  const icon = document.getElementById('themeIcon');
  if (icon) {
    icon.setAttribute('data-lucide', theme === 'dark' ? 'sun' : 'moon');
    if (typeof lucide !== 'undefined') lucide.createIcons();
  }
}

function toggleTheme() {
  const current = getTheme();
  setTheme(current === 'dark' ? 'light' : 'dark');
}

// Initialize theme
document.addEventListener('DOMContentLoaded', () => {
  setTheme(getTheme());
  const themeBtn = document.getElementById('themeToggle');
  if (themeBtn) themeBtn.addEventListener('click', toggleTheme);
});

// ── Dropdown Toggle ──────────────────────────────────────
function toggleDropdown(id) {
  const dropdown = document.getElementById(id);
  if (!dropdown) return;
  const isOpen = dropdown.classList.contains('open');

  // Close all others
  document.querySelectorAll('.dropdown.open').forEach(d => d.classList.remove('open'));

  if (!isOpen) dropdown.classList.add('open');
}

// Close dropdowns on outside click
document.addEventListener('click', (e) => {
  if (!e.target.closest('.dropdown')) {
    document.querySelectorAll('.dropdown.open').forEach(d => d.classList.remove('open'));
  }
});

// ── Sidebar Toggle ───────────────────────────────────────
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  const main = document.getElementById('mainContent');

  if (window.innerWidth <= 768) {
    sidebar.classList.toggle('mobile-open');
    overlay.classList.toggle('active');
  } else {
    sidebar.classList.toggle('collapsed');
    if (main) main.classList.toggle('sidebar-collapsed');
    localStorage.setItem('sidebar-collapsed', sidebar.classList.contains('collapsed'));
  }
}

function closeSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  sidebar.classList.remove('mobile-open');
  overlay.classList.remove('active');
}

document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('sidebarToggle');
  if (toggleBtn) toggleBtn.addEventListener('click', toggleSidebar);

  // Restore sidebar state
  const isCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
  if (isCollapsed && window.innerWidth > 768) {
    document.getElementById('sidebar')?.classList.add('collapsed');
    document.getElementById('mainContent')?.classList.add('sidebar-collapsed');
  }
});

// ── Password Toggle ──────────────────────────────────────
function togglePassword(inputId, btn) {
  const input = document.getElementById(inputId);
  if (!input) return;
  const isText = input.type === 'text';
  input.type = isText ? 'password' : 'text';
  const icon = btn.querySelector('i');
  if (icon) {
    icon.setAttribute('data-lucide', isText ? 'eye' : 'eye-off');
    if (typeof lucide !== 'undefined') lucide.createIcons();
  }
}

// ── Password Strength ────────────────────────────────────
function checkPasswordStrength(password) {
  const bars = [1, 2, 3, 4].map(i => document.getElementById(`sBar${i}`));
  const label = document.getElementById('strengthLabel');
  if (!label) return;

  const hasUpper = /[A-Z]/.test(password);
  const hasLower = /[a-z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  const hasSpecial = /[^A-Za-z0-9]/.test(password);
  const isLong = password.length >= 8;

  let strength = 0;
  if (isLong) strength++;
  if (hasUpper && hasLower) strength++;
  if (hasNumber) strength++;
  if (hasSpecial) strength++;

  const levels = ['', 'weak', 'fair', 'good', 'strong'];
  const labels = ['Enter a password', 'Too weak', 'Could be stronger', 'Good password', 'Strong password!'];

  bars.forEach((bar, idx) => {
    bar.className = 'strength-bar';
    if (idx < strength && password.length > 0) {
      bar.classList.add('active', levels[strength]);
    }
  });

  label.textContent = password.length === 0 ? labels[0] : labels[strength];
  label.style.color = ['', 'var(--accent-red)', 'var(--accent-orange)', 'var(--accent)', 'var(--accent-green)'][strength];
}

// ── FAQ Accordion ────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.faq-question').forEach(btn => {
    btn.addEventListener('click', () => {
      const item = btn.closest('.faq-item');
      const isOpen = item.classList.contains('open');
      document.querySelectorAll('.faq-item.open').forEach(i => i.classList.remove('open'));
      if (!isOpen) item.classList.add('open');
    });
  });
});

// ── Tabs ─────────────────────────────────────────────────
function switchTab(tabId, contentId) {
  // Hide all tab contents in same parent
  const panel = document.getElementById(contentId)?.closest('[data-tab-panel]');
  if (panel) {
    panel.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    panel.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  } else {
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  }
  document.getElementById(contentId)?.classList.add('active');
  document.getElementById(tabId)?.classList.add('active');
}

// ── Modal ─────────────────────────────────────────────────
function openModal(id) {
  const overlay = document.getElementById(id);
  if (overlay) {
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
}

function closeModal(id) {
  const overlay = document.getElementById(id);
  if (overlay) {
    overlay.classList.remove('open');
    document.body.style.overflow = '';
  }
}

// Close modal on overlay click
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('open');
    document.body.style.overflow = '';
  }
});

// Close modal on Escape
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.open').forEach(o => {
      o.classList.remove('open');
      document.body.style.overflow = '';
    });
  }
});

// ── Scroll reveal ─────────────────────────────────────────
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

// ── Sticky Nav ────────────────────────────────────────────
const landingNav = document.getElementById('landingNav');
if (landingNav) {
  window.addEventListener('scroll', () => {
    landingNav.classList.toggle('scrolled', window.scrollY > 20);
  });
}

// ── Newsletter ────────────────────────────────────────────
function subscribeNewsletter() {
  const email = document.getElementById('newsletterEmail')?.value;
  if (!email || !/\S+@\S+\.\S+/.test(email)) {
    showToast('Please enter a valid email address.', 'warning');
    return;
  }
  showToast('Thank you for subscribing! 🎉', 'success');
  if (document.getElementById('newsletterEmail')) {
    document.getElementById('newsletterEmail').value = '';
  }
}

// ── API Helper ────────────────────────────────────────────
async function apiCall(url, method = 'GET', body = null) {
  const options = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body) options.body = JSON.stringify(body);

  try {
    const res = await fetch(url, options);
    const data = await res.json();
    return data;
  } catch (e) {
    console.error('API Error:', e);
    showToast('Network error. Please try again.', 'danger');
    return null;
  }
}

// ── Global Keyboard Shortcuts ─────────────────────────────
document.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === '/') {
    e.preventDefault();
    document.getElementById('globalSearch')?.focus();
  }
});

// ── Confirm dialog ─────────────────────────────────────────
function confirmAction(message, onConfirm) {
  if (window.confirm(message)) onConfirm();
}

// ── Initialize ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  if (typeof lucide !== 'undefined') lucide.createIcons();

  // Observe reveal elements added after load
  document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

  // Range input value display
  document.querySelectorAll('input[type="range"]').forEach(input => {
    const display = document.getElementById(input.id + '_val');
    if (display) {
      display.textContent = input.value;
      input.addEventListener('input', () => display.textContent = input.value);
    }
  });
});
