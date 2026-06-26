/* ════════════════════════════════════════════════════════
   SoLuna — Main JS
   ════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  // ── DOM ready helper ─────────────────────────────────
  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {

    // ═══ HEADER SCROLL ═══
    const header = document.getElementById('header');
    if (header) {
      const onScroll = () => header.classList.toggle('is-scrolled', window.scrollY > 10);
      onScroll();
      window.addEventListener('scroll', onScroll, { passive: true });
    }

    // ═══ THEME TOGGLE ═══
    const themeBtn = document.getElementById('themeToggle');
    const iconLight = document.getElementById('themeIconLight');
    const iconDark = document.getElementById('themeIconDark');

    function applyTheme(theme) {
      document.documentElement.setAttribute('data-theme', theme);
      localStorage.setItem('soluna-theme', theme);
      if (iconLight && iconDark) {
        if (theme === 'dark') {
          iconLight.style.display = 'none';
          iconDark.style.display = '';
        } else {
          iconLight.style.display = '';
          iconDark.style.display = 'none';
        }
      }
    }
    applyTheme(localStorage.getItem('soluna-theme') || 'light');

    if (themeBtn) {
      themeBtn.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        applyTheme(current === 'dark' ? 'light' : 'dark');
      });
    }

    // ═══ CURRENCY SWITCHER ═══
    const currencySelect = document.getElementById('currencySelect');
    if (currencySelect) {
      const saved = localStorage.getItem('soluna-currency') || 'USD';
      currencySelect.value = saved;
      currencySelect.addEventListener('change', () => {
        localStorage.setItem('soluna-currency', currencySelect.value);
        // Notify other pages/scripts
        document.dispatchEvent(new CustomEvent('currency-changed', { detail: currencySelect.value }));
      });
    }

    // ═══ MOBILE DRAWER ═══
    const navToggle = document.getElementById('navToggle');
    const drawer = document.getElementById('drawer');
    const drawerClose = document.getElementById('drawerClose');
    const drawerBackdrop = document.getElementById('drawerBackdrop');

    function openDrawer() {
      drawer?.classList.add('is-open');
      drawerBackdrop?.classList.add('is-open');
      drawer?.setAttribute('aria-hidden', 'false');
      navToggle?.setAttribute('aria-expanded', 'true');
      document.body.style.overflow = 'hidden';
    }
    function closeDrawer() {
      drawer?.classList.remove('is-open');
      drawerBackdrop?.classList.remove('is-open');
      drawer?.setAttribute('aria-hidden', 'true');
      navToggle?.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    }
    navToggle?.addEventListener('click', openDrawer);
    drawerClose?.addEventListener('click', closeDrawer);
    drawerBackdrop?.addEventListener('click', closeDrawer);
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && drawer?.classList.contains('is-open')) closeDrawer();
    });

    // ═══ SEARCH OVERLAY ═══
    const searchToggle = document.getElementById('searchToggle');
    const searchOverlay = document.getElementById('searchOverlay');
    const searchClose = document.getElementById('searchClose');

    function openSearch() {
      searchOverlay?.classList.add('is-open');
      searchOverlay?.setAttribute('aria-hidden', 'false');
      setTimeout(() => searchOverlay?.querySelector('input')?.focus(), 100);
    }
    function closeSearch() {
      searchOverlay?.classList.remove('is-open');
      searchOverlay?.setAttribute('aria-hidden', 'true');
    }
    searchToggle?.addEventListener('click', openSearch);
    searchClose?.addEventListener('click', closeSearch);
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && searchOverlay?.classList.contains('is-open')) closeSearch();
      // Ctrl/Cmd + K — open search
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        openSearch();
      }
    });
    searchOverlay?.addEventListener('click', (e) => {
      if (e.target === searchOverlay) closeSearch();
    });

    // ═══ FLASH MESSAGES — AUTO-DISMISS ═══
    document.querySelectorAll('[data-auto-dismiss]').forEach((alert, idx) => {
      // Close button
      alert.querySelector('.alert-close')?.addEventListener('click', () => dismissAlert(alert));
      // Auto-dismiss after 6s + stagger
      setTimeout(() => dismissAlert(alert), 6000 + idx * 500);
    });
    function dismissAlert(alert) {
      alert.classList.add('is-leaving');
      setTimeout(() => alert.remove(), 300);
    }

    // ═══ BACK TO TOP ═══
    const backToTop = document.getElementById('backToTop');
    if (backToTop) {
      const onScrollBtn = () => backToTop.classList.toggle('is-visible', window.scrollY > 600);
      onScrollBtn();
      window.addEventListener('scroll', onScrollBtn, { passive: true });
      backToTop.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    }

    // ═══ PAGE TRANSITION ═══
    const pageTransition = document.getElementById('pageTransition');
    if (pageTransition) {
      // Enter animation
      pageTransition.classList.add('is-entering');
      setTimeout(() => pageTransition.classList.remove('is-entering'), 500);

      // Outgoing links transition
      document.querySelectorAll('a[href]').forEach(link => {
        const href = link.getAttribute('href');
        if (
          link.hasAttribute('data-no-transition') ||
          link.target === '_blank' ||
          !href ||
          href.startsWith('#') ||
          href.startsWith('mailto:') ||
          href.startsWith('tel:') ||
          // dropdown trigger — let it open the menu (hover/tap) instead of hijacking with the splash
          (link.parentElement && link.parentElement.classList.contains('nav-has-dropdown')) ||
          href.startsWith('http') && !href.includes(window.location.hostname)
        ) return;

        link.addEventListener('click', (e) => {
          if (e.metaKey || e.ctrlKey || e.shiftKey) return; // open in new tab
          e.preventDefault();
          pageTransition.classList.add('is-leaving');
          setTimeout(() => { window.location.href = href; }, 350);
        });
      });
    }

    // ═══ REVEAL ON SCROLL ═══
    window.initReveal = function(root) {
      const targets = (root || document).querySelectorAll('.reveal:not([data-rv])');
      if (!targets.length) return;
      if ('IntersectionObserver' in window) {
        const obs = new IntersectionObserver((entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              entry.target.classList.add('is-revealed');
              obs.unobserve(entry.target);
            }
          });
        }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });
        targets.forEach(el => { el.dataset.rv = '1'; obs.observe(el); });
      } else {
        targets.forEach(el => { el.dataset.rv = '1'; el.classList.add('is-revealed'); });
      }
    };
    window.initReveal();

    // ═══ NEWSLETTER FORM ═══
    document.querySelectorAll('.newsletter').forEach(form => {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const input = form.querySelector('input[type="email"]');
        const feedback = form.nextElementSibling;
        const btn = form.querySelector('.newsletter-btn');
        if (!input?.value) return;

        btn.disabled = true;
        try {
          const fd = new FormData(form);
          const res = await fetch(form.action, { method: 'POST', body: fd });
          const data = await res.json();
          if (feedback) {
            feedback.style.display = 'block';
            feedback.textContent = data.message || (data.ok ? 'Obuna muvaffaqiyatli!' : 'Xatolik yuz berdi.');
            feedback.style.color = data.ok ? '#4caf50' : '#f44336';
          }
          if (data.ok) input.value = '';
        } catch {
          if (feedback) {
            feedback.style.display = 'block';
            feedback.textContent = 'Xatolik yuz berdi. Qaytadan urinib ko\'ring.';
            feedback.style.color = '#f44336';
          }
        } finally {
          btn.disabled = false;
        }
      });
    });

    // ═══ DROPDOWN — Mobile/touch support ═══
    document.querySelectorAll('.nav-has-dropdown').forEach(item => {
      const link = item.querySelector('.nav-link, .nav-user-btn');
      if (!link) return;
      // Touch device — first click opens, second navigates
      link.addEventListener('click', (e) => {
        if (window.matchMedia('(hover: hover)').matches) return; // desktop
        const dropdown = item.querySelector('.nav-dropdown');
        if (!dropdown) return;
        if (!item.classList.contains('is-open')) {
          e.preventDefault();
          document.querySelectorAll('.nav-has-dropdown.is-open').forEach(o => o.classList.remove('is-open'));
          item.classList.add('is-open');
        } else {
          item.classList.remove('is-open');
        }
      });
    });
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.nav-has-dropdown')) {
        document.querySelectorAll('.nav-has-dropdown.is-open').forEach(o => o.classList.remove('is-open'));
      }
    });

  });
})();
/* ════════════════════════════════════════════════════════════
   LANG + CURRENCY SWITCHER — to'liq JS
   main.js OXIRIGA qo'shing
   ════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {

    // ════ LANGUAGE SWITCHER ════
    const langSwitcher = document.getElementById('langSwitcher');
    const langTrigger = document.getElementById('langTrigger');
    const langForm = document.getElementById('langForm');
    const langNext = document.getElementById('langNext');
    const langValue = document.getElementById('langValue');

    if (langSwitcher && langTrigger) {
      // Toggle
      langTrigger.addEventListener('click', (e) => {
        e.stopPropagation();
        // Boshqa dropdownlarni yopish
        document.querySelectorAll('.cur-switcher.is-open').forEach(s => s.classList.remove('is-open'));
        langSwitcher.classList.toggle('is-open');
        langTrigger.setAttribute('aria-expanded', langSwitcher.classList.contains('is-open'));
      });

      // Til tanlash
      langSwitcher.querySelectorAll('.lang-option').forEach(option => {
        option.addEventListener('click', (e) => {
          e.preventDefault();
          e.stopPropagation();

          const newLang = option.dataset.lang;
          const currentLang = document.documentElement.lang || langValue.value;

          if (newLang === currentLang) {
            langSwitcher.classList.remove('is-open');
            return;
          }

          // Loading
          option.classList.add('is-loading');

          // Scroll saqlash
          sessionStorage.setItem('soluna-scroll', window.scrollY.toString());

          // Form yangilab submit
          langValue.value = newLang;
          langNext.value = buildLangUrl(newLang);
          langForm.submit();
        });
      });
    }

    // ════ CURRENCY SWITCHER ════
    const curSwitcher = document.getElementById('curSwitcher');
    const curTrigger = document.getElementById('curTrigger');
    const curSymbol = document.getElementById('curSymbol');
    const curCode = document.getElementById('curCode');

    if (curSwitcher && curTrigger) {
      // Avval saqlangan valyutani yuklash
      const saved = localStorage.getItem('soluna-currency') || 'USD';
      applyCurrency(saved);

      // Toggle
      curTrigger.addEventListener('click', (e) => {
        e.stopPropagation();
        document.querySelectorAll('.lang-switcher.is-open').forEach(s => s.classList.remove('is-open'));
        curSwitcher.classList.toggle('is-open');
        curTrigger.setAttribute('aria-expanded', curSwitcher.classList.contains('is-open'));
      });

      // Valyuta tanlash
      curSwitcher.querySelectorAll('.cur-option').forEach(option => {
        option.addEventListener('click', (e) => {
          e.preventDefault();
          e.stopPropagation();

          const newCur = option.dataset.cur;
          const symbol = option.dataset.symbol;

          applyCurrency(newCur, symbol);
          localStorage.setItem('soluna-currency', newCur);

          // Boshqa komponentlarga xabar
          document.dispatchEvent(new CustomEvent('currency-changed', {
            detail: { code: newCur, symbol: symbol }
          }));

          curSwitcher.classList.remove('is-open');
        });
      });
    }

    function applyCurrency(code, symbol) {
      if (!curSymbol || !curCode) return;
      curCode.textContent = code;

      // Symbol topish (data atributdan yoki standartdan)
      if (!symbol) {
        const symbols = { USD: '$', EUR: '€', GBP: '£', RUB: '₽', UZS: "so'm",
                          KRW: '₩', JPY: '¥', TRY: '₺', KZT: '₸', CNY: '¥' };
        symbol = symbols[code] || code;
      }
      curSymbol.textContent = symbol;

      // Active option highlight
      curSwitcher.querySelectorAll('.cur-option').forEach(opt => {
        opt.classList.toggle('is-active', opt.dataset.cur === code);
      });
    }

    // ════ OUTSIDE CLICK ════
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.lang-switcher')) {
        langSwitcher?.classList.remove('is-open');
      }
      if (!e.target.closest('.cur-switcher')) {
        curSwitcher?.classList.remove('is-open');
      }
    });

    // ════ ESC ════
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        langSwitcher?.classList.remove('is-open');
        curSwitcher?.classList.remove('is-open');
      }
    });

    // ════ SCROLL RESTORE (til o'zgargandan keyin) ════
    const savedScroll = sessionStorage.getItem('soluna-scroll');
    if (savedScroll) {
      window.scrollTo({ top: parseInt(savedScroll, 10), behavior: 'instant' });
      sessionStorage.removeItem('soluna-scroll');
    }
  });

  /**
   * URL'da til prefiksini almashtirish
   * /ru/tours/ → /uz/tours/
   */
  function buildLangUrl(newLang) {
    const path = window.location.pathname;
    const search = window.location.search;
    const hash = window.location.hash;
    const langPattern = /^\/([a-z]{2}(?:-[a-z]{2,4})?)(\/|$)/i;
    const match = path.match(langPattern);
    const newPath = match
      ? path.replace(langPattern, `/${newLang}$2`)
      : `/${newLang}${path}`;
    return newPath + search + hash;
  }

})();

/* ════════════════════════════════════════════════════════════
   WISHLIST — tour card heart buttons (global, delegated)
   ════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  function getCookie(name) {
    var v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return v ? v.pop() : '';
  }

  function showToast(msg, type) {
    var t = document.createElement('div');
    t.textContent = msg;
    t.setAttribute('role', 'status');
    t.style.cssText =
      'position:fixed;left:50%;bottom:28px;transform:translateX(-50%) translateY(10px);' +
      'z-index:10000;padding:12px 20px;border-radius:12px;font-family:inherit;font-weight:600;' +
      'font-size:.9rem;letter-spacing:-.01em;box-shadow:0 12px 40px rgba(0,0,0,.25);opacity:0;' +
      'transition:opacity .25s ease, transform .25s cubic-bezier(0.22,1,0.36,1);pointer-events:none;' +
      (type === 'error'
        ? 'background:#E24B4A;color:#fff;'
        : 'background:#c9a84c;color:#1C1C1E;');
    document.body.appendChild(t);
    requestAnimationFrame(function () {
      t.style.opacity = '1';
      t.style.transform = 'translateX(-50%) translateY(0)';
    });
    setTimeout(function () {
      t.style.opacity = '0';
      t.style.transform = 'translateX(-50%) translateY(10px)';
      setTimeout(function () { t.remove(); }, 280);
    }, 2200);
  }

  // Event delegation — works for any current/future .tour-card-fav-btn
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.tour-card-fav-btn');
    if (!btn) return;
    e.preventDefault();
    e.stopPropagation();

    var url = btn.dataset.wishlistUrl;
    if (!url) return;
    if (btn.dataset.busy === '1') return;
    btn.dataset.busy = '1';

    fetch(url, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCookie('csrftoken'), 'X-Requested-With': 'XMLHttpRequest' },
    }).then(function (r) {
      if (r.status === 401) {
        var login = window.SOLUNA_LOGIN_URL || '/accounts/login/';
        location.href = login + '?next=' + encodeURIComponent(location.pathname);
        return null;
      }
      return r.json();
    }).then(function (data) {
      btn.dataset.busy = '';
      if (!data) return;
      var icon = btn.querySelector('i');
      if (data.status === 'added') {
        btn.classList.add('is-liked');
        if (icon) icon.className = 'ti ti-heart-filled';
        showToast(btn.dataset.addedText || 'Added to wishlist');
      } else if (data.status === 'removed') {
        btn.classList.remove('is-liked');
        if (icon) icon.className = 'ti ti-heart';
        showToast(btn.dataset.removedText || 'Removed from wishlist');
      }
    }).catch(function () {
      btn.dataset.busy = '';
      showToast(btn.dataset.errorText || 'Error. Try again.', 'error');
    });
  });

  window.SoLunaToast = showToast;
})();