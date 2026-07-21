/* ============================================================
   PlacementAI – Auth & Dashboard JavaScript
   ============================================================ */

// ── Dashboard Init ───────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Animate progress bars
  document.querySelectorAll('.progress-bar').forEach(bar => {
    const width = bar.style.width;
    bar.style.width = '0%';
    setTimeout(() => {
      bar.style.transition = 'width 1.2s cubic-bezier(0.4, 0, 0.2, 1)';
      bar.style.width = width;
    }, 200);
  });

  // Animate SVG rings
  document.querySelectorAll('circle[stroke-dashoffset]').forEach(circle => {
    const offset = circle.getAttribute('stroke-dashoffset');
    circle.style.strokeDashoffset = circle.getAttribute('stroke-dasharray') || '251.3';
    circle.style.transition = 'stroke-dashoffset 1.5s cubic-bezier(0.4, 0, 0.2, 1) 0.3s';
    setTimeout(() => {
      circle.style.strokeDashoffset = offset;
    }, 100);
  });

  // Sidebar active highlight
  const currentPath = window.location.pathname;
  document.querySelectorAll('.sidebar-link').forEach(link => {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });
});

// ── Global Search ────────────────────────────────────────
const searchPages = [
  { name: 'Dashboard', url: '/student/dashboard', icon: '📊' },
  { name: 'AI Prediction', url: '/predict/', icon: '🤖' },
  { name: 'My Profile', url: '/student/profile', icon: '👤' },
  { name: 'Skill Assessment', url: '/student/skills', icon: '⚡' },
  { name: 'Projects', url: '/student/projects', icon: '💻' },
  { name: 'Internships', url: '/student/internships', icon: '🏢' },
  { name: 'Certificates', url: '/student/certificates', icon: '🏅' },
  { name: 'Coding Profile', url: '/student/coding-profile', icon: '🖥️' },
  { name: 'AI Career Advisor', url: '/student/ai-advisor', icon: '🤖' },
  { name: 'Interview Prep', url: '/student/interview-prep', icon: '🎤' },
  { name: 'Eligible Companies', url: '/predict/eligible-companies', icon: '🏢' },
  { name: 'Goals Tracker', url: '/student/goals', icon: '🎯' },
  { name: 'Leaderboard', url: '/student/leaderboard', icon: '🏆' },
  { name: 'Notifications', url: '/student/notifications', icon: '🔔' },
  { name: 'Settings', url: '/student/settings', icon: '⚙️' },
];

let searchDropdown = null;

const searchInput = document.getElementById('globalSearch');
if (searchInput) {
  searchInput.addEventListener('input', (e) => {
    const q = e.target.value.trim().toLowerCase();
    if (searchDropdown) searchDropdown.remove();

    if (!q) return;

    const results = searchPages.filter(p => p.name.toLowerCase().includes(q));
    if (!results.length) return;

    searchDropdown = document.createElement('div');
    searchDropdown.style.cssText = `
      position: absolute;
      top: calc(100% + 6px);
      left: 0; right: 0;
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow-lg);
      z-index: 2000;
      overflow: hidden;
    `;

    results.slice(0, 6).forEach(page => {
      const item = document.createElement('a');
      item.href = page.url;
      item.style.cssText = `
        display: flex; align-items: center; gap: 12px;
        padding: 10px 14px; font-size: 0.875rem;
        color: var(--text-secondary); text-decoration: none;
        transition: background 0.15s;
        border-bottom: 1px solid var(--border);
      `;
      item.innerHTML = `<span>${page.icon}</span><span>${page.name}</span>`;
      item.addEventListener('mouseenter', () => item.style.background = 'var(--bg-hover)');
      item.addEventListener('mouseleave', () => item.style.background = '');
      searchDropdown.appendChild(item);
    });

    const wrapper = searchInput.closest('.nav-search');
    if (wrapper) {
      wrapper.style.position = 'relative';
      wrapper.appendChild(searchDropdown);
    }
  });

  document.addEventListener('click', (e) => {
    if (!e.target.closest('.nav-search')) {
      searchDropdown?.remove();
      searchDropdown = null;
    }
  });
}
