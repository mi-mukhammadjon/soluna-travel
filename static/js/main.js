/* ============================================================
   SoLuna main.js — Travila interactions
   ============================================================ */
(function () {
  'use strict';

  /* ── 1. Scroll Reveal ───────────────────────────────────── */
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add('revealed');
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -50px 0px' });

    document.querySelectorAll('.reveal').forEach(el => io.observe(el));
  } else {
    document.querySelectorAll('.reveal').forEach(el => el.classList.add('revealed'));
  }

  /* ── 2. Page Transition Overlay ─────────────────────────── */
  const overlay = document.getElementById('pageTransition');
  const isInternalLink = (a) => {
    if (!a) return false;
    if (a.target === '_blank') return false;
    if (a.dataset.noTransition !== undefined) return false;
    if (a.hasAttribute('download')) return false;
    const href = a.getAttribute('href');
    if (!href) return false;
    if (href.startsWith('#')) return false;
    if (href.startsWith('mailto:') || href.startsWith('tel:')) return false;
    if (href.startsWith('http') && !href.startsWith(window.location.origin)) return false;
    return true;
  };

  if (overlay) {
    // Animate IN on load
    requestAnimationFrame(() => {
      overlay.classList.add('entering');
      setTimeout(() => overlay.classList.remove('entering', 'exiting'), 600);
    });

    // Animate OUT on internal link click
    document.addEventListener('click', (e) => {
      const a = e.target.closest('a');
      if (!isInternalLink(a)) return;

      e.preventDefault();
      overlay.classList.add('exiting');
      setTimeout(() => { window.location.href = a.href; }, 380);
    });
  }

  /* ── 3. Header shadow on scroll ─────────────────────────── */
  const header = document.getElementById('header');
  if (header) {
    let lastY = 0;
    window.addEventListener('scroll', () => {
      const y = window.scrollY;
      if (y > 20) header.classList.add('is-scrolled');
      else header.classList.remove('is-scrolled');
      lastY = y;
    }, { passive: true });
  }

  /* ── 4. Mobile Nav Toggle ───────────────────────────────── */
  const navToggle = document.getElementById('navToggle');
  if (navToggle) {
    navToggle.addEventListener('click', () => {
      document.body.classList.toggle('nav-open');
    });
  }

  /* ── 5. Search Tabs (Tours / Hotels / Tickets / ...) ───── */
  document.querySelectorAll('.search-tabs').forEach(group => {
    const tabs = group.querySelectorAll('.search-tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('is-active'));
        tab.classList.add('is-active');
      });
    });
  });

  /* ── 6. Tour Card Favorite (heart icon toggle) ─────────── */
  document.addEventListener('click', (e) => {
    const fav = e.target.closest('.tour-card-fav');
    if (!fav) return;
    e.preventDefault();
    e.stopPropagation();
    fav.classList.toggle('is-fav');
    const icon = fav.querySelector('i');
    if (icon) {
      if (fav.classList.contains('is-fav')) {
        icon.className = 'ti ti-heart-filled';
        // TODO: POST to /api/favorites/<id>/toggle/
      } else {
        icon.className = 'ti ti-heart';
      }
    }
  });

  /* ── 7. Tabs on tour detail (#overview / #itinerary / ...) ─ */
  const tabLinks = document.querySelectorAll('.td-tab');
  if (tabLinks.length) {
    tabLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        // Visual active state
        tabLinks.forEach(t => t.classList.remove('is-active'));
        link.classList.add('is-active');
      });
    });

    // Auto-highlight on scroll
    if ('IntersectionObserver' in window) {
      const sections = document.querySelectorAll('.td-section');
      if (sections.length) {
        const sectIo = new IntersectionObserver((entries) => {
          entries.forEach(e => {
            if (e.isIntersecting) {
              const id = e.target.id;
              tabLinks.forEach(t => {
                t.classList.toggle('is-active', t.getAttribute('href') === '#' + id);
              });
            }
          });
        }, { threshold: 0.25, rootMargin: '-100px 0px -50% 0px' });
        sections.forEach(s => sectIo.observe(s));
      }
    }
  }

  /* ── 8. Auto-hide flash messages ──────────────────────── */
  document.querySelectorAll('.messages-container .alert').forEach((el, i) => {
    setTimeout(() => {
      el.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      el.style.opacity = '0';
      el.style.transform = 'translateX(20px)';
      setTimeout(() => el.remove(), 400);
    }, 4000 + i * 500);
  });

  /* ── 9. Counter animation (stat numbers) ───────────────── */
  if ('IntersectionObserver' in window) {
    const animateNumber = (el) => {
      const text = el.textContent.trim();
      const match = text.match(/^([\d,.]+)([+KMB]*)$/);
      if (!match) return;
      const target = parseFloat(match[1].replace(/,/g, ''));
      const suffix = match[2] || '';
      if (isNaN(target)) return;

      const duration = 1400;
      const start = performance.now();
      el.textContent = '0' + suffix;

      const tick = (now) => {
        const p = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - p, 3);
        const cur = target * eased;
        const display = cur >= 1000 ? Math.round(cur).toLocaleString() : (target % 1 ? cur.toFixed(1) : Math.round(cur));
        el.textContent = display + suffix;
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    };

    const statIo = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          animateNumber(e.target);
          statIo.unobserve(e.target);
        }
      });
    }, { threshold: 0.3 });

    document.querySelectorAll('.stat-num').forEach(el => statIo.observe(el));
  }

  /* ── 10. Smooth scroll for in-page anchors ─────────────── */
  document.querySelectorAll('a[href^="#"]:not([href="#"])').forEach(a => {
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href').slice(1);
      const target = document.getElementById(id);
      if (!target) return;
      e.preventDefault();
      const top = target.getBoundingClientRect().top + window.scrollY - 110;
      window.scrollTo({ top, behavior: 'smooth' });
    });
  });

})();