/* ============================================================
   GENEVA MOTOR HAUS — finance-v2.js — the financing application
   ============================================================
   Without this file the form is the whole AAN application laid open: every
   field reachable, nothing hidden by a condition. With it:

   · PREVIOUS RESIDENCE / EMPLOYMENT open when the time at the address or at
     the job is under two years, and close again when it isn't (AAN's form
     opens them and never closes them). A closed part is disabled, so its
     required fields cannot block the send.
   · THE CO-APPLICANT switch opens their details, residence and employment;
     "same address as the applicant" removes their address fields.
   · THE VEHICLE list follows the make, the make follows the vehicle, and a
     VDP arrives here with ?car=<slug> already chosen.
   · THE RAIL lights the step in view.
   · SEND checks the form, then answers in place — a static preview cannot
     deliver an application, and says so.

   Shared by sell.html, whose form has none of the conditional parts: every
   piece above is skipped when its elements are absent.
   ============================================================ */
(function () {
  'use strict';

  var form = document.getElementById('fin-form');
  if (!form) return;
  var calm = window.matchMedia('(prefers-reduced-motion: reduce)');

  function setPart(el, on) {
    if (!el) return;
    el.hidden = !on;
    [].slice.call(el.querySelectorAll('input, select, textarea')).forEach(function (i) { i.disabled = !on; });
  }
  function under2(select) {
    var v = select.value;
    return v !== '' && parseInt(v, 10) < 2;
  }

  /* ---- previous residence / employment, for the applicant and co-applicant ---- */
  var conditionals = [].slice.call(form.querySelectorAll('select[data-under2]')).filter(function (s) { return s.getAttribute('data-under2'); });
  function syncUnder2(s) {
    var part = document.getElementById(s.getAttribute('data-under2'));
    var co = s.name.indexOf('co_') === 0;
    var coOn = co ? !!(coSwitch && coSwitch.checked) : true;
    setPart(part, coOn && !s.disabled && under2(s));
  }

  /* ---- the co-applicant ---- */
  var coSwitch = document.getElementById('f-co_applicant_active');
  var coBox = document.getElementById('fin-co');
  var sameAddr = document.getElementById('f-co_same_address');
  var coResFields = document.getElementById('co-res-fields');
  function syncCo() {
    if (!coSwitch) { conditionals.forEach(syncUnder2); markRail(); return; }   // a form with no co-applicant (sell.html)
    var on = coSwitch.checked;
    setPart(coBox, on);
    if (on) {
      setPart(coResFields, !sameAddr.checked);
      setPart(document.getElementById('co_prev-res'), false);
      setPart(document.getElementById('co_prev-emp'), false);
    }
    conditionals.forEach(syncUnder2);
    // co_same_address hides the residence, and with it its previous-residence part
    if (on && sameAddr.checked) setPart(document.getElementById('co_prev-res'), false);
    markRail();
  }

  conditionals.forEach(function (s) {
    s.addEventListener('change', function () {
      syncUnder2(s);
      if (sameAddr && sameAddr.checked && s.name === 'co_addr_y') setPart(document.getElementById('co_prev-res'), false);
    });
  });
  if (coSwitch) coSwitch.addEventListener('change', syncCo);
  if (sameAddr) sameAddr.addEventListener('change', syncCo);

  /* ---- vehicle of interest ---- */
  var make = form.elements.make;
  var car = form.elements.stock;
  var carOptions = car ? [].slice.call(car.options).slice(1) : [];
  function filterCars() {
    var m = make.value;
    carOptions.forEach(function (o) { o.hidden = !!m && o.getAttribute('data-make') !== m; });
    var sel = car.options[car.selectedIndex];
    if (sel && sel.value && sel.hidden) car.value = '';
  }
  if (make && car) {
    make.addEventListener('change', filterCars);
    car.addEventListener('change', function () {
      var o = car.options[car.selectedIndex];
      if (o && o.value) { make.value = o.getAttribute('data-make'); filterCars(); }
    });
    var wanted = new URLSearchParams(location.search).get('car');
    if (wanted && carOptions.some(function (o) { return o.value === wanted; })) {
      car.value = wanted;
      make.value = car.options[car.selectedIndex].getAttribute('data-make');
      filterCars();
    }
  }

  /* ---- the summary: what is answered, what each step still needs ---- */
  var links = [].slice.call(document.querySelectorAll('.fin-step'));
  var sections = links.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); });
  var progress = document.querySelector('[data-progress]');
  var CHECK = '<svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true"><path d="M2.5 7.3 5.6 10.2 11.5 3.8" stroke="currentColor" stroke-width="1.6"/></svg>';
  function filled(i) { return i.type === 'checkbox' ? i.checked : i.type === 'file' ? i.files.length > 0 : i.value.trim() !== ''; }
  function answered(i) { return filled(i) && i.checkValidity(); }
  function markRail() {
    var done = 0, total = 0;
    links.forEach(function (a, k) {
      var s = sections[k], out = a.querySelector('[data-status]');
      if (!s || !out) return;
      var fields = [].slice.call(s.querySelectorAll('input, select, textarea')).filter(function (i) { return !i.disabled; });
      var req = fields.filter(function (i) { return i.required; });
      var left = req.filter(function (i) { return !answered(i); }).length;
      total += req.length;
      done += req.length - left;
      // a step with required fields counts only those, and says so ("0 / 3 required");
      // a step with none says Optional, and a photograph step counts its files
      var file = fields.filter(function (i) { return i.type === 'file'; })[0];
      var attached = file ? file.files.length : 0;
      var complete = req.length ? !left : attached > 0;
      var html = req.length ? (left ? '' : CHECK) + (req.length - left) + ' / ' + req.length + ' required'
        : attached ? CHECK + attached + ' attached' : 'Optional';
      if (out.innerHTML !== html) out.innerHTML = html;
      out.classList.toggle('is-done', complete);
    });
    if (!progress) return;
    progress.hidden = false;
    progress.querySelector('[data-done]').textContent = done;
    progress.querySelector('[data-total]').textContent = total;
    progress.querySelector('[data-bar]').style.transform = 'scaleX(' + (total ? done / total : 0) + ')';
  }
  // target listeners (the conditional parts) run first, so the count sees the new shape
  form.addEventListener('input', markRail);
  form.addEventListener('change', markRail);
  if ('IntersectionObserver' in window && links.length) {
    var inView = new Map();
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { inView.set(en.target, en.isIntersecting ? en.intersectionRatio : 0); });
      var best = null, bestTop = Infinity;
      sections.forEach(function (s) {
        if (!s || !inView.get(s)) return;
        var top = Math.abs(s.getBoundingClientRect().top - 120);
        if (top < bestTop) { bestTop = top; best = s; }
      });
      if (best) links.forEach(function (a, k) { if (sections[k] === best) a.setAttribute('aria-current', 'step'); else a.removeAttribute('aria-current'); });
    }, { rootMargin: '-20% 0px -55% 0px', threshold: [0, 0.01, 0.5, 1] });
    sections.forEach(function (s) { if (s) io.observe(s); });
  }
  links.forEach(function (a, k) {
    a.addEventListener('click', function (e) {
      var s = sections[k];
      if (!s) return;
      e.preventDefault();
      s.scrollIntoView({ block: 'start', behavior: calm.matches ? 'auto' : 'smooth' });
      var first = s.querySelector('input:not([disabled]), select:not([disabled]), textarea:not([disabled])');
      if (first) first.focus({ preventScroll: true });
    });
  });

  /* ---- send and clear ---- */
  var sent = document.getElementById('fin-sent');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    form.classList.add('was-sent');
    if (!form.checkValidity()) {
      var bad = form.querySelector(':invalid:not(fieldset)');
      if (bad) {
        bad.scrollIntoView({ block: 'center', behavior: calm.matches ? 'auto' : 'smooth' });
        setTimeout(function () { bad.focus({ preventScroll: true }); bad.reportValidity(); }, calm.matches ? 0 : 350);
      }
      return;
    }
    var first = (form.elements.fname && form.elements.fname.value.trim()) || '';
    var slot = sent.querySelector('[data-sent-name]');
    if (slot) slot.textContent = first ? ', ' + first : '';
    form.hidden = true;
    sent.hidden = false;
    form.closest('.fin-apply__body').classList.add('is-sent');
    sent.scrollIntoView({ block: 'center', behavior: calm.matches ? 'auto' : 'smooth' });
    sent.focus({ preventScroll: true });
  });

  var clear = form.querySelector('.fin-clear');
  if (clear) {
    clear.addEventListener('click', function () {
      if (!window.confirm('Clear everything you have entered?')) return;
      form.reset();
      form.classList.remove('was-sent');
      filterCars && make && car && filterCars();
      syncCo();
      var f = form.querySelector('input:not([type=hidden])');
      if (f) f.focus();
    });
  }

  // the starting state: every conditional part closed until its answer asks for it
  setPart(document.getElementById('prev-res'), false);
  setPart(document.getElementById('prev-emp'), false);
  syncCo();
})();
