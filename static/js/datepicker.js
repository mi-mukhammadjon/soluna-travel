/* ════════════════════════════════════════════════════════════
   SoLuna — Themed Date Picker (vanilla JS, no deps)
   Har bir <input type="date"> ni gold-themed kalendarga aylantiradi.
   Asl input qiymati/nomi saqlanadi → forma submit o'zgarmasdan ishlaydi.
   Qiymat formati: input.value = YYYY-MM-DD, ko'rinishi = DD-MM-YYYY.
   ════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var DOW = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'];

  function pad(n) { return n < 10 ? '0' + n : '' + n; }
  function toISO(d) { return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
  function fmt(d) { return pad(d.getDate()) + '-' + pad(d.getMonth() + 1) + '-' + d.getFullYear(); }
  function fromISO(s) {
    if (!s) return null;
    var p = s.split('-');
    if (p.length !== 3) return null;
    var y = +p[0], m = +p[1], d = +p[2];
    if (!y || !m || !d) return null;
    return new Date(y, m - 1, d);
  }
  function sameDay(a, b) {
    return a && b && a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate();
  }
  function stripTime(d) { return new Date(d.getFullYear(), d.getMonth(), d.getDate()); }

  function DatePicker(input) {
    this.input = input;
    this.required = input.required || input.hasAttribute('required');
    this.min = fromISO(input.getAttribute('min'));
    this.placeholder = input.getAttribute('data-placeholder') || 'dd-mm-yyyy';
    this.selected = fromISO(input.value);
    var base = this.selected || (this.min && this.min > new Date() ? this.min : new Date());
    this.view = new Date(base.getFullYear(), base.getMonth(), 1);
    this.pop = null;
    this.open = false;
    this.build();
  }

  DatePicker.prototype.build = function () {
    var input = this.input;
    var origClass = input.className;
    input.type = 'hidden';

    var wrap = document.createElement('span');
    wrap.className = 'sl-dp';
    input.parentNode.insertBefore(wrap, input);
    wrap.appendChild(input);
    this.wrap = wrap;

    var trigger = document.createElement('button');
    trigger.type = 'button';
    trigger.className = (origClass ? origClass + ' ' : '') + 'sl-dp-field';
    trigger.setAttribute('aria-haspopup', 'dialog');
    trigger.innerHTML = '<span class="sl-dp-val"></span><i class="ti ti-calendar sl-dp-ic"></i>';
    wrap.appendChild(trigger);
    this.trigger = trigger;
    this.valEl = trigger.querySelector('.sl-dp-val');

    this.syncTrigger();

    var self = this;
    trigger.addEventListener('click', function (e) { e.preventDefault(); self.toggle(); });

    // Required validatsiya — input hidden bo'lgani uchun native required ishlamaydi
    if (this.required && input.form) {
      input.form.addEventListener('submit', function (e) {
        if (!input.value) {
          e.preventDefault();
          e.stopImmediatePropagation();  // boshqa submit handlerlar (masalan tugma "Processing") ishlamasin
          trigger.classList.add('is-invalid');
          trigger.focus();
          self.openPop();
        }
      }, true);  // capture — eng birinchi ishlaydi
    }
  };

  DatePicker.prototype.syncTrigger = function () {
    if (this.selected) {
      this.valEl.textContent = fmt(this.selected);
      this.trigger.classList.remove('is-placeholder');
    } else {
      this.valEl.textContent = this.placeholder;
      this.trigger.classList.add('is-placeholder');
    }
  };

  DatePicker.prototype.toggle = function () { this.open ? this.closePop() : this.openPop(); };

  DatePicker.prototype.buildPop = function () {
    var pop = document.createElement('div');
    pop.className = 'sl-dp-pop';
    pop.setAttribute('role', 'dialog');
    pop.innerHTML =
      '<div class="sl-dp-card">' +
        '<div class="sl-dp-head">' +
          '<button type="button" class="sl-dp-nav" data-nav="-1" aria-label="Prev"><i class="ti ti-chevron-left"></i></button>' +
          '<div class="sl-dp-title"></div>' +
          '<button type="button" class="sl-dp-nav" data-nav="1" aria-label="Next"><i class="ti ti-chevron-right"></i></button>' +
        '</div>' +
        '<div class="sl-dp-grid sl-dp-dow">' + DOW.map(function (d) { return '<span>' + d + '</span>'; }).join('') + '</div>' +
        '<div class="sl-dp-grid sl-dp-days"></div>' +
        '<div class="sl-dp-foot">' +
          '<button type="button" class="sl-dp-today-btn">Today</button>' +
          '<button type="button" class="sl-dp-clear-btn">Clear</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(pop);
    this.pop = pop;
    this.titleEl = pop.querySelector('.sl-dp-title');
    this.daysEl = pop.querySelector('.sl-dp-days');

    var self = this;
    pop.querySelectorAll('.sl-dp-nav').forEach(function (btn) {
      btn.addEventListener('click', function () {
        self.view.setMonth(self.view.getMonth() + parseInt(btn.dataset.nav, 10));
        self.render();
      });
    });
    pop.querySelector('.sl-dp-today-btn').addEventListener('click', function () {
      var t = stripTime(new Date());
      if (self.min && t < stripTime(self.min)) t = stripTime(self.min);
      self.pick(t);
    });
    pop.querySelector('.sl-dp-clear-btn').addEventListener('click', function () {
      self.selected = null;
      self.input.value = '';
      self.input.dispatchEvent(new Event('input', { bubbles: true }));
      self.input.dispatchEvent(new Event('change', { bubbles: true }));
      self.syncTrigger();
      self.render();
      self.closePop();
    });

    // Tashqariga bosish / scroll / resize / Esc
    this._onDoc = function (e) { if (!pop.contains(e.target) && !self.wrap.contains(e.target)) self.closePop(); };
    this._onKey = function (e) { if (e.key === 'Escape') self.closePop(); };
    this._onWin = function () { if (self.open) self.position(); };
  };

  DatePicker.prototype.render = function () {
    this.titleEl.textContent = this.view.toLocaleString(undefined, { month: 'long' }) + ', ' + this.view.getFullYear();

    var year = this.view.getFullYear(), month = this.view.getMonth();
    var firstDow = new Date(year, month, 1).getDay();
    var daysInMonth = new Date(year, month + 1, 0).getDate();
    var today = stripTime(new Date());
    var minD = this.min ? stripTime(this.min) : null;

    var html = '';
    for (var i = 0; i < firstDow; i++) html += '<span class="sl-dp-empty"></span>';
    for (var d = 1; d <= daysInMonth; d++) {
      var cur = new Date(year, month, d);
      var cls = 'sl-dp-day';
      if (minD && cur < minD) cls += ' is-disabled';
      if (sameDay(cur, today)) cls += ' is-today';
      if (this.selected && sameDay(cur, this.selected)) cls += ' is-selected';
      html += '<button type="button" class="' + cls + '" data-day="' + d + '">' + d + '</button>';
    }
    this.daysEl.innerHTML = html;

    var self = this;
    this.daysEl.querySelectorAll('.sl-dp-day:not(.is-disabled)').forEach(function (btn) {
      btn.addEventListener('click', function () {
        self.pick(new Date(self.view.getFullYear(), self.view.getMonth(), parseInt(btn.dataset.day, 10)));
      });
    });
  };

  DatePicker.prototype.pick = function (date) {
    this.selected = date;
    this.view = new Date(date.getFullYear(), date.getMonth(), 1);
    this.input.value = toISO(date);
    this.input.dispatchEvent(new Event('input', { bubbles: true }));
    this.input.dispatchEvent(new Event('change', { bubbles: true }));
    this.trigger.classList.remove('is-invalid');
    this.syncTrigger();
    this.closePop();
  };

  DatePicker.prototype.position = function () {
    var r = this.trigger.getBoundingClientRect();
    var pop = this.pop;
    var w = pop.offsetWidth, h = pop.offsetHeight;
    var left = r.left;
    if (left + w > window.innerWidth - 8) left = window.innerWidth - w - 8;
    if (left < 8) left = 8;
    var top = r.bottom + 6;
    if (top + h > window.innerHeight - 8 && r.top - h - 6 > 8) top = r.top - h - 6;
    pop.style.left = Math.round(left) + 'px';
    pop.style.top = Math.round(top) + 'px';
  };

  DatePicker.prototype.openPop = function () {
    if (!this.pop) this.buildPop();
    if (this.open) return;
    this.render();
    this.pop.style.visibility = 'hidden';
    this.pop.classList.add('is-open');
    this.position();
    this.pop.style.visibility = '';
    this.open = true;
    this.wrap.classList.add('is-open');
    document.addEventListener('mousedown', this._onDoc);
    document.addEventListener('keydown', this._onKey);
    window.addEventListener('scroll', this._onWin, true);
    window.addEventListener('resize', this._onWin);
  };

  DatePicker.prototype.closePop = function () {
    if (!this.open || !this.pop) return;
    this.pop.classList.remove('is-open');
    this.open = false;
    this.wrap.classList.remove('is-open');
    document.removeEventListener('mousedown', this._onDoc);
    document.removeEventListener('keydown', this._onKey);
    window.removeEventListener('scroll', this._onWin, true);
    window.removeEventListener('resize', this._onWin);
  };

  function init() {
    var inputs = document.querySelectorAll('input[type="date"]:not([data-sl-dp])');
    inputs.forEach(function (input) {
      input.setAttribute('data-sl-dp', '1');
      try {
        new DatePicker(input);
      } catch (e) {
        // Xato bo'lsa native input'ni tiklaymiz (foydalanuvchi sana tanlay olsin)
        if (input.type === 'hidden') input.type = 'date';
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
