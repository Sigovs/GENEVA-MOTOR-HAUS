/* Geneva Motor Haus — geneva.js
   The page is complete without this file: every plate carries its
   own link, the index is a list, the photographs are in the markup.
   Everything here adds a convenience. main.js carries the rest
   (menu, condensed header, reveals, the map, the sell pill). */

/* ============================================================
   THE CATALOGUE — one photograph, a plate, an index
   ============================================================
   The index drives the frame. Click (or Enter) on a line CHOOSES a car;
   hover or focus PREVIEWS it and leaving the list restores the choice,
   so a pointer crossing the column never leaves the section on a car
   nobody picked. The arrows step through the index in the order it is
   written, and wrap — eight cars are a ring, not a document.
   Crossfade only; the CSS owns the timing. */
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
   ============================================================
   Below 1200px the header field is gone and the menu carries it as its
   first thing. Without script the glyph is a plain link to the SRP. */
(function () {
  'use strict';

  var glyph  = document.querySelector('[data-opens-search]');
  var toggle = document.querySelector('.menu-toggle');
  var menu   = document.getElementById('site-menu');
  if (!glyph || !toggle || !menu) return;

  glyph.addEventListener('click', function (e) {
    e.preventDefault();
    if (toggle.getAttribute('aria-expanded') !== 'true') toggle.click();
    var field = menu.querySelector('input[type="search"]');
    if (field) field.focus();
  });
})();
