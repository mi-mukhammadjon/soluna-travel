/**
 * SoLuna — static/js/main.js
 * Saytning YAGONA JS fayli. base.html dagi inline <script> va
 * soluna-motion.js shu faylga birlashtirildi (DRY).
 * Ulash: <script defer src="{% static 'js/main.js' %}"></script>
 */

(function () {
  'use strict';

  const prefersReducedMotion =
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ════════════════════════════════════════
     1. NAVBAR — scroll holati
     ════════════════════════════════════════ */
  const navbar = document.getElementById('navbar');
  if (navbar) {
    let ticking = false;
    const updateNavbar = () => {
      navbar.classList.toggle('scrolled', window.scrollY > 60);
      ticking = false;
    };
    window.addEventListener('scroll', () => {
      if (!ticking) {
        requestAnimationFrame(updateNavbar);
        ticking = true;
      }
    }, { passive: true });
    updateNavbar();
  }

  /* ════════════════════════════════════════
     2. MOBIL MENYU
     ════════════════════════════════════════ */
  const toggle = document.getElementById('navToggle');
  const drawer = document.getElementById('navDrawer');

  function closeDrawer() {
    toggle?.classList.remove('open');
    drawer?.classList.remove('open');
    toggle?.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }

  toggle?.addEventListener('click', () => {
    const isOpen = drawer.classList.toggle('open');
    toggle.classList.toggle('open', isOpen);
    toggle.setAttribute('aria-expanded', String(isOpen));
    document.body.style.overflow = isOpen ? 'hidden' : '';
  });

  drawer?.querySelectorAll('a').forEach((link) =>
    link.addEventListener('click', closeDrawer)
  );

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeDrawer();
  });

  /* ════════════════════════════════════════
     3. SCROLL REVEAL — yagona observer, yagona klass (.revealed)
     ════════════════════════════════════════ */
  const revealEls = document.querySelectorAll('.reveal, .reveal-left, .reveal-scale');
  if (revealEls.length) {
    if (prefersReducedMotion) {
      revealEls.forEach((el) => el.classList.add('revealed'));
    } else {
      const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add('revealed');
            revealObserver.unobserve(e.target);
          }
        });
      }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

      revealEls.forEach((el) => revealObserver.observe(el));
    }
  }

  /* ════════════════════════════════════════
     4. SAHIFA O'TISH — yagona overlay (#pageTransition)
     ════════════════════════════════════════ */
  const overlay = document.getElementById('pageTransition');

  if (overlay && !prefersReducedMotion) {
    // Event delegation — har bir <a> ga alohida listener emas
    document.addEventListener('click', (e) => {
      const link = e.target.closest('a[href]');
      if (!link) return;

      const href = link.getAttribute('href');
      if (
        !href ||
        href.startsWith('#') ||
        href.startsWith('mailto:') ||
        href.startsWith('tel:') ||
        href.startsWith('javascript:') ||
        (href.startsWith('http') && !href.startsWith(window.location.origin)) ||
        link.target === '_blank' ||
        link.hasAttribute('download') ||
        link.dataset.noTransition !== undefined ||
        e.metaKey || e.ctrlKey || e.shiftKey
      ) return;

      e.preventDefault();
      overlay.classList.remove('entering');
      overlay.classList.add('exiting');
      setTimeout(() => { window.location.href = href; }, 430);
    });

    // bfcache (orqaga tugmasi) bilan ham ishlaydi
    window.addEventListener('pageshow', () => {
      overlay.classList.remove('exiting');
      overlay.classList.add('entering');
    });
  }

  /* ════════════════════════════════════════
     5. FLASH XABARLAR — avto yashirish
     ════════════════════════════════════════ */
  const alerts = document.querySelectorAll('.messages-container .alert');
  if (alerts.length) {
    setTimeout(() => {
      alerts.forEach((el) => {
        el.style.transition = 'opacity 0.5s, transform 0.5s';
        el.style.opacity = '0';
        el.style.transform = 'translateX(20px)';
        setTimeout(() => el.remove(), 500);
      });
    }, 4500);
  }

  /* ════════════════════════════════════════
     6. COUNTER — data-count + data-suffix
     FIX: suffix endi float qiymatlarga ham qo'shiladi
     ════════════════════════════════════════ */
  function animateCounter(el) {
    const raw = el.getAttribute('data-count');
    const target = parseFloat(raw);
    if (Number.isNaN(target)) return;

    const isFloat = raw.includes('.');
    const suffix = el.getAttribute('data-suffix') || '';
    const duration = 1800;
    const start = performance.now();

    const update = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const value = eased * target;
      el.textContent = (isFloat ? value.toFixed(1) : Math.round(value)) + suffix;
      if (progress < 1) requestAnimationFrame(update);
    };
    requestAnimationFrame(update);
  }

  const counterEls = document.querySelectorAll('[data-count]');
  if (counterEls.length) {
    const counterObserver = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting && !e.target.dataset.counted) {
          e.target.dataset.counted = '1';
          animateCounter(e.target);
          counterObserver.unobserve(e.target);
        }
      });
    }, { threshold: 0.5 });
    counterEls.forEach((el) => counterObserver.observe(el));
  }

  /* ════════════════════════════════════════
     7. HERO — kirish animatsiyasi + parallax
     FIX: parallax endi --parallax-y custom property orqali,
     scale transformini buzmaydi; rAF bilan throttle qilingan
     ════════════════════════════════════════ */
  document.querySelectorAll('.hero-enter').forEach((el, i) => {
    setTimeout(() => el.classList.add('entered'), 200 + i * 200);
  });

  const heroBg = document.getElementById('heroBg');
  if (heroBg) {
    heroBg.classList.add('loaded');

    if (!prefersReducedMotion) {
      let parallaxTicking = false;
      window.addEventListener('scroll', () => {
        if (!parallaxTicking) {
          requestAnimationFrame(() => {
            heroBg.style.setProperty('--parallax-y', `${window.scrollY * 0.25}px`);
            parallaxTicking = false;
          });
          parallaxTicking = true;
        }
      }, { passive: true });
    }
  }

  /* ════════════════════════════════════════
     8. FORMA SUBMIT — loading holati
     ════════════════════════════════════════ */
  document.querySelectorAll('form[data-loading]').forEach((form) => {
    form.addEventListener('submit', () => {
      const btn = form.querySelector('[type="submit"]');
      if (btn) {
        btn.classList.add('is-loading');
        btn.disabled = true;
      }
      if (!form.querySelector('.loader-line')) {
        const line = document.createElement('div');
        line.className = 'loader-line';
        line.style.marginTop = '1rem';
        form.appendChild(line);
      }
    });
  });

})();