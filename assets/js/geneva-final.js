/* Geneva Motor Haus — geneva-final.js (index_finale.html)
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
   THE CAROUSEL — eight cards, 3 · 2 · 1 in view
   ============================================================
   The track is a native scroller with snap points: touch, trackpad and
   keyboard focus already move it. The arrows page it by the number of
   cards in view; they disable at the ends rather than wrap — eight
   cars are a row, not a ring, and a control that does nothing says so. */
(function () {
  'use strict';

  var wrap = document.querySelector('.gf-cars__wrap');
  if (!wrap) return;
  var track = wrap.querySelector('.gf-cars__track');
  var cards = track ? [].slice.call(track.children) : [];
  var prev = wrap.querySelector('.gf-cars__arrow--prev');
  var next = wrap.querySelector('.gf-cars__arrow--next');
  if (!track || cards.length < 2 || !prev || !next) return;

  function step() {
    // one card plus the gap, read off the layout so the CSS owns the numbers
    return cards[1].offsetLeft - cards[0].offsetLeft;
  }
  function perView() {
    return Math.max(1, Math.round(track.clientWidth / step()));
  }

  function settle() {
    var max = track.scrollWidth - track.clientWidth;
    var atStart = track.scrollLeft <= 2;
    var atEnd = track.scrollLeft >= max - 2;
    prev.setAttribute('aria-disabled', String(atStart));
    next.setAttribute('aria-disabled', String(atEnd));
    prev.tabIndex = atStart ? -1 : 0;
    next.tabIndex = atEnd ? -1 : 0;
  }

  /* THE MOVE. One authored curve rather than the browser's own smooth
     scroll, so the track travels the same way in every browser: 520ms,
     decelerating (ease-out cubic), one page of cards per press, always
     landing on a snap point. A press mid-travel retargets from where
     the track is. Reduced motion: the track jumps. */
  var calm = window.matchMedia('(prefers-reduced-motion: reduce)');
  var raf = 0;
  function glide(target) {
    cancelAnimationFrame(raf);
    var from = track.scrollLeft, delta = target - from;
    if (calm.matches || Math.abs(delta) < 1) { track.scrollLeft = target; return; }
    var t0 = performance.now(), dur = 520;
    // snap is released for the glide so the browser cannot pull the
    // track to a card mid-travel; the target is itself a snap point
    track.classList.add('is-gliding');
    function frame(now) {
      var t = Math.min(1, (now - t0) / dur);
      var e = 1 - Math.pow(1 - t, 3);
      track.scrollLeft = from + delta * e;
      if (t < 1) raf = requestAnimationFrame(frame);
      else track.classList.remove('is-gliding');
    }
    raf = requestAnimationFrame(frame);
  }

  function page(dir) {
    if ((dir < 0 && prev.getAttribute('aria-disabled') === 'true') ||
        (dir > 0 && next.getAttribute('aria-disabled') === 'true')) return;
    var s = step(), per = perView();
    var max = track.scrollWidth - track.clientWidth;
    var here = Math.round(track.scrollLeft / s) * s;
    var target = Math.min(max, Math.max(0, here + dir * s * per));
    glide(target);
  }

  prev.addEventListener('click', function () { page(-1); });
  next.addEventListener('click', function () { page(1); });

  // Left / Right on the track itself, for a keyboard that has tabbed in
  track.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowRight') { e.preventDefault(); page(1); }
    if (e.key === 'ArrowLeft')  { e.preventDefault(); page(-1); }
  });

  var ticking = false;
  track.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; requestAnimationFrame(function () { ticking = false; settle(); }); }
  }, { passive: true });
  window.addEventListener('resize', settle);
  if (document.readyState === 'complete') settle(); else window.addEventListener('load', settle);
  settle();
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
