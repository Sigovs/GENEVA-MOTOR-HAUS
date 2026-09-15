/* ============================================================
   GENEVA MOTOR HAUS — ds-v1.js — the design system page
   ============================================================
   Everything this page states about a value, it reads from the site's
   live CSS when it opens:

   · [data-token-value]  the resolved value of a custom property
   · [data-contrast]     the WCAG ratio of a token pair, blended over its
                         ground, graded AA / AAA (large text: 3:1)
   · [data-measure]      the computed size, line height, weight and face of
                         a type sample, at this window's width
   · [data-replay]       plays a sample section's entrance again
   · the section pills   mark the section in view
   ============================================================ */
(function () {
  'use strict';

  var body = document.body;
  var cs = getComputedStyle(body);

  /* ---- token values ---- */
  [].slice.call(document.querySelectorAll('[data-token-value]')).forEach(function (el) {
    var v = cs.getPropertyValue(el.getAttribute('data-token-value')).trim();
    el.textContent = v || '—';
  });

  /* ---- contrast ---- */
  function resolve(token) {
    var probe = document.createElement('span');
    probe.style.color = 'var(' + token + ')';
    body.appendChild(probe);
    var c = getComputedStyle(probe).color;
    body.removeChild(probe);
    return c;
  }
  function parse(c) {
    var m = c.match(/[\d.]+/g).map(Number);
    return { rgb: m.slice(0, 3), a: m.length > 3 ? m[3] : 1 };
  }
  function lum(rgb) {
    var v = rgb.map(function (x) { x /= 255; return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); });
    return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2];
  }
  function ratio(fg, bg) {
    var f = parse(fg), b = parse(bg);
    var mixed = f.rgb.map(function (x, i) { return x * f.a + b.rgb[i] * (1 - f.a); });
    var l1 = lum(mixed), l2 = lum(b.rgb);
    return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
  }
  [].slice.call(document.querySelectorAll('[data-contrast]')).forEach(function (row) {
    var r = ratio(resolve(row.getAttribute('data-fg')), resolve(row.getAttribute('data-bg')));
    var large = row.hasAttribute('data-large');
    var aa = large ? 3 : 4.5, aaa = large ? 4.5 : 7;
    row.querySelector('[data-ratio]').textContent = r.toFixed(2) + ':1';
    var grade = document.createElement('span');
    grade.className = 'ds-grade';
    if (row.hasAttribute('data-fill')) {
      grade.textContent = r >= aa ? 'Passes, still a fill' : 'Fill only';
    } else if (r >= aaa) {
      grade.textContent = 'AAA'; grade.classList.add('is-pass');
    } else if (r >= aa) {
      grade.textContent = 'AA' + (large ? ' large' : ''); grade.classList.add('is-pass');
    } else {
      grade.textContent = 'Fails AA';
    }
    var cell = row.querySelector('[data-grade]');
    cell.textContent = '';
    cell.appendChild(grade);
  });

  /* ---- type measures ---- */
  var metas = [].slice.call(document.querySelectorAll('[data-measure]'));
  function measure() {
    metas.forEach(function (meta) {
      var el = document.getElementById(meta.getAttribute('data-measure'));
      if (!el) return;
      var s = getComputedStyle(el);
      var size = parseFloat(s.fontSize);
      var lh = s.lineHeight === 'normal' ? 'normal' : (parseFloat(s.lineHeight) / size).toFixed(2);
      var face = s.fontFamily.split(',')[0].replace(/["']/g, '');
      var track = s.letterSpacing === 'normal' ? '' : ' · tracking ' + s.letterSpacing;
      meta.textContent = face + ' ' + s.fontWeight + ' · ' + Math.round(size) + 'px / ' + lh + track + (s.textTransform === 'uppercase' ? ' · upper case' : '');
    });
  }
  measure();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(measure);
  var t;
  window.addEventListener('resize', function () { clearTimeout(t); t = setTimeout(measure, 150); });

  /* ---- replay an entrance ---- */
  [].slice.call(document.querySelectorAll('[data-replay]')).forEach(function (btn) {
    var note = btn.parentElement.querySelector('[data-replay-note]');
    btn.addEventListener('click', function () {
      var stage = document.getElementById(btn.getAttribute('data-replay'));
      if (!stage) return;
      if (!document.documentElement.classList.contains('reveal-armed')) {
        if (note) note.textContent = 'Motion is reduced on this device, so the page arrives complete — as it should.';
        return;
      }
      stage.classList.add('ds-noanim');
      stage.classList.remove('is-revealed');
      void stage.offsetWidth;
      stage.classList.remove('ds-noanim');
      requestAnimationFrame(function () { requestAnimationFrame(function () { stage.classList.add('is-revealed'); }); });
    });
  });

  /* ---- the section in view ---- */
  var links = [].slice.call(document.querySelectorAll('.ds-nav a'));
  var targets = links.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); });
  var head = document.querySelector('.ds-head');
  if ('IntersectionObserver' in window && links.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        if (en.target === head) {   // back at the top: no section is current, and the pills return to their start
          links.forEach(function (a) { a.removeAttribute('aria-current'); });
          links[0].parentElement.parentElement.scrollTo({ left: 0, behavior: 'auto' });
          return;
        }
        var k = targets.indexOf(en.target);
        links.forEach(function (a, i) { if (i === k) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current'); });
        var cur = links[k];
        if (cur && cur.scrollIntoView && cur.parentElement.parentElement.scrollWidth > cur.parentElement.parentElement.clientWidth) {
          cur.parentElement.parentElement.scrollTo({ left: cur.offsetLeft - 24, behavior: 'auto' });
        }
      });
    }, { rootMargin: '-35% 0px -60% 0px' });
    targets.forEach(function (s) { if (s) io.observe(s); });
    if (head) io.observe(head);
  }
})();
