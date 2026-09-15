/* ============================================================
   GENEVA MOTOR HAUS — srp-v2.js — the inventory results page
   ============================================================
   The page is complete without this file: all 23 cars are in the
   markup in the order the live site lists them, every card links to its
   car, and the facet panels still open natively. Everything here is a
   convenience on top of that.

   ONE SOURCE OF STATE. The checkboxes are the state. The marque pills,
   the facet counts on the triggers, the chips and the phone's sheet are
   all views of them, so no two controls can ever disagree. The keyword
   and the sort live in their own inputs.

   What CMC's SRP promised and did not do, this does: the count updates
   (and is announced), sort sorts, the keyword filters, an empty result
   says so and offers the way back, and a phone gets a sheet.

   The state is written to the address (?make=Porsche&sort=price-asc), so
   a link from the homepage can arrive filtered and a reload keeps it.
   ============================================================ */
(function () {
  'use strict';

  var tools = document.getElementById('srp-tools');
  var grid = document.getElementById('srp-grid');
  if (!tools || !grid) return;

  var cards = [].slice.call(grid.querySelectorAll('.srp-card'));
  var boxes = [].slice.call(tools.querySelectorAll('.srp-opt input[type="checkbox"]'));
  var facets = [].slice.call(tools.querySelectorAll('.srp-facet'));
  var makePills = [].slice.call(document.querySelectorAll('.srp-make'));
  var q = document.getElementById('srp-q');
  var searchForm = q ? q.form : null;
  var sort = document.getElementById('srp-sort');
  var counts = [].slice.call(document.querySelectorAll('[data-srp-count]'));
  var chipsWrap = document.getElementById('srp-chips');
  var chipsRow = chipsWrap ? chipsWrap.querySelector('.srp-chips__row') : null;
  var clearAllBtn = chipsWrap ? chipsWrap.querySelector('.srp-chips__clear') : null;
  var empty = document.getElementById('srp-empty');
  var openBtn = tools.querySelector('.srp-filters-open');
  var openN = tools.querySelector('.srp-filters-open__n');
  var sheet = document.getElementById('srp-facets');
  var RANGES = ['year', 'price', 'miles'];

  var data = cards.map(function (c) {
    return {
      el: c,
      make: c.getAttribute('data-make'),
      year: Number(c.getAttribute('data-year')),
      price: Number(c.getAttribute('data-price')),
      miles: Number(c.getAttribute('data-miles')),
      body: c.getAttribute('data-body') || '',
      order: Number(c.getAttribute('data-order')),
      text: c.getAttribute('data-text') || ''
    };
  });

  function checked(name) {
    return boxes.filter(function (b) { return b.name === name && b.checked; });
  }
  function range(value) {
    var p = value.split('-');
    return [Number(p[0]), Number(p[1])];
  }
  function labelOf(box) {
    var n = box.closest('.srp-opt').querySelector('.srp-opt__name');
    return n ? n.textContent.trim() : box.value;
  }

  /* ---- filtering: OR inside a facet, AND across facets ---- */
  function apply() {
    var makes = checked('make').map(function (b) { return b.value; });
    var bodies = checked('body').map(function (b) { return b.value; });
    var ranges = {};
    RANGES.forEach(function (n) { ranges[n] = checked(n).map(function (b) { return range(b.value); }); });
    var terms = (q ? q.value : '').toLowerCase().trim().split(/\s+/).filter(Boolean);

    var shown = 0;
    data.forEach(function (d) {
      var ok = (!makes.length || makes.indexOf(d.make) > -1) && (!bodies.length || bodies.indexOf(d.body) > -1);
      RANGES.forEach(function (n) {
        if (ok && ranges[n].length) {
          ok = ranges[n].some(function (r) { return d[n] >= r[0] && d[n] <= r[1]; });
        }
      });
      if (ok && terms.length) {
        ok = terms.every(function (t) { return d.text.indexOf(t) > -1; });
      }
      d.el.hidden = !ok;
      if (ok) shown++;
    });

    counts.forEach(function (el) { el.textContent = String(shown); });
    if (empty) empty.hidden = shown > 0;
    renderChips();
    syncTriggers();
    syncMakes();
    writeUrl();
  }

  /* ---- sorting: the DOM order is the order read, by eye and by ear ---- */
  var SORTS = {
    'listed': function (a, b) { return a.order - b.order; },
    'price-asc': function (a, b) { return a.price - b.price || a.order - b.order; },
    'price-desc': function (a, b) { return b.price - a.price || a.order - b.order; },
    'year-desc': function (a, b) { return b.year - a.year || a.order - b.order; },
    'year-asc': function (a, b) { return a.year - b.year || a.order - b.order; },
    'miles-asc': function (a, b) { return a.miles - b.miles || a.order - b.order; }
  };
  function reorder() {
    var fn = SORTS[sort && sort.value] || SORTS.listed;
    data.slice().sort(fn).forEach(function (d) { grid.appendChild(d.el); });
    writeUrl();
  }

  /* ---- the chosen filters, read back ---- */
  function chip(text, onRemove) {
    var li = document.createElement('li');
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'srp-chip';
    btn.setAttribute('aria-label', 'Remove filter ' + text);
    var span = document.createElement('span');
    span.textContent = text;
    btn.appendChild(span);
    btn.insertAdjacentHTML('beforeend',
      '<svg class="srp-chip__x" width="9" height="9" viewBox="0 0 9 9" fill="none" aria-hidden="true">' +
      '<path d="m1 1 7 7M8 1 1 8" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>');
    btn.addEventListener('click', function () {
      onRemove();
      // the chip is gone: land on the next one, or on the search field
      var next = chipsRow && chipsRow.querySelector('.srp-chip');
      (next || q || document.body).focus();
    });
    li.appendChild(btn);
    return li;
  }
  function renderChips() {
    if (!chipsWrap || !chipsRow) return;
    chipsRow.textContent = '';
    boxes.filter(function (b) { return b.checked; }).forEach(function (b) {
      chipsRow.appendChild(chip(labelOf(b), function () { b.checked = false; apply(); }));
    });
    var term = q ? q.value.trim() : '';
    if (term) {
      chipsRow.appendChild(chip('“' + term + '”', function () { q.value = ''; apply(); }));
    }
    chipsWrap.hidden = !chipsRow.children.length;
  }

  /* ---- the counts on the triggers and on the phone's Filters button ---- */
  function syncTriggers() {
    var total = 0;
    facets.forEach(function (f) {
      var n = f.querySelectorAll('input:checked').length;
      total += n;
      var badge = f.querySelector('.srp-facet__n');
      if (badge) { badge.textContent = String(n); badge.hidden = n === 0; }
    });
    if (openN) { openN.textContent = String(total); openN.hidden = total === 0; }
  }

  /* ---- the marque pills are the Make facet said shorter ---- */
  function boxForMake(name) {
    return boxes.filter(function (b) { return b.name === 'make' && b.value === name; })[0] || null;
  }
  function syncMakes() {
    makePills.forEach(function (p) {
      var b = boxForMake(p.getAttribute('data-make'));
      p.setAttribute('aria-pressed', String(!!(b && b.checked)));
    });
  }
  makePills.forEach(function (p) {
    p.addEventListener('click', function () {
      var b = boxForMake(p.getAttribute('data-make'));
      if (!b) return;
      b.checked = !b.checked;
      apply();
    });
  });

  /* ---- the address ---- */
  function writeUrl() {
    if (!window.history || !history.replaceState) return;
    var params = new URLSearchParams();
    ['make', 'body'].concat(RANGES).forEach(function (n) {
      var v = checked(n).map(function (b) { return b.value; });
      if (v.length) params.set(n, v.join(','));
    });
    if (q && q.value.trim()) params.set('q', q.value.trim());
    if (sort && sort.value !== 'listed') params.set('sort', sort.value);
    var s = params.toString();
    history.replaceState(null, '', location.pathname + (s ? '?' + s : '') + location.hash);
  }
  function readUrl() {
    var params = new URLSearchParams(location.search);
    ['make', 'body'].concat(RANGES).forEach(function (n) {
      var want = (params.get(n) || '').split(',').filter(Boolean);
      boxes.forEach(function (b) { if (b.name === n && want.indexOf(b.value) > -1) b.checked = true; });
    });
    if (q && params.get('q')) q.value = params.get('q');
    if (sort && params.get('sort') && SORTS[params.get('sort')]) sort.value = params.get('sort');
  }

  /* ---- clearing ---- */
  function clearAll() {
    boxes.forEach(function (b) { b.checked = false; });
    if (q) q.value = '';
    apply();
  }
  if (clearAllBtn) clearAllBtn.addEventListener('click', function () { clearAll(); if (q) q.focus(); });
  if (empty) {
    var emptyBtn = empty.querySelector('.srp-empty__clear');
    if (emptyBtn) emptyBtn.addEventListener('click', function () { clearAll(); if (q) q.focus(); });
  }
  facets.forEach(function (f) {
    var c = f.querySelector('.srp-facet__clear');
    if (!c) return;
    c.addEventListener('click', function () {
      [].slice.call(f.querySelectorAll('input:checked')).forEach(function (b) { b.checked = false; });
      apply();
    });
  });

  /* ---- inputs ---- */
  boxes.forEach(function (b) { b.addEventListener('change', apply); });
  var typing = 0;
  if (q) {
    q.addEventListener('input', function () {
      clearTimeout(typing);
      typing = setTimeout(apply, 140);
    });
  }
  if (searchForm) {
    searchForm.addEventListener('submit', function (e) { e.preventDefault(); apply(); });
  }
  if (sort) sort.addEventListener('change', reorder);

  /* ---- one panel at a time; outside closes; Escape closes ---- */
  function inSheet() { return tools.classList.contains('is-sheet'); }
  facets.forEach(function (f) {
    f.addEventListener('toggle', function () {
      if (!f.open || inSheet()) return;
      facets.forEach(function (o) { if (o !== f) o.open = false; });
    });
  });
  document.addEventListener('click', function (e) {
    if (inSheet()) return;
    facets.forEach(function (f) { if (f.open && !f.contains(e.target)) f.open = false; });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (inSheet()) { closeSheet(); return; }
    var open = facets.filter(function (f) { return f.open; })[0];
    if (!open) return;
    open.open = false;
    var t = open.querySelector('.srp-facet__trigger');
    if (t) t.focus();
  });

  /* ---- the phone's sheet: the same facets, all open, over the page ---- */
  function openSheet() {
    tools.classList.add('is-sheet');
    document.documentElement.classList.add('srp-lock');
    if (openBtn) openBtn.setAttribute('aria-expanded', 'true');
    facets.forEach(function (f) { f.open = true; });
    var close = sheet && sheet.querySelector('.srp-sheet__close');
    if (close) close.focus();
  }
  function closeSheet() {
    tools.classList.remove('is-sheet');
    document.documentElement.classList.remove('srp-lock');
    if (openBtn) { openBtn.setAttribute('aria-expanded', 'false'); openBtn.focus(); }
    facets.forEach(function (f) { f.open = false; });
  }
  if (openBtn) openBtn.addEventListener('click', openSheet);
  if (sheet) {
    var closeBtn = sheet.querySelector('.srp-sheet__close');
    var showBtn = sheet.querySelector('.srp-sheet__show');
    var resetBtn = sheet.querySelector('.srp-sheet__reset');
    if (closeBtn) closeBtn.addEventListener('click', closeSheet);
    if (showBtn) showBtn.addEventListener('click', closeSheet);
    if (resetBtn) resetBtn.addEventListener('click', function () {
      boxes.forEach(function (b) { b.checked = false; });
      apply();
    });
  }
  // a sheet left open while the window grows past the phone layout would
  // strand the page locked
  var wide = window.matchMedia('(min-width: 901px)');
  var onWide = function () { if (wide.matches && inSheet()) closeSheet(); };
  if (wide.addEventListener) wide.addEventListener('change', onWide); else if (wide.addListener) wide.addListener(onWide);

  readUrl();
  reorder();
  apply();
})();
