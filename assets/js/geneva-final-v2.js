/* Geneva Motor Haus — geneva-final-v2.js (index_finale_v2.html; clone of geneva-final.js)
   Loaded after main.js, which carries the menu, the condensed-header
   sentinel, the reveals, the map's reach, the sell pill. This file adds
   three things and the page is complete without any of them: the
   carousel scrolls natively, the hero type is simply there, the search
   glyph is a link. */

/* ============================================================
   THE HERO'S EXIT — a fallback for browsers without scroll timelines
   ============================================================
   geneva-final.css drives the exit with animation-timeline: view().
   Where that is unsupported the same numbers run off --gf-p, 0 at the
   top of the page and 1 when the hero's copy has gone — one passive
   scroll listener, one rAF, transform + opacity only. Reduced motion:
   nothing is armed and the type stays put. */
(function () {
  'use strict';

  var hero = document.querySelector('.hero');
  if (!hero) return;
  var calm = window.matchMedia('(prefers-reduced-motion: reduce)');
  var native = window.CSS && CSS.supports && CSS.supports('animation-timeline: view()');
  if (calm.matches || native) return;

  document.documentElement.classList.add('gf-scroll-fallback');
  var ticking = false;
  function paint() {
    ticking = false;
    var reach = hero.offsetHeight * 0.58;
    var p = Math.min(1, Math.max(0, window.scrollY / reach));
    hero.style.setProperty('--gf-p', p.toFixed(3));
  }
  window.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; requestAnimationFrame(paint); }
  }, { passive: true });
  paint();
})();

/* ============================================================
   THE CATALOGUE — one photograph, a plate, an index (Figma 46:829)
   ============================================================
   Replaces the carousel of cards (finale 3). Ported from index2's
   geneva.js unchanged in behaviour: the index drives the frame. Click
   (or Enter) on a line CHOOSES a car; hover or focus PREVIEWS it and
   leaving the list restores the choice, so a pointer crossing the
   column never leaves the section on a car nobody picked. The arrows
   step through the index in the order it is written, and wrap — eight
   cars are a ring, not a document. Crossfade only; the CSS owns the
   timing. */
(function () {
  'use strict';

  var cat = document.querySelector('.gmh-cat');
  if (!cat) return;

  var photos = [].slice.call(cat.querySelectorAll('.gmh-cat__photo'));
  var plates = [].slice.call(cat.querySelectorAll('.gmh-cat__plate'));
  var rows   = [].slice.call(cat.querySelectorAll('.gmh-cat__row'));
  var at     = cat.querySelector('.gmh-cat__at');
  if (photos.length < 2 || !rows.length) return;

  var frames = rows.map(function (r) { return Number(r.getAttribute('data-frame')); });
  var seat = 0;

  function pad(n) { return (n < 10 ? '0' : '') + n; }

  function show(i) {
    var s = frames.indexOf(i);
    if (s !== -1) seat = s;
    photos.forEach(function (p) {
      p.classList.toggle('is-active', p.getAttribute('data-frame') === String(i));
    });
    plates.forEach(function (p) {
      p.classList.toggle('is-active', p.getAttribute('data-frame') === String(i));
    });
    rows.forEach(function (r) {
      r.setAttribute('aria-pressed', String(r.getAttribute('data-frame') === String(i)));
    });
    if (at) at.textContent = pad(seat + 1);
  }

  var locked = frames[0];
  function select(i) { locked = i; show(i); }
  function restore() { show(locked); }

  rows.forEach(function (row) {
    var i = Number(row.getAttribute('data-frame'));
    row.addEventListener('click', function () { select(i); });
    row.addEventListener('mouseenter', function () { show(i); });
    row.addEventListener('focus', function () { show(i); });
  });

  var list = cat.querySelector('.gmh-cat__index');
  if (list) {
    list.addEventListener('mouseleave', restore);
    list.addEventListener('focusout', function (e) {
      if (!list.contains(e.relatedTarget)) restore();
    });
  }

  [].slice.call(cat.querySelectorAll('.gmh-cat__arrow')).forEach(function (btn) {
    var step = Number(btn.getAttribute('data-step')) || 1;
    btn.addEventListener('click', function () {
      var next = (seat + step + frames.length) % frames.length;
      select(frames[next]);
    });
  });

  // The photographs load lazily; the first one is eager. Warm the next
  // in the ring so the first arrow press crossfades to a picture, not
  // to a fetch.
  var second = photos[1];
  if (second && second.loading === 'lazy') second.loading = 'eager';
})();

/* ============================================================
   SEARCH ON A NARROW BAR — the glyph opens the menu on its field
   ============================================================ */
(function () {
  'use strict';

  var glyph  = document.querySelector('[data-opens-search]');
  var toggle = document.querySelector('.menu-toggle');
  var menu   = document.getElementById('site-menu');
  if (!glyph || !toggle || !menu) return;

  glyph.addEventListener('click', function (e) {
    e.preventDefault();
    if (toggle.getAttribute('aria-expanded') !== 'true') toggle.click();
    // main.js moves focus to the first group heading on a timeout; the
    // field has to be asked for after that
    var field = menu.querySelector('input[type="search"]');
    if (field) setTimeout(function () { field.focus(); }, 0);
  });
})();

/* ============================================================
   SHIPPING, PINNED WITH ITS FOOT ON THE WINDOW'S FOOT
   ============================================================
   geneva-final.css pins the chapter at min(0, 100svh - its height), so
   a chapter taller than the window stops with its last line in view
   rather than its first. The height is read here, on load and on
   resize, and written as --ship-h. */
(function () {
  'use strict';
  var ship = document.querySelector('.gmh-ship');
  if (!ship) return;
  function measure() { ship.style.setProperty('--ship-h', ship.offsetHeight + 'px'); }
  if ('ResizeObserver' in window) new ResizeObserver(measure).observe(ship);
  window.addEventListener('resize', measure);
  if (document.readyState === 'complete') measure(); else window.addEventListener('load', measure);
  measure();
})();
