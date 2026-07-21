/* ============================================================
   PlacementAI – Landing Page JavaScript
   Animations, counter, particle effects, scroll behavior
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // ── Animated Counters ──────────────────────────────────
  function animateCounter(el, target, duration = 2000, isFloat = false) {
    let start = 0;
    const increment = target / (duration / 16);
    const timer = setInterval(() => {
      start += increment;
      if (start >= target) {
        start = target;
        clearInterval(timer);
      }
      el.textContent = isFloat ? start.toFixed(1) : Math.floor(start).toLocaleString();
    }, 16);
  }

  const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !entry.target.dataset.animated) {
        entry.target.dataset.animated = '1';
        const target = parseFloat(entry.target.dataset.count);
        animateCounter(entry.target, target, 2000);
      }
    });
  }, { threshold: 0.5 });

  document.querySelectorAll('[data-count]').forEach(el => counterObserver.observe(el));

  // ── FAQ Accordion ──────────────────────────────────────
  document.querySelectorAll('.faq-question').forEach(btn => {
    btn.addEventListener('click', () => {
      const item = btn.closest('.faq-item');
      const wasOpen = item.classList.contains('open');
      document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('open'));
      if (!wasOpen) item.classList.add('open');
    });
  });

  // ── Smooth Scroll for nav links ────────────────────────
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', (e) => {
      const id = link.getAttribute('href');
      if (id === '#') return;
      const target = document.querySelector(id);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ── Scroll Reveal ─────────────────────────────────────
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

  // ── Navbar Scroll ─────────────────────────────────────
  const nav = document.getElementById('landingNav');
  if (nav) {
    let lastScrollY = 0;
    window.addEventListener('scroll', () => {
      const scrollY = window.scrollY;
      nav.classList.toggle('scrolled', scrollY > 20);
      lastScrollY = scrollY;
    }, { passive: true });
  }

  // ── Mobile Menu ─────────────────────────────────────────
  const menuToggle = document.getElementById('menuToggle');
  const navLinks = document.querySelector('.nav-links-landing');

  if (menuToggle && navLinks) {
    let mobileMenuOpen = false;
    menuToggle.addEventListener('click', () => {
      mobileMenuOpen = !mobileMenuOpen;
      if (mobileMenuOpen) {
        navLinks.style.cssText = `
          display: flex;
          flex-direction: column;
          position: fixed;
          top: 70px; left: 0; right: 0;
          background: rgba(10, 10, 15, 0.98);
          backdrop-filter: blur(20px);
          padding: 1.5rem;
          border-bottom: 1px solid rgba(255,255,255,0.08);
          gap: 0.5rem;
          z-index: 999;
          animation: fadeInDown 0.3s ease forwards;
        `;
      } else {
        navLinks.style.display = 'none';
      }
    });

    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        mobileMenuOpen = false;
        navLinks.style.display = 'none';
      });
    });
  }

  // ── Particle Dots Background ──────────────────────────
  function createParticles() {
    const hero = document.querySelector('.hero');
    if (!hero) return;

    for (let i = 0; i < 30; i++) {
      const dot = document.createElement('div');
      dot.style.cssText = `
        position: absolute;
        width: ${Math.random() * 4 + 2}px;
        height: ${Math.random() * 4 + 2}px;
        border-radius: 50%;
        background: rgba(99, 102, 241, ${Math.random() * 0.5 + 0.1});
        left: ${Math.random() * 100}%;
        top: ${Math.random() * 100}%;
        animation: float ${Math.random() * 6 + 4}s ease-in-out infinite;
        animation-delay: ${Math.random() * 4}s;
        pointer-events: none;
        z-index: 0;
      `;
      hero.appendChild(dot);
    }
  }

  createParticles();

  // ── Typing Effect for Hero ─────────────────────────────
  const subtitleEl = document.querySelector('.hero-subtitle');
  if (subtitleEl) {
    subtitleEl.style.opacity = '0';
    subtitleEl.style.transform = 'translateY(10px)';
    setTimeout(() => {
      subtitleEl.style.transition = 'all 0.8s ease 0.5s';
      subtitleEl.style.opacity = '1';
      subtitleEl.style.transform = 'translateY(0)';
    }, 100);
  }

  // ── Pricing Toggle ─────────────────────────────────────
  const pricingToggle = document.getElementById('pricingToggle');
  if (pricingToggle) {
    pricingToggle.addEventListener('change', () => {
      const isAnnual = pricingToggle.checked;
      document.querySelectorAll('.pricing-price').forEach((price, i) => {
        const monthly = ['0', '299', '4999'][i] || '0';
        const annual = ['0', '199', '3499'][i] || '0';
        price.innerHTML = `<sup>₹</sup>${isAnnual ? annual : monthly}`;
      });
      document.querySelectorAll('.pricing-period').forEach((p, i) => {
        p.textContent = i === 0 ? 'forever · no credit card' :
          (isAnnual ? 'per month · billed annually' : 'per month · billed monthly');
      });
    });
  }

  // ── Predict Demo Form (if on landing) ─────────────────
  const demoForm = document.getElementById('demoPredictForm');
  if (demoForm) {
    demoForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const cgpa = parseFloat(document.getElementById('demoCGPA')?.value || 7.5);
      const tech = parseFloat(document.getElementById('demoTech')?.value || 7);
      const comm = parseFloat(document.getElementById('demoComm')?.value || 6);

      const score = Math.min(100, Math.max(10,
        cgpa * 10 + tech * 5 + comm * 4 + Math.random() * 5
      ));

      const resultEl = document.getElementById('demoPredictResult');
      if (resultEl) {
        resultEl.innerHTML = `
          <div style="text-align:center; padding:1rem;">
            <div style="font-size:2.5rem; font-weight:900; color:${score >= 60 ? '#10b981' : '#ef4444'};">${score.toFixed(0)}%</div>
            <div style="color:${score >= 60 ? '#10b981' : '#ef4444'}; font-weight:700;">${score >= 60 ? '✅ Likely Placed' : '⚠️ Needs Improvement'}</div>
            <p style="font-size:0.8rem; color:#94a3b8; margin-top:0.5rem;">
              ${score >= 60 ? 'Great profile! Sign up for detailed analysis.' : 'Sign up to get a detailed improvement plan!'}
            </p>
            <a href="/auth/signup" style="display:inline-block; margin-top:0.75rem;" class="btn btn-primary btn-sm">Get Full Prediction →</a>
          </div>
        `;
      }
    });
  }
});
