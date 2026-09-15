/* ============================================================
   GENEVA MOTOR HAUS — vdp-v2.js — the vehicle detail page
   ============================================================
   The page is complete without this file: the first photograph shows,
   the contact sheet links every photograph at size, the disclosures open
   natively, the phone and email links work, the related row scrolls.

   What it adds — CMC's VDP mechanics, with its defects left behind:
   · the gallery: arrows and thumbnails, ←/→ on the stage and the strip,
     a swipe on touch, the counter; it wraps;
   · Save (kept in this browser), Share (the system sheet, or the link
     copied and announced) and Text to phone (send the page to yourself);
   · a link to #ask / #finance / #shipping opens its disclosure and lands
     below the header;
   · the question form checks itself and answers in place — a static
     preview cannot deliver it, and says so instead of pretending;
   · the payment estimate uses the visitor's own down payment and rate;
   · the related row pages with dots that follow the scroll.
   ============================================================ */
(function () {
  'use strict';

  var calm = window.matchMedia('(prefers-reduced-motion: reduce)');
  var live = document.getElementById('vdp-live');
  var say = function (msg) { if (live) { live.textContent = ''; setTimeout(function () { live.textContent = msg; }, 30); } };

  /* ---- the gallery ---- */
  var gal = document.querySelector('[data-gallery]');
  if (gal) {
    var frames = [].slice.call(gal.querySelectorAll('.vdp-gal__frame'));
    var thumbs = [].slice.call(gal.querySelectorAll('.vdp-gal__thumb'));
    var at = gal.querySelector('[data-gal-at]');
    var stage = gal.querySelector('.vdp-gal__stage');
    var i = 0;
    var show = function (n, focusThumb) {
      if (!frames.length) return;
      i = (n + frames.length) % frames.length;
      frames.forEach(function (f, k) {
        f.classList.toggle('is-active', k === i);
        if (k === i && f.loading === 'lazy') f.loading = 'eager';
      });
      thumbs.forEach(function (t, k) { t.setAttribute('aria-current', String(k === i)); });
      if (at) at.textContent = String(i + 1);
      var t = thumbs[i];
      if (t) {
        var li = t.parentElement, strip = li.parentElement;
        if (li.offsetLeft < strip.scrollLeft || li.offsetLeft + li.offsetWidth > strip.scrollLeft + strip.clientWidth) {
          strip.scrollTo({ left: li.offsetLeft - strip.clientWidth / 2 + li.offsetWidth / 2, behavior: calm.matches ? 'auto' : 'smooth' });
        }
        if (focusThumb) t.focus();
      }
      var next = frames[(i + 1) % frames.length];
      if (next && next.loading === 'lazy') next.loading = 'eager';
    };
    [].slice.call(gal.querySelectorAll('[data-step]')).forEach(function (b) {
      b.addEventListener('click', function () { show(i + Number(b.getAttribute('data-step'))); });
    });
    thumbs.forEach(function (t, k) {
      t.addEventListener('click', function () { show(k); });
      t.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowRight') { e.preventDefault(); show(i + 1, true); }
        if (e.key === 'ArrowLeft') { e.preventDefault(); show(i - 1, true); }
      });
    });
    if (stage) {
      stage.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowRight') { e.preventDefault(); show(i + 1); }
        if (e.key === 'ArrowLeft') { e.preventDefault(); show(i - 1); }
      });
      var x0 = null, y0 = null;
      stage.addEventListener('pointerdown', function (e) { if (e.pointerType !== 'mouse') { x0 = e.clientX; y0 = e.clientY; } });
      stage.addEventListener('pointerup', function (e) {
        if (x0 === null) return;
        var dx = e.clientX - x0, dy = e.clientY - y0;
        x0 = y0 = null;
        if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy)) show(i + (dx < 0 ? 1 : -1));
      });
      stage.addEventListener('pointercancel', function () { x0 = y0 = null; });
    }
  }

  /* ---- Save, Share, Text to phone ---- */
  var title = (document.querySelector('.vdp-plate__title') || {}).textContent;
  title = title ? title.replace(/\s+/g, ' ').trim() : document.title;
  var copy = function (text) {
    if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(text);
    return new Promise(function (ok, no) {
      var ta = document.createElement('textarea');
      ta.value = text; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy') ? ok() : no(); } catch (err) { no(err); }
      ta.remove();
    });
  };
  var flash = function (btn, text) {
    var label = btn.querySelector('span');
    if (!label) return;
    var was = label.textContent;
    label.textContent = text;
    setTimeout(function () { label.textContent = was; }, 1600);
  };

  var save = document.querySelector('[data-save]');
  if (save) {
    var KEY = 'gmh-saved', slug = save.getAttribute('data-save');
    var read = function () { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (err) { return []; } };
    var paint = function (on) {
      save.setAttribute('aria-pressed', String(on));
      var label = save.querySelector('span');
      if (label) label.textContent = on ? 'Saved' : 'Save';
    };
    paint(read().indexOf(slug) > -1);
    save.addEventListener('click', function () {
      var list = read(), k = list.indexOf(slug), on = k === -1;
      if (on) list.push(slug); else list.splice(k, 1);
      try { localStorage.setItem(KEY, JSON.stringify(list)); } catch (err) { /* private mode: the state still shows */ }
      paint(on);
      say(on ? 'Saved in this browser' : 'Removed from saved');
    });
  }

  var share = document.querySelector('[data-share]');
  if (share) {
    share.addEventListener('click', function () {
      if (navigator.share) { navigator.share({ title: title, url: location.href }).catch(function () {}); return; }
      copy(location.href).then(function () { flash(share, 'Link copied'); say('Link copied'); },
                               function () { say('Could not copy the link'); });
    });
  }
  var sms = document.querySelector('[data-text-to-phone]');
  if (sms) {
    var body = title + ' — ' + location.href;
    sms.setAttribute('href', 'sms:?&body=' + encodeURIComponent(body));
    sms.addEventListener('click', function (e) {
      if (window.matchMedia('(hover: none) and (pointer: coarse)').matches) return;   // a phone follows the sms: link
      e.preventDefault();                                                            // a desk copies it instead
      copy(body).then(function () { flash(sms, 'Copied'); say('Link copied — paste it into a message'); });
    });
  }

  /* ---- #ask / #finance / #shipping open their disclosure ---- */
  var openFromHash = function (hash, scroll) {
    if (!hash || hash.length < 2) return;
    var target = document.getElementById(hash.slice(1));
    if (!target || target.tagName !== 'DETAILS') return;
    target.open = true;
    if (scroll) target.scrollIntoView({ block: 'start', behavior: calm.matches ? 'auto' : 'smooth' });
    var sum = target.querySelector('summary');
    if (sum) sum.focus({ preventScroll: true });
  };
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    if (!a) return;
    var target = document.getElementById(a.getAttribute('href').slice(1));
    if (!target || target.tagName !== 'DETAILS') return;
    e.preventDefault();
    history.replaceState(null, '', a.getAttribute('href'));
    openFromHash(a.getAttribute('href'), true);
  });
  if (location.hash) openFromHash(location.hash, true);

  /* ---- the question: checked here, answered in place ---- */
  var ask = document.querySelector('.vdp-ask');
  if (ask) {
    var sent = ask.parentElement.querySelector('.vdp-sent');
    ask.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!ask.reportValidity()) return;
      if (!sent) return;
      var first = (ask.elements.fname && ask.elements.fname.value.trim()) || '';
      var slot = sent.querySelector('[data-sent-name]');
      if (slot) slot.textContent = first ? ', ' + first : '';
      ask.hidden = true;
      sent.hidden = false;
      sent.focus();
    });
  }

  /* ---- the payment estimate, from the visitor's own numbers ---- */
  var calc = document.querySelector('.vdp-calc');
  if (calc) {
    var price = Number(calc.getAttribute('data-price')) || 0;
    var out = calc.querySelector('.vdp-calc__out');
    var num = function (n) { var f = calc.elements[n]; return f ? Number(String(f.value).replace(/[^0-9.]/g, '')) : NaN; };
    var fmt = function (n) { return '$' + Math.round(n).toLocaleString('en-US'); };
    var run = function () {
      var aprField = calc.elements.apr;
      var apr = num('apr'), months = num('term'), principal = price - (num('down') || 0);
      if (!aprField || aprField.value.trim() === '' || !isFinite(apr)) { out.textContent = 'Enter a rate'; return; }
      if (principal <= 0 || !months) { out.textContent = '—'; return; }
      var r = apr / 100 / 12;
      var pay = r === 0 ? principal / months : principal * r / (1 - Math.pow(1 + r, -months));
      out.textContent = fmt(pay) + ' / mo';
    };
    calc.addEventListener('input', run);
    calc.addEventListener('change', run);
    calc.addEventListener('submit', function (e) { e.preventDefault(); run(); });
    run();
  }

  /* ---- the related row: pages and dots that follow the scroll ---- */
  var track = document.querySelector('[data-track]');
  var dots = document.querySelector('[data-dots]');
  if (track && dots) {
    var items = [].slice.call(track.children);
    var perPage = function () { return items.length ? Math.max(1, Math.round(track.clientWidth / items[0].getBoundingClientRect().width)) : 1; };
    var pages = 0;
    var build = function () {
      var n = Math.ceil(items.length / perPage());
      if (n === pages) return;
      pages = n;
      dots.textContent = '';
      if (n < 2) return;
      for (var p = 0; p < n; p++) {
        (function (p) {
          var b = document.createElement('button');
          b.type = 'button';
          b.className = 'vdp-rel__dot';
          b.setAttribute('aria-label', 'Page ' + (p + 1) + ' of ' + n);
          b.addEventListener('click', function () {
            var target = items[Math.min(items.length - 1, p * perPage())];
            track.scrollTo({ left: target.offsetLeft - track.offsetLeft, behavior: calm.matches ? 'auto' : 'smooth' });
          });
          dots.appendChild(b);
        })(p);
      }
      mark();
    };
    var mark = function () {
      var btns = [].slice.call(dots.children);
      if (!btns.length) return;
      var max = track.scrollWidth - track.clientWidth;
      var p = max <= 0 ? 0 : Math.round((track.scrollLeft / max) * (btns.length - 1));
      btns.forEach(function (b, k) { b.setAttribute('aria-current', String(k === p)); });
    };
    var t1 = 0, t2 = 0;
    track.addEventListener('scroll', function () { clearTimeout(t1); t1 = setTimeout(mark, 90); }, { passive: true });
    window.addEventListener('resize', function () { clearTimeout(t2); t2 = setTimeout(function () { pages = 0; build(); }, 150); });
    build();
  }
})();
