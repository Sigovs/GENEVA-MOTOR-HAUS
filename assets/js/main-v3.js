/* Chicago Motor Cars — main
   The page is complete without this file. Everything here adds a
   convenience; nothing here is the only way to reach content.

   The chapter-rail observer and the hero reel were removed with the
   sections they drove. Both are in git at efd7a40 and come back with
   their markup, not before — a guarded IIFE that returns early on a
   page with no matching elements is still dead code asking to be read. */

(function () {
  'use strict';

  var toggle = document.querySelector('.menu-toggle');
  var menu = document.getElementById('site-menu');
  if (!toggle || !menu) return;

  // The menu markup ships `hidden` so a failed script leaves a page
  // with a visible header and a working hero, never a stuck overlay.
  // Script present → the toggle becomes real.
  document.documentElement.classList.add('has-js');

  function setOpen(open) {
    toggle.setAttribute('aria-expanded', String(open));
    menu.hidden = !open;
    // The page scrolls now, so without this the document slides around
    // behind the overlay and the visitor loses their place.
    document.body.style.overflow = open ? 'hidden' : '';
    if (open) {
      var first = menu.querySelector('a');
      if (first) first.focus();
    }
  }

  toggle.addEventListener('click', function () {
    setOpen(toggle.getAttribute('aria-expanded') !== 'true');
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
      setOpen(false);
      toggle.focus();
    }
  });

  menu.addEventListener('click', function (e) {
    if (e.target.closest('a')) setOpen(false);
  });

  // Close only if the toggle itself has gone away — it used to close on
  // every resize into desktop, which is now wrong: the condensed header
  // puts a real toggle on desktop too, and closing the panel out from
  // under someone who deliberately opened it is worse than leaving it.
  window.addEventListener('resize', function () {
    if (toggle.getAttribute('aria-expanded') !== 'true') return;
    if (getComputedStyle(toggle).display === 'none') setOpen(false);
  });

  /* The header condenses once it has left the hero. IntersectionObserver
     on a sentinel rather than a scroll listener: the answer changes
     twice in the life of the page, so it should not be recomputed on
     every frame of every scroll. */
  var sentinel = document.querySelector('.scroll-sentinel');
  if (sentinel && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      var past = !entries[0].isIntersecting;
      document.documentElement.classList.toggle('is-condensed', past);
      // A dropdown left open would hang under a bar that no longer
      // shows the word that opened it.
      if (past) {
        document.querySelectorAll('.navmenu__trigger[aria-expanded="true"]')
          .forEach(function (t) {
            t.setAttribute('aria-expanded', 'false');
            var p = document.getElementById(t.getAttribute('aria-controls'));
            if (p) p.hidden = true;
          });
      }
    }, { threshold: 0 }).observe(sentinel);
  }
})();

/* The navigation bar's dropdowns.

   Hover opens them for a pointer, but hover is never the ONLY way in:
   the triggers are real <button>s that open on click and on Enter or
   Space, because a route that cannot be found without a pointer is not
   a route. Escape closes and returns focus to the trigger it came from.

   The panels ship in the markup rather than being built here, so with
   the script gone the mobile breakpoint stands every panel open and all
   four groups stay reachable. */
(function () {
  'use strict';

  var bar = document.querySelector('.navbar');
  if (!bar) return;

  var menus = [].slice.call(bar.querySelectorAll('.navmenu')).map(function (m) {
    return { trigger: m.querySelector('.navmenu__trigger'), panel: m.querySelector('.navmenu__panel') };
  }).filter(function (m) { return m.trigger && m.panel; });
  if (!menus.length) return;

  var closeTimer = null;

  function show(target) {
    menus.forEach(function (m) {
      var on = m === target;
      m.trigger.setAttribute('aria-expanded', String(on));
      m.panel.hidden = !on;
    });
  }
  function closeAll() { show(null); }

  menus.forEach(function (m) {
    m.trigger.addEventListener('click', function () {
      var open = m.trigger.getAttribute('aria-expanded') === 'true';
      open ? closeAll() : show(m);
    });
    // Pointer users get it on hover; the click path above still works.
    m.trigger.addEventListener('mouseenter', function () {
      clearTimeout(closeTimer);
      show(m);
    });
  });

  // A small grace period, or the panel closes while the pointer is
  // crossing the gap between the trigger and the panel below it.
  bar.addEventListener('mouseleave', function () {
    closeTimer = setTimeout(closeAll, 180);
  });
  bar.addEventListener('mouseenter', function () { clearTimeout(closeTimer); });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var open = menus.filter(function (m) { return m.trigger.getAttribute('aria-expanded') === 'true'; })[0];
    if (!open) return;
    closeAll();
    open.trigger.focus();
  });

  // Tabbing out of the bar entirely, or clicking away, closes it.
  document.addEventListener('focusin', function (e) {
    if (!bar.contains(e.target)) closeAll();
  });
  document.addEventListener('click', function (e) {
    if (!bar.contains(e.target)) closeAll();
  });
})();

/* ============================================================
   FEATURED INVENTORY — the index drives the dominant field
   ============================================================
   Hover or focus a record and the field crossfades to that vehicle.
   Enhancement only: without this script the first car stays up and every
   record is still a link to the inventory, so nothing a visitor needs
   depends on it. Pointer AND focus, so the keyboard gets the same
   behaviour rather than a degraded one. No timers, no autoplay, no
   carousel — the visitor drives it and it holds where they leave it.

   Only records carrying data-frame drive the field. The others are real
   inventory with no cut-out asset yet: they light on hover and they link
   out, but they never take the enlarged active state, because that state
   means "this is the car in the field" and awarding it to a vehicle the
   field is not showing would be the interface telling a lie.
   ============================================================ */
(function () {
  var wrap = document.querySelector('.showcase');
  if (!wrap) return;

  var cars = [].slice.call(wrap.querySelectorAll('.stage__car'));
  var recs = [].slice.call(wrap.querySelectorAll('.rec'));
  if (cars.length < 2) return;

  var driving = recs.filter(function (r) {
    return r.getAttribute('data-frame') !== null;
  });
  if (!driving.length) return;

  // The order the arrows step through is the order the INDEX is written in,
  // read off the DOM — not 0..n. If a record is ever removed or reordered,
  // the arrows follow the list the reader can see rather than a count that
  // has quietly stopped matching it.
  var frames = driving.map(function (r) { return Number(r.getAttribute('data-frame')); });
  var at = 0;

  /* THE SIDE ALTERNATES, AND IT IS DECIDED ON A CHANGE, NOT ON A STATE.

     `shown` is read off the DOM rather than assumed to be 0, so the
     opening frame is whatever the markup says is active and nothing
     slides on first paint. show() is also called by hover and by
     restore(), which frequently re-assert the SAME car — without this
     guard, crossing the list would have flung the picture sideways
     repeatedly while nothing was actually changing.

     Two elements are written on every change and they get OPPOSITE
     signs: the arriving car comes from one edge and the departing one
     leaves by the other, so they cross. Giving both the same sign made
     them pile onto one side and read as a single object sliding off.

     The reflow between setting --side and adding is-active is not
     optional. A transition starts from the last RENDERED value, so
     without forcing the style recalculation the browser would begin the
     slide from wherever the car was parked last time and travel a
     distance nobody chose — sometimes zero. Reading offsetWidth is what
     makes the new starting edge real before the class lands. */
  var calm = window.matchMedia('(prefers-reduced-motion: reduce)');
  var shown = -1;
  cars.forEach(function (c, n) { if (c.classList.contains('is-active')) shown = n; });

  var side = 1;

  function slide(incoming, outgoing) {
    if (!incoming || calm.matches) return;
    side = -side;
    if (outgoing && outgoing !== incoming) {
      outgoing.style.setProperty('--side', String(-side));
    }
    incoming.style.setProperty('--side', String(side));
    void incoming.offsetWidth;
  }

  function show(i) {
    var seat = frames.indexOf(i);
    if (seat !== -1) at = seat;
    if (i !== shown) { slide(cars[i], cars[shown]); shown = i; }
    cars.forEach(function (c, n) {
      c.classList.toggle('is-active', n === i);
    });
    recs.forEach(function (r) {
      var on = r.getAttribute('data-frame') === String(i);
      r.classList.toggle('is-active', on);
      /* The index looks identical whichever record is chosen — that is
         the brief. aria-pressed is how the choice still reaches anyone
         who cannot see the photograph change, and it costs no pixels. */
      /* The record is a <div> now — it holds a link as well as being
         selectable, and a link inside a button is invalid. The pressed
         state lives on the overlay button that fills the card. */
      var pressable = r.hasAttribute('aria-pressed') ? r : r.querySelector('.rec__select');
      if (pressable) pressable.setAttribute('aria-pressed', String(on));
    });
  }

  /* THE INDEX NO LONGER DRIVES THE FIELD. The arrows do, and only the
     arrows.

     Hover used to select a record, which meant the composition changed
     under a pointer that was only crossing the column on its way
     somewhere else. Every one of those accidental changes moved
     something — the type, the thumbnail, and the vehicle itself, which
     is a different height in every photograph. Advancing on an explicit
     press instead makes each change something the visitor asked for.

     TWO LEVELS OF STATE, AND ONLY ONE OF THEM IS STICKY.

     `locked` is the record the visitor actually chose — by clicking it,
     or by stepping the arrows. `show()` paints whatever is being looked
     at, which during a hover is the row under the pointer and at every
     other moment is `locked`.

     That distinction is the whole reason the earlier version had to be
     torn out. Hover used to BE the selection, so a pointer crossing the
     column on its way somewhere else left the section showing a car
     nobody picked, and there was no state to return to. Now leaving the
     list restores the choice, every time.

     Keyboard gets the same shape: focus previews, blur out of the list
     restores. The records are <button>s, not links — all four hrefs
     pointed at the same generic inventory URL, so they were never
     per-vehicle destinations, and "View all 301 vehicles" carries that
     one destination once, at the foot of the list where it belongs. */
  var locked = frames.length ? frames[0] : 0;

  function select(i) { locked = i; show(i); }
  function restore() { show(locked); }

  driving.forEach(function (rec) {
    var i = Number(rec.getAttribute('data-frame'));
    rec.addEventListener('click', function () { select(i); });
    rec.addEventListener('mouseenter', function () { show(i); });
    rec.addEventListener('focus', function () { show(i); });
  });

  var list = wrap.querySelector('.recs');
  if (list) {
    list.addEventListener('mouseleave', restore);
    list.addEventListener('focusout', function (e) {
      if (!list.contains(e.relatedTarget)) restore();
    });
  }

  // Arrows wrap rather than disable at the ends. Four vehicles is a ring,
  // not a document — a dead control at either end would be the only piece
  // of this section that can be pressed and do nothing.
  [].slice.call(wrap.querySelectorAll('.stage__arrow')).forEach(function (btn) {
    var step = Number(btn.getAttribute('data-step'));
    btn.addEventListener('click', function () {
      /* select(), not show() — an arrow press is a CHOICE, so it moves
         the locked record. Stepping with show() would have left `locked`
         behind, and the next stray hover would have snapped the section
         back to whatever it used to be. */
      var next = (at + step + frames.length) % frames.length;
      select(frames[next]);
    });
  });
})();

/* ============================================================
   THE HERO SLIDER — two slides: the film, then the frame
   ============================================================
   Not a carousel. There is no timer and nothing advances on a clock:
   the film runs once, and reaching its end is what hands the stage to
   the photograph. After that the hero holds where it is until a visitor
   says otherwise. That is the difference between a sequence with an
   ending and a loop that talks over itself.

   Playback is started HERE rather than by an `autoplay` attribute,
   because the attribute begins downloading and playing before anything
   can ask whether this visitor wants motion.

   Under prefers-reduced-motion the film is not merely paused — it never
   loads, the photograph is the hero from the first paint, and the pager
   is removed rather than left showing a choice that has become a lie.

   The fade waits for `canplaythrough`, not `loadeddata`. At 21 MB that
   is the difference between continuous motion and fading in to a stall.
   ============================================================ */
(function () {
  'use strict';

  var hero   = document.querySelector('.hero');
  if (!hero) return;
  var slides  = [].slice.call(hero.querySelectorAll('.hero__slide'));
  var counter = hero.querySelector('.counter');
  var num     = counter && counter.querySelector('.counter__n');
  var video   = hero.querySelector('.hero__video');
  if (slides.length < 2) return;

  var title  = hero.querySelector('.hero__slide-title');

  var at = 0;
  var calm = window.matchMedia('(prefers-reduced-motion: reduce)');

  function pad(n) { return (n < 10 ? '0' : '') + n; }

  /* The arc is restarted by REPLACING the class, not by toggling a
     property: a CSS animation does not rewind while its element keeps
     the class, so a second visit to the film would have shown an arc
     already full. Remove, force a reflow, add back — the one reliable
     retrigger without a second set of keyframes. */
  var STILL_HOLD = 5;          // seconds a still slide is given
  var arc = counter && counter.querySelector('.counter__arc');
  var onArcEnd = null;

  function arm(seconds, andThen) {
    if (!counter) return;
    counter.classList.remove('is-timing', 'is-static');
    void counter.offsetWidth;
    counter.style.setProperty('--run', seconds + 's');
    counter.style.setProperty('--run-state', 'running');
    counter.classList.add('is-timing');

    /* The ADVANCE is driven by the arc's own animationend, not by a
       parallel setTimeout. One clock: whatever the arc shows is what
       actually happens, and a paused arc is a paused slide for free —
       a separate timer would keep counting behind a stopped instrument
       and the two would drift apart within one cycle. */
    if (arc && onArcEnd) arc.removeEventListener('animationend', onArcEnd);
    onArcEnd = null;
    if (arc && andThen) {
      onArcEnd = function () { onArcEnd = null; andThen(); };
      arc.addEventListener('animationend', onArcEnd, { once: true });
    }
  }
  function settle() {
    if (!counter) return;
    counter.classList.remove('is-timing');
    counter.classList.add('is-static');
  }

  /* The word advances on EVERY change of slide — clicked or automatic —
     and it runs its own, longer cycle. It is deliberately not read off
     the slide: with four words over two frames it would otherwise be
     captioning a picture it does not describe. It is the register the
     house speaks in, turning over.

     Crossfaded rather than cut: it is the only thing on this row whose
     content swaps, and a hard swap beside a smoothly running arc reads
     as a glitch. */
  /* THE CHAPTER NAME IS READ OFF THE SLIDE, NOT OFF A LIST.

     It used to run its own rotation through four words over two slides,
     deliberately, so the word read as a register rather than a caption.
     That is a defensible idea and it produced an undefensible artefact:
     the numeral said 01 while the word said Performance, so the two
     halves of one chapter marker disagreed twice per cycle.

     Each slide now carries its own data-title, which is what the markup
     comment already said it wanted. Number, name and media cannot drift,
     because there is only one source for all three: the slide. A third
     chapter arrives when a third slide does, not before. */
  function nameSlide(i) {
    if (!title) return;
    var next = slides[i] && slides[i].getAttribute('data-title');
    if (!next || next === title.textContent) return;
    title.classList.add('is-swapping');
    setTimeout(function () {
      title.textContent = next;
      title.classList.remove('is-swapping');
    }, 200);
  }

  function go(i) {
    at = i;
    slides.forEach(function (s, n) { s.classList.toggle('is-current', n === i); });
    nameSlide(i);
    if (num) num.textContent = pad(i + 1);
    // Nothing plays while it is not the thing on screen.
    if (video && i !== 0) video.pause();
    /* A still now has a duration too, so it gets a real arc rather than
       an empty ring — five seconds, then it hands back to the film. The
       film is timed by the film itself; see `ended` below. */
    if (i !== 0) {
      if (calm.matches) settle();
      else arm(STILL_HOLD, function () { go(0); restartFilm(); });
    }
  }

  function restartFilm() {
    if (!video || calm.matches) return;
    video.currentTime = 0;
    if (isFinite(video.duration)) arm(video.duration.toFixed(2));
    video.play().catch(function () {});
  }

  if (counter) {
    counter.addEventListener('click', function () {
      var next = (at + 1) % slides.length;
      go(next);
      if (next === 0) restartFilm();
    });
  }

  /* ---- reduced motion: the photograph IS the hero ---- */
  function standDown() {
    if (video) { video.pause(); video.removeAttribute('src'); video.load(); }
    go(1);
    if (counter) counter.remove();   // one slide reachable, so no instrument
  }

  if (calm.matches) { standDown(); return; }
  calm.addEventListener('change', function (e) { if (e.matches) standDown(); });

  if (!video) return;

  function reveal() { video.classList.add('is-playing'); }

  /* THE FILM DRIVES THE ARC ONLY WHILE THE FILM IS WHAT THE ARC IS TIMING.

     Without the `at === 0` guard the still slide never ran and the hero
     stopped dead on frame 02. HTMLMediaElement.pause() does not fire its
     `pause` event synchronously — it queues a media element task — so
     go(1) ran in this order:

         video.pause()          queues `pause`
         arm(STILL_HOLD, ...)   --run-state: running
         (task queue drains)    `pause` handler -> --run-state: paused

     The arc was armed with a real 5s duration and then immediately frozen
     at dashoffset 204.8 by an event about a video that is not even on
     screen. And because the advance hangs off the arc's animationend, a
     stopped arc is a stopped sequence: measured on the page, frame 02 was
     still up 6.3s into a 5s hold, and would have stayed up forever.

     Guarding on `at` rather than reordering the two calls is the fix that
     keeps holding true. The ordering could be swapped today, but any
     later pause() from anywhere else would silently break the still
     again; the film's playback state is simply not information about a
     clock the film is not running. */
  video.addEventListener('play',  function () {
    if (counter && at === 0) counter.style.setProperty('--run-state', 'running');
  });
  video.addEventListener('pause', function () {
    if (counter && at === 0) counter.style.setProperty('--run-state', 'paused');
  });

  video.addEventListener('canplaythrough', function () {
    if (isFinite(video.duration)) arm(video.duration.toFixed(2));
    var p = video.play();
    if (p && typeof p.catch === 'function') p.then(reveal).catch(function () {});
    else reveal();
  }, { once: true });

  // The end of the film is the transition.
  video.addEventListener('ended', function () { go(1); });

  /* ---- Nothing advances past someone who is looking at it ----
     The hero now moves on its own, so it has to stop when a visitor is
     engaged with it. Pointer over the hero, or keyboard focus inside it,
     holds BOTH the film and the arc — and because the arc is the clock,
     holding the arc holds the slide. This is the same protection the
     earlier reel carried, and it is what separates a sequence from a
     carousel that talks over you. */
  function hold(on) {
    if (counter) counter.style.setProperty('--run-state', on ? 'paused' : 'running');
    if (!video) return;
    if (on) video.pause();
    else if (slides[0].classList.contains('is-current')) video.play().catch(function () {});
  }
  hero.addEventListener('mouseenter', function () { hold(true); });
  hero.addEventListener('mouseleave', function () { hold(false); });
  /* Focus holds it only for a KEYBOARD user. Clicking the counter also
     focuses it, and with a plain focusin handler that click paused the
     hero permanently — the visitor stepped one slide and the sequence
     never started again. :focus-visible is exactly the distinction:
     someone navigating by keyboard needs the hold, someone who just
     pressed a button does not.

     The try/catch is not decoration — :focus-visible throws on engines
     that do not know the selector, and a hero that stops advancing
     because of a matches() call would be a poor trade for a nicety. */
  function focusHolds(el) {
    if (!el || el === document.body) return false;
    try { return el.matches(':focus-visible'); }
    catch (e) { return false; }
  }
  hero.addEventListener('focusin', function (e) {
    if (focusHolds(e.target)) hold(true);
  });
  hero.addEventListener('focusout', function (e) {
    if (!hero.contains(e.relatedTarget)) hold(false);
  });

  document.addEventListener('visibilitychange', function () {
    hold(document.hidden);
  });

  video.load();
})();

/* ============================================================
   HERO SEARCH — a row knows whether it has been answered
   ============================================================
   CSS alone cannot ask this. :placeholder-shown does not apply to
   <select>, and :has() cannot test a select's VALUE — only its
   structure — so the one honest way to tell an empty control from an
   answered one is to read it.

   Two lines of state, and it also runs on load: a browser restoring
   form values after a back-navigation would otherwise show four filled
   selects behind four empty-looking labels.
   ============================================================ */
(function () {
  'use strict';

  var rows = [].slice.call(document.querySelectorAll('.hunt__field'));
  if (!rows.length) return;

  rows.forEach(function (row) {
    var control = row.querySelector('.hunt__control');
    var out     = row.querySelector('.hunt__value');
    if (!control) return;
    function sync() {
      var filled = control.value !== '';
      row.classList.toggle('is-filled', filled);
      /* The visible value is a span, not the select's own text: the
         select is an invisible sheet covering the row, so it has no text
         to show. Writing the chosen option's label here is what keeps
         the row readable — and it reads the OPTION rather than the raw
         value, so what appears is exactly what was picked from the list. */
      /* The value line is written in EVERY state, answered or not. Four
         labels over four empty lines gave the visitor nothing to read and
         no way to tell a filter that was open from one that was broken;
         "Any Make" states the control's current setting, which is what a
         resting filter actually is. The placeholder option carries that
         wording, so the line is always the option list's own language and
         never a second string invented here. */
      if (out) out.textContent = control.options[control.selectedIndex].text;
    }
    control.addEventListener('change', sync);
    sync();
  });
})();

/* ============================================================
   STORY — one composed reveal for the proof area
   ============================================================
   Role: HIERARCHY. The three figures are not equal and the motion says
   so — the claim counts, and the two facts that support it arrive once
   it has landed. Order carries the ranking that scale alone was only
   half carrying.

   One sequence, one trigger, once per visit:

     30,000+ counts, 1750ms, smootherstep
     at 82% of that count -> 2003 slides in from the right
     120ms later          -> $2B+ follows

   The reveal is driven by the COUNTER'S OWN PROGRESS, not by a second
   timer and not by a scroll range. A parallel timer would drift from the
   thing it is supposed to be answering; scroll ranges would put the
   secondary facts wherever the reader's scrolling happened to leave
   them. Reading the count means the two events cannot come apart.

   NOTHING IS HIDDEN UNTIL THE SCRIPT SAYS SO. The hidden state lives
   behind .is-armed, which only this file adds, and only after it has
   checked that motion is allowed. A failed script, a blocked file or a
   reduced-motion setting all leave three finished figures on screen —
   which is what the markup already contains.
   ============================================================ */
(function () {
  'use strict';

  var stats = document.querySelector('.story__stats');
  if (!stats) return;

  var fig    = stats.querySelector('.stat__n[data-count-to]');
  var proofs = [].slice.call(stats.querySelectorAll('.stat--proof'));
  if (!fig || !proofs.length) return;

  var calm = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (calm.matches || !('IntersectionObserver' in window)) return;

  stats.classList.add('is-armed');

  function render(el, value, done) {
    var counting = !done && el.hasAttribute('data-decimals');
    var text = counting
      ? value.toFixed(Number(el.getAttribute('data-decimals')) || 1)
      : (el.hasAttribute('data-plain')
          ? String(Math.round(value))
          : Math.round(value).toLocaleString('en-US'));
    var suffix = el.getAttribute('data-suffix') || '';
    if (!done) suffix = suffix.replace(/\+$/, '');
    el.textContent = (el.getAttribute('data-prefix') || '') + text + suffix;
  }

  /* Smootherstep: zero velocity at both ends, so the count starts from
     rest and settles rather than bolting and braking. */
  function ease(t) { return t * t * t * (t * (t * 6 - 15) + 10); }

  var HANDOVER = 0.82;   /* the last 18% of the count */
  var GAP      = 120;    /* ms between the two proof points */

  function play() {
    var target = Number(fig.getAttribute('data-count-to'));
    if (!isFinite(target)) return;
    var dur = 1750;
    var t0 = null;
    var handed = false;

    function frame(now) {
      if (t0 === null) t0 = now;
      var p = Math.min(1, (now - t0) / dur);
      render(fig, target * ease(p), p === 1);

      if (!handed && p >= HANDOVER) {
        handed = true;
        proofs.forEach(function (el, i) {
          setTimeout(function () { el.classList.add('is-in'); }, i * GAP);
        });
      }
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  /* An intentional threshold, not one pixel. 0.45 of the proof row means
     the reader has arrived at the composition rather than clipped its top
     edge on the way past — and unobserving on the first hit is what stops
     a small scroll wobble replaying it. */
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      io.disconnect();
      stats.classList.add('is-live');
      play();
    });
  }, { threshold: 0.45 });

  io.observe(stats);
})();

/* ============================================================
   SECTION ENTRY — one observer for every chapter below the hero
   ============================================================
   Sections opt in with `data-reveal`. The hero does not carry it and
   keeps its own behaviour.

   Nothing is hidden until this runs and has checked that motion is
   allowed — the CSS states all sit behind `.reveal-armed`, which only
   this file adds. A blocked script, a parse error or a reduced-motion
   setting therefore leaves every section complete rather than blank,
   which is the one failure mode a scroll-reveal must not have.

   rootMargin rather than a ratio threshold: a section taller than the
   viewport can never reach a 25% intersection ratio on a short screen,
   and the reveal would simply never fire. Firing when the section's top
   passes 78% of the viewport height means the same intentional moment
   at every section height and every window size.

   unobserve on the first hit — one clean entrance per visit, and a small
   scroll wobble cannot replay it.
   ============================================================ */
(function () {
  'use strict';

  var sections = [].slice.call(document.querySelectorAll('[data-reveal]'));
  if (!sections.length) return;

  var calm = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (calm.matches || !('IntersectionObserver' in window)) return;

  document.documentElement.classList.add('reveal-armed');

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      io.unobserve(e.target);
      e.target.classList.add('is-revealed');
    });
  }, { threshold: 0, rootMargin: '0px 0px -22% 0px' });

  sections.forEach(function (s) { io.observe(s); });

  /* A section already on screen at load — a deep link, or a restored
     scroll position — reveals immediately rather than waiting for a
     scroll that may never come. */
  requestAnimationFrame(function () {
    sections.forEach(function (s) {
      if (s.getBoundingClientRect().top < window.innerHeight * 0.78) {
        io.unobserve(s);
        s.classList.add('is-revealed');
      }
    });
  });
})();

/* ============================================================
   THE BREAK — a film that costs nothing until it is nearly seen
   ============================================================
   The file is 20MB. Shipping it in the markup would mean every visitor
   who never scrolls past the inventory pays for a band they did not
   reach, so the <source> ships with data-src and no src, and this
   attaches it one viewport ahead of the band.

   Under prefers-reduced-motion the source is NEVER attached. Not
   attached-then-paused: not fetched at all. The poster is a real frame
   from the film, so the band is a photograph of the room in that case
   rather than a black rectangle waiting for something.

   THE PLAY/PAUSE CONTROL WAS REMOVED at Alex's direction. Recorded
   because it has a cost: motion-taste I1 asks that an autoplaying loop
   be stoppable, and now it is not. What is left standing in its place
   is the reduced-motion path, which is the stronger half of that rule
   anyway — anyone who has asked their system for less movement never
   receives the film at all, and the band is a still photograph for
   them. The loop only ever runs for someone who has not asked to be
   spared it. It is also muted and aria-hidden, so it is decoration in
   the accessibility tree rather than content that cannot be paused.
   ============================================================ */
(function () {
  'use strict';

  var band = document.querySelector('.brk');
  if (!band) return;

  var video = band.querySelector('.brk__video');
  var source = band.querySelector('.brk__video source');
  if (!video || !source) return;

  var calm = window.matchMedia('(prefers-reduced-motion: reduce)');
  var attached = false;

  function attach() {
    if (attached || calm.matches) return;
    attached = true;
    source.src = source.getAttribute('data-src');
    video.load();
  }

  function play() {
    if (calm.matches) return;
    attach();
    var p = video.play();
    /* Autoplay can be refused even when muted. If it is, the band keeps
       its poster, which is a real frame of the same room — so a refusal
       costs the movement and nothing else. */
    if (p && p.catch) p.catch(function () {});
  }

  if ('IntersectionObserver' in window) {
    /* Two observers, two margins. The outer one attaches the source
       early enough that the film is ready when the band arrives; the
       inner one starts and stops playback, so a film left running four
       sections up is not still decoding behind the page. The band is
       pinned now, which makes the second one matter more rather than
       less: a pinned element stays intersecting for a long time. */
    new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) attach(); });
    }, { rootMargin: '100% 0px' }).observe(band);

    new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) play();
        else if (!video.paused) video.pause();
      });
    }, { threshold: 0.25 }).observe(band);
  } else {
    attach();
  }

  /* Turning the setting on mid-visit stops the film and leaves the
     poster. Turning it off does not start one nobody asked for. */
  var onCalm = function () { if (calm.matches) video.pause(); };
  if (calm.addEventListener) calm.addEventListener('change', onCalm);
  else if (calm.addListener) calm.addListener(onCalm);
})();

/* ============================================================
   SERVICE — the film loads when the band is nearly reached
   ============================================================
   Same contract as the break: the <source> ships with data-src and no
   src, script attaches it a viewport out, and under reduced motion it
   is never fetched. 1.9MB is small next to the other two, but "small"
   is not a reason to spend it on a visitor who never scrolls this far.

   There is no play control here and that is deliberate rather than an
   omission: the film is muted, decorative and aria-hidden, the register
   beside it carries every fact and every action, and under reduced
   motion the section is complete with no film at all.
   ============================================================ */
(function () {
  'use strict';

  var band = document.querySelector('.svc');
  if (!band) return;

  var video = band.querySelector('.svc__video');
  var source = band.querySelector('.svc__video source');
  if (!video || !source) return;

  var calm = window.matchMedia('(prefers-reduced-motion: reduce)');
  var attached = false;

  function attach() {
    if (attached || calm.matches) return;
    attached = true;
    source.src = source.getAttribute('data-src');
    video.load();
  }

  function play() {
    if (calm.matches) return;
    attach();
    var p = video.play();
    if (p && p.catch) p.catch(function () {});
  }

  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (e) {
      e.forEach(function (x) { if (x.isIntersecting) attach(); });
    }, { rootMargin: '100% 0px' }).observe(band);

    new IntersectionObserver(function (e) {
      e.forEach(function (x) {
        if (x.isIntersecting) play();
        else if (!video.paused) video.pause();
      });
    }, { threshold: 0.2 }).observe(band);
  } else {
    attach();
  }

  var onCalm = function () { if (calm.matches) video.pause(); };
  if (calm.addEventListener) calm.addEventListener('change', onCalm);
  else if (calm.addListener) calm.addListener(onCalm);
})();

/* The Karma film runs on the same lazy-attach + pause-offscreen module
   as the Service band: preload="none" until it is one viewport away,
   and it stops the moment it leaves. Same rules, different band. */
(function () {
  'use strict';

  var band = document.querySelector('.karma');
  if (!band) return;

  var video = band.querySelector('.karma__video');
  var source = band.querySelector('.karma__video source');
  if (!video || !source) return;

  var calm = window.matchMedia('(prefers-reduced-motion: reduce)');
  var attached = false;

  function attach() {
    if (attached || calm.matches) return;
    attached = true;
    source.src = source.getAttribute('data-src');
    video.load();
  }

  function play() {
    if (calm.matches) return;
    attach();
    var p = video.play();
    if (p && p.catch) p.catch(function () {});
  }

  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (e) {
      e.forEach(function (x) { if (x.isIntersecting) attach(); });
    }, { rootMargin: '100% 0px' }).observe(band);

    new IntersectionObserver(function (e) {
      e.forEach(function (x) {
        if (x.isIntersecting) play();
        else if (!video.paused) video.pause();
      });
    }, { threshold: 0.2 }).observe(band);
  } else {
    attach();
  }

  var onCalm = function () { if (calm.matches) video.pause(); };
  if (calm.addEventListener) calm.addEventListener('change', onCalm);
  else if (calm.addListener) calm.addListener(onCalm);
})();


/* ============================================================
   REVIEWS — the page-turn dots
   ============================================================
   The rail already works without this: it is a scroll-snap track, so a
   trackpad swipe turns a page whether or not any of this runs. What the
   script adds is the dots, and it BUILDS them rather than reading them
   from markup — dots authored by hand would be free to disagree with the
   layout the moment a breakpoint changed how many cards fit.

   The count comes from the same custom property the CSS lays out with
   (--revs-per), so there is exactly one source of truth for "how many
   cards is a page". Re-read on resize, because that number changes.
   ============================================================ */
(function () {
  var track = document.getElementById('revs-track');
  var dots  = document.querySelector('[data-dots-for="revs-track"]');
  if (!track || !dots) return;

  var cards = [].slice.call(track.children);
  if (!cards.length) return;

  var pages = 0;

  function perView() {
    var n = parseInt(getComputedStyle(track).getPropertyValue('--revs-per'), 10);
    return n > 0 ? n : 1;
  }

  function build() {
    var per = perView();
    var next = Math.ceil(cards.length / per);
    if (next === pages) return;
    pages = next;
    dots.innerHTML = '';
    for (var i = 0; i < pages; i++) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'revs__dot';
      b.setAttribute('role', 'tab');
      b.setAttribute('aria-label', 'Page ' + (i + 1) + ' of ' + pages);
      b.setAttribute('aria-selected', i === 0 ? 'true' : 'false');
      b.dataset.page = String(i);
      dots.appendChild(b);
    }
    sync();
  }

  /* Which page is showing is asked of the SCROLL POSITION, not remembered
     from the last click — a swipe and a click have to give the same
     answer, and only the scroll position knows about both. */
  function current() {
    var per = perView();
    var step = track.scrollWidth / Math.max(cards.length, 1) * per;
    if (!step) return 0;
    var i = Math.round(track.scrollLeft / step);
    return Math.max(0, Math.min(pages - 1, i));
  }

  function sync() {
    var at = current();
    for (var i = 0; i < dots.children.length; i++) {
      dots.children[i].setAttribute('aria-selected', i === at ? 'true' : 'false');
    }
  }

  dots.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('.revs__dot') : null;
    if (!b) return;
    var per = perView();
    var target = cards[Math.min(cards.length - 1, +b.dataset.page * per)];
    track.scrollTo({ left: target.offsetLeft - track.offsetLeft, behavior: 'smooth' });
  });

  var raf = 0;
  track.addEventListener('scroll', function () {
    if (raf) return;
    raf = requestAnimationFrame(function () { raf = 0; sync(); });
  }, { passive: true });

  if ('ResizeObserver' in window) new ResizeObserver(build).observe(track);
  else window.addEventListener('resize', build);

  build();
})();


/* ============================================================
   DRAG TO SCROLL — [data-drag-scroll]
   ============================================================
   Pointer Events, so one path covers mouse, trackpad and pen; touch is
   left alone because the browser's own inertia is better than anything
   written here and setPointerCapture would take it away.

   Two details are the whole thing. Scroll snapping is turned OFF for the
   duration of a drag — with `scroll-snap-type: x mandatory` still live,
   every scrollLeft write is fought by the snap engine and the rail
   judders. And the gesture only becomes a drag after ~4px of travel, so
   a click on a frame is still a click; below that threshold nothing is
   suppressed and the link fires normally.
   ============================================================ */
(function () {
  var rails = document.querySelectorAll('[data-drag-scroll]');
  if (!rails.length || !window.PointerEvent) return;

  Array.prototype.forEach.call(rails, function (rail) {
    var down = false, moved = false, startX = 0, startLeft = 0, id = null;

    rail.addEventListener('pointerdown', function (e) {
      if (e.pointerType === 'touch' || e.button !== 0) return;
      down = true; moved = false; id = e.pointerId;
      startX = e.clientX;
      startLeft = rail.scrollLeft;
    });

    rail.addEventListener('pointermove', function (e) {
      if (!down || e.pointerId !== id) return;
      var dx = e.clientX - startX;
      if (!moved) {
        if (Math.abs(dx) < 4) return;      /* still a click, not a drag */
        moved = true;
        rail.classList.add('is-dragging');
        rail.setPointerCapture(id);
      }
      e.preventDefault();
      rail.scrollLeft = startLeft - dx;
    });

    function end(e) {
      if (!down || (e && e.pointerId !== id)) return;
      down = false;
      if (moved) {
        if (rail.hasPointerCapture && rail.hasPointerCapture(id)) rail.releasePointerCapture(id);
        rail.classList.remove('is-dragging');
        /* Swallow exactly one click — the one this drag is about to
           synthesise on whatever frame the pointer came to rest over. */
        rail.addEventListener('click', function swallow(ev) {
          ev.preventDefault(); ev.stopPropagation();
          rail.removeEventListener('click', swallow, true);
        }, true);
      }
      moved = false; id = null;
    }

    rail.addEventListener('pointerup', end);
    rail.addEventListener('pointercancel', end);
    rail.addEventListener('lostpointercapture', end);
    rail.addEventListener('dragstart', function (e) { e.preventDefault(); });
  });
})();

/* ============================================================
   THE MOBILE MENU'S GROUPS COLLAPSE
   ============================================================
   Inventory alone is eighteen rows; open, the four groups run 2415px on a
   844px screen, so the menu opened onto a wall of links and the reader
   had to scroll to find out what the sections even were. Closed by
   default, the four headings fit one screen and the choice is made
   before the scrolling starts.

   PROGRESSIVE, in the same shape as the rest of this file: the markup
   ships every link in the document, and the collapsing only exists once
   this runs. Script blocked, script broken — the menu is the full list it
   always was, which is the behaviour the nav panels already rely on.

   The heading becomes a real <button> with aria-expanded and
   aria-controls rather than a <p> with a click handler, because a control
   that a screen reader cannot announce as a control is not one. Groups
   with no heading — Warranty / Events / My Garage, and the showrooms —
   are left alone: there is nothing to label them with.
   ============================================================ */
(function () {
  'use strict';

  var menu = document.getElementById('site-menu');
  if (!menu) return;

  var groups = [].slice.call(menu.querySelectorAll('.menu__group'));
  var built = 0;

  groups.forEach(function (g, i) {
    var label = g.querySelector('.menu__label');
    var links = [].slice.call(g.querySelectorAll('a'));
    if (!label || !links.length) return;

    var panel = document.createElement('div');
    panel.className = 'menu__panel';
    panel.id = 'menu-panel-' + i;

    var inner = document.createElement('div');
    inner.className = 'menu__panel-in';
    links.forEach(function (a) { inner.appendChild(a); });
    panel.appendChild(inner);

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = label.className + ' menu__trigger';
    btn.setAttribute('aria-expanded', 'false');
    btn.setAttribute('aria-controls', panel.id);
    btn.textContent = label.textContent;
    btn.insertAdjacentHTML('beforeend',
      '<svg class="menu__chev" width="12" height="8" viewBox="0 0 12 8" fill="none" aria-hidden="true">' +
      '<path d="M1 1.5 6 6.5l5-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="square"/></svg>');

    label.parentNode.replaceChild(btn, label);
    g.appendChild(panel);
    built++;

    btn.addEventListener('click', function () {
      var open = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', String(!open));
      g.classList.toggle('is-open', !open);
    });
  });

  if (!built) return;
  document.documentElement.classList.add('menu-collapsible');

  /* The opener focuses the menu's first link. With every group shut that
     link is inside a closed panel, so focus would land somewhere nobody
     can see. The first heading is the right entry point now. */
  var toggle = document.querySelector('.menu-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      if (toggle.getAttribute('aria-expanded') !== 'true') return;
      var first = menu.querySelector('.menu__trigger');
      if (first) setTimeout(function () { first.focus(); }, 0);
    });
  }
})();


/* ============================================================
   LOCATION PANELS — the film plays only while its panel is open
   ============================================================
   preload="none" until the panel is first opened, so a visitor who never
   goes near the register never downloads it. Attached on first open,
   played while open, paused the moment it closes — a looping video
   running behind a collapsed 196px panel is work nobody asked for.

   Guarded on prefers-reduced-motion: the still underneath is the whole
   picture there, and it is already in place.
   ============================================================ */
(function () {
  'use strict';

  var panels = document.querySelectorAll('.loc');
  if (!panels.length) return;

  var calm = window.matchMedia('(prefers-reduced-motion: reduce)');

  Array.prototype.forEach.call(panels, function (panel) {
    var video = panel.querySelector('.loc__video');
    if (!video) return;
    var source = video.querySelector('source[data-src]');
    var attached = false;

    function attach() {
      if (attached || !source) return;
      attached = true;
      source.src = source.getAttribute('data-src');
      video.load();
    }
    function play() {
      if (calm.matches) return;
      attach();
      var p = video.play();
      if (p && p.catch) p.catch(function () {});
    }
    function stop() { if (!video.paused) video.pause(); }

    panel.addEventListener('mouseenter', play);
    panel.addEventListener('focusin', play);
    panel.addEventListener('mouseleave', stop);
    panel.addEventListener('focusout', function (e) {
      if (!panel.contains(e.relatedTarget)) stop();
    });

    /* The one that is open on arrival starts when the register does,
       not when the page does — same rule as every other film here. */
    if (panel.classList.contains('is-open') && 'IntersectionObserver' in window) {
      new IntersectionObserver(function (entries, obs) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          play();
          obs.unobserve(panel);
        });
      }, { rootMargin: '0px 0px -20% 0px' }).observe(panel);
    }
  });
})();


/* ============================================================
   THE VDP GALLERY
   ============================================================
   Six frames stacked in one box, crossfading. Not a carousel and not a
   lightbox: the frames are all in the DOM at their real size, so the
   only thing a click changes is which one has opacity, and the browser
   never reflows.

   The strip drives it. Arrow keys walk it too, because a row of six
   buttons that only answers to a pointer is a row of six buttons a
   keyboard user has to tab through one at a time to see photograph six.

   Nothing is hidden without script: the first frame carries .is-active
   in the markup and the rest sit behind it at opacity 0, so a blocked
   script leaves the page showing the car rather than showing nothing.
   ============================================================ */
(function () {
  'use strict';

  var gal = document.querySelector('.gal');
  if (!gal) return;

  var frames = gal.querySelectorAll('.gal__stage img');
  var thumbs = gal.querySelectorAll('.gal__thumb');
  if (!frames.length || !thumbs.length) return;

  function show(i) {
    if (i < 0) i = thumbs.length - 1;
    if (i >= thumbs.length) i = 0;
    Array.prototype.forEach.call(frames, function (f, n) {
      f.classList.toggle('is-active', n === i);
    });
    Array.prototype.forEach.call(thumbs, function (t, n) {
      t.setAttribute('aria-current', n === i ? 'true' : 'false');
    });
  }

  /* The arrows walk the same index the strip sets. They are the only
     control that moves the picture without naming a destination, so they
     read the CURRENT frame off the DOM rather than keeping a counter of
     their own — a counter would drift the first time anything else set
     the frame, and the thumbnails do exactly that. */
  Array.prototype.forEach.call(gal.querySelectorAll('.gal__arrow'), function (btn) {
    btn.addEventListener('click', function () {
      var cur = 0;
      Array.prototype.forEach.call(thumbs, function (t, n) {
        if (t.getAttribute('aria-current') === 'true') cur = n;
      });
      show(cur + (parseInt(btn.getAttribute('data-step'), 10) || 1));
    });
  });

  Array.prototype.forEach.call(thumbs, function (t, i) {
    t.addEventListener('click', function () { show(i); });
    t.addEventListener('keydown', function (e) {
      var d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
      if (!d) return;
      e.preventDefault();
      var next = (i + d + thumbs.length) % thumbs.length;
      show(next);
      thumbs[next].focus();
    });
  });
})();

/* ============================================================
   SAVE A VEHICLE FROM THE RESULTS
   ============================================================
   The button ships with aria-pressed="false" in the markup, so with no
   script it is a control that announces its state and does nothing — and
   "My Garage" in the header is still the real route. This makes it toggle
   and keeps the header's count honest.

   No storage: the preview has no account and writing to localStorage
   would let the page claim a save it cannot actually keep. It holds for
   the visit, which is what it can truthfully do.
   ============================================================ */
(function () {
  'use strict';

  var saves = [].slice.call(document.querySelectorAll('.veh__save'));
  if (!saves.length) return;

  var count = document.querySelector('.navbar__count');
  var n = count ? Number(count.textContent.trim()) || 0 : 0;

  saves.forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      /* The button sits over the card. Without this the card's own link
         would follow while the mark was being set. */
      e.preventDefault();
      e.stopPropagation();
      var on = btn.getAttribute('aria-pressed') === 'true';
      btn.setAttribute('aria-pressed', String(!on));
      n += on ? -1 : 1;
      if (count) count.textContent = String(Math.max(0, n));
    });
  });
})();

/* ============================================================
   THE CHOSEN FILTERS, READ BACK
   ============================================================
   Each filter panel closes over its own choices, so once three panels are
   shut there is nothing on screen saying what the list is filtered by.
   The chips are that sentence.

   They are built from the checkboxes rather than kept in a second list,
   so the two cannot disagree: the checkbox is the state, the chip is a
   view of it, and removing a chip unchecks the box it came from.

   The row ships `hidden` and stays out of the layout until something is
   selected — an always-present "no filters" strip is furniture that says
   nothing.
   ============================================================ */
(function () {
  'use strict';

  var bar = document.querySelector('.filterbar');
  var wrap = document.getElementById('srp-chips');
  if (!bar || !wrap) return;

  var row = wrap.querySelector('.chips__row');
  var clearAll = wrap.querySelector('.chips__clear');
  var boxes = [].slice.call(bar.querySelectorAll('.fopt input[type="checkbox"]'));
  if (!boxes.length) return;

  function label(box) {
    var n = box.closest('.fopt').querySelector('.fopt__name');
    return n ? n.textContent.trim() : box.value;
  }

  function render() {
    var on = boxes.filter(function (b) { return b.checked; });
    wrap.hidden = on.length === 0;
    row.textContent = '';
    on.forEach(function (b) {
      var li = document.createElement('li');
      var chip = document.createElement('button');
      chip.type = 'button';
      chip.className = 'chip';
      chip.setAttribute('aria-label', 'Remove filter ' + label(b));
      chip.innerHTML = '<span>' + label(b) + '</span>' +
        '<svg class="chip__x" width="9" height="9" viewBox="0 0 9 9" fill="none" aria-hidden="true">' +
        '<path d="m1 1 7 7M8 1 1 8" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>';
      chip.addEventListener('click', function () {
        b.checked = false;
        render();
        b.focus();
      });
      li.appendChild(chip);
      row.appendChild(li);
    });
  }

  boxes.forEach(function (b) { b.addEventListener('change', render); });

  clearAll.addEventListener('click', function () {
    boxes.forEach(function (b) { b.checked = false; });
    render();
    var first = bar.querySelector('.fpill__trigger');
    if (first) first.focus();
  });

  /* Clear inside a panel only clears that panel. */
  [].slice.call(bar.querySelectorAll('.fpill__clear')).forEach(function (btn) {
    btn.addEventListener('click', function () {
      var pill = btn.closest('.fpill');
      [].slice.call(pill.querySelectorAll('input[type="checkbox"]'))
        .forEach(function (b) { b.checked = false; });
      render();
    });
  });

  /* ---- and the list actually filters ----
     There is no Apply, so the change IS the action. The predicates read
     each card off the DOM once — make, body, year and price are all in
     the markup — and every band below is the same one the panels offer,
     so a label and its filter cannot drift apart. */
  var cells = [].slice.call(document.querySelectorAll('.veh-cell'));
  var count = document.querySelector('.page-head__count');
  /* Everything after the LAST 'of'. A leading regex re-read its own
     output once the count had been rewritten, and the label grew a
     second '24 of' every time. Splitting from the end cannot. */
  /* Everything after the LAST 'of'. A leading regex re-read its own
     output once the count had been rewritten, so the label grew a second
     '24 of' on every pass. Splitting from the end cannot. */
  var countTotal = count ? count.textContent.trim().split(/\s+of\s+/).pop() : '';

  var data = cells.map(function (c) {
    var txt = function (sel) { var e = c.querySelector(sel); return e ? e.textContent.trim() : ''; };
    var name = txt('.veh__name');
    var pe = c.querySelector('.veh__pill--price');
    var price = pe ? Number(pe.textContent.replace(/[^0-9]/g, '')) : 0;
    var pills = [].slice.call(c.querySelectorAll('.veh__pill'));
    var body = pills.length ? pills[pills.length - 1].textContent.trim() : '';
    return { cell: c, make: txt('.veh__make'), body: body,
             year: Number((name.match(/^(d{4})/) || [0, 0])[1]), price: price };
  });

  var YEAR = {
    '2024 and newer': function (y) { return y >= 2024; },
    '2020 – 2023': function (y) { return y >= 2020 && y <= 2023; },
    '2015 – 2019': function (y) { return y >= 2015 && y <= 2019; },
    'Before 2015': function (y) { return y > 0 && y < 2015; }
  };
  var PRICE = {
    'Under $250,000': function (v) { return v < 250000; },
    '$250,000 – $500,000': function (v) { return v >= 250000 && v < 500000; },
    '$500,000 – $750,000': function (v) { return v >= 500000 && v < 750000; },
    '$750,000 and above': function (v) { return v >= 750000; }
  };

  function chosen(pillId) {
    var pill = document.getElementById(pillId);
    if (!pill) return [];
    return [].slice.call(pill.querySelectorAll('input:checked')).map(function (bx) {
      var n = bx.closest('.fopt').querySelector('.fopt__name');
      return n ? n.textContent.trim() : bx.value;
    });
  }

  function apply() {
    var mk = chosen('f-make'), bd = chosen('f-body'),
        yr = chosen('f-year'), pr = chosen('f-price');
    var shown = 0;
    data.forEach(function (d) {
      var ok = (!mk.length || mk.indexOf(d.make) > -1)
            && (!bd.length || bd.indexOf(d.body) > -1)
            && (!yr.length || yr.some(function (k) { return YEAR[k] && YEAR[k](d.year); }))
            && (!pr.length || pr.some(function (k) { return PRICE[k] && PRICE[k](d.price); }));
      d.cell.hidden = !ok;
      if (ok) shown++;
    });
    if (count) count.innerHTML = '<b>' + shown + '</b> of ' + countTotal;
  }

  boxes.forEach(function (bx) { bx.addEventListener('change', apply); });
  clearAll.addEventListener('click', apply);
  [].slice.call(bar.querySelectorAll('.fpill__clear')).forEach(function (btn) {
    btn.addEventListener('click', apply);
  });

  render();
  apply();
})();

/* ============================================================
   ONE FILTER PANEL AT A TIME
   ============================================================
   <details> has no idea its siblings exist, so every panel opened stayed
   open: four overlapping cards, the ones behind unreachable, and nothing
   closed them but clicking the trigger again.

   Opening one closes the others. Clicking outside the row closes all of
   them. Escape closes and returns focus to the trigger it came from,
   which is the same contract the nav dropdowns already keep.
   ============================================================ */
(function () {
  'use strict';

  var bar = document.querySelector('.filterbar');
  if (!bar) return;

  var pills = [].slice.call(bar.querySelectorAll('.fpill'));
  if (!pills.length) return;

  pills.forEach(function (d) {
    d.addEventListener('toggle', function () {
      if (!d.open) return;
      pills.forEach(function (o) { if (o !== d) o.open = false; });
    });
  });

  document.addEventListener('click', function (e) {
    if (bar.contains(e.target)) return;
    pills.forEach(function (d) { d.open = false; });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var open = pills.filter(function (d) { return d.open; })[0];
    if (!open) return;
    open.open = false;
    var t = open.querySelector('.fpill__trigger');
    if (t) t.focus();
  });
})();

/* ============================================================
   THE MARQUE STRIP IS THE MAKE FILTER, SAID SHORTER
   ============================================================
   Seven marques, the same seven the Make panel holds, with the same
   counts — so leaving them as decoration would be a row that looks like
   a control and is not one. Pressing a marque ticks its checkbox, which
   is the single source of state: the panel, the chips and the strip all
   read from it and therefore cannot disagree.
   ============================================================ */
(function () {
  'use strict';

  var strip = document.querySelector('.brands');
  var makePill = document.getElementById('f-make');
  if (!strip || !makePill) return;

  var boxes = [].slice.call(makePill.querySelectorAll('.fopt'));

  function boxFor(name) {
    var hit = boxes.filter(function (o) {
      var n = o.querySelector('.fopt__name');
      return n && n.textContent.trim() === name;
    })[0];
    return hit ? hit.querySelector('input') : null;
  }

  [].slice.call(strip.querySelectorAll('.brand')).forEach(function (btn) {
    var name = (btn.childNodes[0].textContent || '').trim();
    var box = boxFor(name);
    if (!box) return;
    btn.setAttribute('aria-pressed', String(box.checked));
    btn.addEventListener('click', function () {
      box.checked = !box.checked;
      box.dispatchEvent(new Event('change', { bubbles: true }));
    });
    box.addEventListener('change', function () {
      btn.setAttribute('aria-pressed', String(box.checked));
    });
  });
})();

/* ============================================================
   DETAILED SEARCH — the same filters, opened together
   ============================================================
   It was a link to the live site: the one control promising MORE
   filtering was the one that left the page. It now opens all four groups
   at once, against the same checkboxes — no second set of inputs, so the
   sheet and the pills cannot disagree.

   The exclusive-panel rule is suspended while it is open, because four
   panels side by side is the whole point of the mode; it resumes on
   close, where overlapping dropdowns would be a defect again.
   ============================================================ */
(function () {
  'use strict';

  var bar = document.querySelector('.filterbar');
  var btn = document.querySelector('.filterbar__all');
  if (!bar || !btn) return;

  var pills = [].slice.call(bar.querySelectorAll('.fpill'));
  var label = btn.childNodes[0];

  btn.addEventListener('click', function () {
    var on = btn.getAttribute('aria-expanded') === 'true';
    btn.setAttribute('aria-expanded', String(!on));
    bar.classList.toggle('is-detailed', !on);
    pills.forEach(function (d) { d.open = !on; });
    if (label) label.textContent = on ? 'Detailed search ' : 'Fewer filters ';
  });

  /* Reset all clears every box in the sheet. Show N closes it — the
     filtering already happened on each change, so this button confirms
     nothing; it is the way OUT of the sheet, and its number is the
     result you are about to look at. */
  var reset = bar.querySelector('.filterbar__reset');
  var show  = bar.querySelector('.filterbar__show');
  var count = document.querySelector('.page-head__count');

  if (reset) {
    reset.addEventListener('click', function () {
      [].slice.call(bar.querySelectorAll('input[type="checkbox"]')).forEach(function (b) {
        if (!b.checked) return;
        b.checked = false;
        b.dispatchEvent(new Event('change', { bubbles: true }));
      });
    });
  }

  if (show) {
    show.addEventListener('click', function () { btn.click(); });
    /* The number tracks the list, read off the count the page already
       maintains rather than recomputed from a second source. */
    var sync = function () {
      if (!count) return;
      var n = (count.textContent.match(/d+/) || ['0'])[0];
      var b = show.querySelector('b');
      if (b) b.textContent = n;
    };
    bar.addEventListener('change', function () { setTimeout(sync, 0); });
    sync();
  }
})();

/* ============================================================
   PAGING A CARD'S PHOTOGRAPHS
   ============================================================
   Simulated for the preview: only the Viper cards carry a real gallery,
   the rest borrow their second and third frames from the pool. The
   behaviour is the real one, so swapping in the feed's own sets changes
   nothing here.

   The arrows sit inside the card's link area, so each one has to stop
   the click reaching it — otherwise paging a photograph would navigate
   to the vehicle. tabindex="-1" in the markup keeps twenty-four cards
   from adding forty-eight tab stops; the card itself is the keyboard
   route and it goes to the same place.
   ============================================================ */
(function () {
  'use strict';

  var cells = [].slice.call(document.querySelectorAll('.veh-cell'));
  if (!cells.length) return;

  cells.forEach(function (cell) {
    var frames = [].slice.call(cell.querySelectorAll('.veh__frame'));
    var navs = [].slice.call(cell.querySelectorAll('.veh__nav'));
    if (frames.length < 2) {
      navs.forEach(function (b) { b.remove(); });   /* nothing to page */
      return;
    }

    var at = 0;
    function show(i) {
      at = (i + frames.length) % frames.length;
      frames.forEach(function (f, n) { f.classList.toggle('is-on', n === at); });
    }

    navs.forEach(function (btn) {
      var step = btn.classList.contains('veh__nav--prev') ? -1 : 1;
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        show(at + step);
      });
    });
  });
})();

/* ============================================================
   THE VDP'S VIDEO FACADE AND ITS ESTIMATOR
   ============================================================ */
(function () {
  'use strict';

  /* ---- the YouTube facade ----
     The iframe does not exist until somebody asks for it. Loading it up
     front is about a megabyte of third-party script and a set of cookies
     dropped before anyone wanted a video. */
  var ytb = document.querySelector('.ytb');
  if (ytb) {
    var load = function () {
      if (ytb.querySelector('iframe')) return;
      var f = document.createElement('iframe');
      f.src = ytb.getAttribute('data-yt');
      f.title = 'Chicago Motor Cars on YouTube';
      f.allow = 'accelerometer; autoplay; encrypted-media; picture-in-picture';
      f.setAttribute('allowfullscreen', '');
      ytb.appendChild(f);
    };
    var play = ytb.querySelector('.ytb__play');
    if (play) play.addEventListener('click', load);

    /* The call on the photograph opens the panel and starts the film in
       one move — a control labelled "Watch video" that only scrolls you
       to a closed drawer has not done what it said. */
    var call = document.querySelector('[data-open-video]');
    var panel = ytb.closest('details');
    if (call && panel) {
      call.addEventListener('click', function () {
        panel.open = true;
        panel.scrollIntoView({ block: 'center',
          behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
        load();
      });
    }
  }

  /* ---- the estimator ----
     Standard amortisation on the three values the reader sets. It is
     arithmetic on their own numbers, not a quote, and the copy beside it
     says so. A zero rate is handled separately because the formula
     divides by it. */
  var calc = document.querySelector('.calc');
  if (!calc) return;

  var num = function (el) {
    var v = parseFloat(String(el.value).replace(/[^\d.]/g, ''));
    return isFinite(v) ? v : 0;
  };
  var price = calc.querySelector('#c-price');
  var down = calc.querySelector('#c-down');
  var term = calc.querySelector('#c-term');
  var apr = calc.querySelector('#c-apr');
  var out = calc.querySelector('#c-monthly');

  function run() {
    var principal = Math.max(0, num(price) - num(down));
    var n = parseInt(term.value, 10) || 60;
    var r = num(apr) / 100 / 12;
    var m = r > 0
      ? principal * r / (1 - Math.pow(1 + r, -n))
      : principal / n;
    out.textContent = (principal > 0 && isFinite(m))
      ? '$' + Math.round(m).toLocaleString('en-US') + ' / mo'
      : '—';
  }

  ['input', 'change'].forEach(function (ev) {
    calc.addEventListener(ev, run);
  });
  run();
})();

/* ============================================================
   THE RELATED ROW'S DOTS
   ============================================================
   The reviews chapter's module in miniature: the dots are built from
   how many cards actually fit a row, so a three-across grid that
   becomes one-across on a phone gets three dots instead of one. Built
   by script and nothing is hidden without it — no script, no dots, and
   the grid is still a grid.
   ============================================================ */
(function () {
  'use strict';
  var track = document.querySelector('[data-rel-track]');
  var wrap = document.querySelector('[data-rel-dots]');
  if (!track || !wrap) return;

  var cards = [].slice.call(track.children);
  if (cards.length < 2) return;

  /* HOW MANY FIT, not how many share a top edge. The first version
     counted cards on the same visual row, which was right for a grid
     and wrong the moment this became a horizontal track — there every
     card shares a top, so it counted all six and concluded there was
     one page. Track width over card width is the question either way. */
  function perRow() {
    var w = track.clientWidth;
    var cw = cards[0].getBoundingClientRect().width;
    var gap = parseFloat(getComputedStyle(track).columnGap) || 0;
    if (!cw) return 1;
    return Math.max(1, Math.round((w + gap) / (cw + gap)));
  }

  function build() {
    var pages = Math.ceil(cards.length / perRow());
    wrap.textContent = '';
    if (pages < 2) return;
    for (var i = 0; i < pages; i++) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'rel__dot';
      b.setAttribute('aria-current', i === 0 ? 'true' : 'false');
      b.setAttribute('aria-label', 'Page ' + (i + 1) + ' of ' + pages);
      (function (idx) {
        b.addEventListener('click', function () {
          /* scrollLeft rather than scrollIntoView: the latter also scrolls
             the PAGE to bring the track into view, which yanks the
             reader somewhere they did not ask to go when they only
             wanted the next three cars. */
          var target = cards[idx * perRow()];
          if (target) track.scrollLeft = target.offsetLeft - cards[0].offsetLeft;
          [].forEach.call(wrap.children, function (d, n) {
            d.setAttribute('aria-current', n === idx ? 'true' : 'false');
          });
        });
      })(i);
      wrap.appendChild(b);
    }
  }

  /* A swipe or a trackpad scroll moves the track without touching the
     dots, so the dots have to follow the track rather than own it. */
  function sync() {
    var n = perRow();
    var page = Math.round(track.scrollLeft / ((cards[0].getBoundingClientRect().width +
      (parseFloat(getComputedStyle(track).columnGap) || 0)) * n));
    [].forEach.call(wrap.children, function (d, i) {
      d.setAttribute('aria-current', i === page ? 'true' : 'false');
    });
  }

  build();
  var s;
  track.addEventListener('scroll', function () { clearTimeout(s); s = setTimeout(sync, 90); });
  var t;
  window.addEventListener('resize', function () { clearTimeout(t); t = setTimeout(build, 150); });
})();

/* ============================================================
   SAVE · SHARE · TEXT TO PHONE
   ============================================================
   The three page-furniture controls above the vehicle. None of them
   talks to a server: Save is local, Share and Text both hand the
   browser a link and step out of the way.
   ============================================================ */
(function () {
  'use strict';
  var bar = document.querySelector('.topbar__tools');
  if (!bar) return;

  var url = location.href.split('?')[0];
  var title = (document.querySelector('h1') || {}).textContent || document.title;
  title = title.replace(/\s+/g, ' ').trim();

  /* ---- text to phone ----
     The href carries the listing so a phone opens its composer already
     written and the reader picks the recipient — usually themselves.
     Nobody's number is asked for or stored.

     On a desktop an sms: link is a control that silently does nothing,
     so there it copies instead and says so. Detected by pointer, not by
     user-agent string. */
  var textLink = bar.querySelector('[data-text-to-phone]');
  if (textLink) {
    var body = title + ' — ' + url;
    textLink.setAttribute('href', 'sms:?&body=' + encodeURIComponent(body));
    var coarse = window.matchMedia('(hover: none) and (pointer: coarse)').matches;
    if (!coarse) {
      textLink.addEventListener('click', function (e) {
        e.preventDefault();
        copy(body, textLink, 'Link copied');
      });
    }
  }

  /* ---- share ---- */
  var shareBtn = bar.querySelector('[data-share]');
  if (shareBtn) {
    shareBtn.addEventListener('click', function () {
      if (navigator.share) {
        navigator.share({ title: title, url: url }).catch(function () {});
        return;
      }
      copy(url, shareBtn, 'Link copied');
    });
  }

  function copy(text, el, msg) {
    var done = function () {
      var label = el.lastChild;
      var was = label.nodeValue;
      label.nodeValue = ' ' + msg;
      setTimeout(function () { label.nodeValue = was; }, 1600);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () {});
      return;
    }
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); done(); } catch (err) {}
    document.body.removeChild(ta);
  }

  /* ---- save ----
     Local only, and it survives a reload, which is the whole point of a
     save mark. The garage counter in the masthead is another module's
     business; this one just remembers. */
  var saveBtn = bar.querySelector('[data-save]');
  if (saveBtn) {
    var key = 'cmc-saved';
    var id = saveBtn.getAttribute('data-save');
    var read = function () {
      try { return JSON.parse(localStorage.getItem(key)) || []; } catch (e) { return []; }
    };
    var set = function (on) { saveBtn.setAttribute('aria-pressed', on ? 'true' : 'false'); };
    set(read().indexOf(id) > -1);
    saveBtn.addEventListener('click', function () {
      var list = read();
      var at = list.indexOf(id);
      if (at > -1) list.splice(at, 1); else list.push(id);
      try { localStorage.setItem(key, JSON.stringify(list)); } catch (e) {}
      set(list.indexOf(id) > -1);
    });
  }
})();

/* ============================================================
   THE VDP'S SHIPPING ESTIMATE, AND OPENING A PANEL FROM A LINK
   ============================================================ */
(function () {
  'use strict';

  /* ---- an anchor that opens what it points at ----
     <details> does not open because you linked to it, so a link to a
     closed panel scrolls to a heading and appears to do nothing. This
     opens the target, then scrolls — and it also handles a page loaded
     with #shipping already in the URL, which is how a link from another
     page would arrive. */
  function openPanel(hash) {
    if (!hash || hash.length < 2) return null;
    var el;
    try { el = document.querySelector(hash); } catch (e) { return null; }
    if (!el) return null;
    var d = el.closest ? (el.matches('details') ? el : el.closest('details')) : null;
    if (d) d.open = true;
    return el;
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    if (!a) return;
    var el = openPanel(a.getAttribute('href'));
    if (!el) return;
    e.preventDefault();
    history.replaceState(null, '', a.getAttribute('href'));
    el.scrollIntoView({ block: 'start',
      behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  });

  if (location.hash) {
    var t = openPanel(location.hash);
    if (t) setTimeout(function () { t.scrollIntoView({ block: 'start' }); }, 60);
  }

  /* ---- the shipping estimate ----
     THE TWO CONSTANTS BELOW ARE PLACEHOLDERS. CMC's carrier pricing is
     not something I have, and inventing a per-mile figure on a $900k
     car is exactly the number somebody quotes back at you. They are
     named, they are at the top, and the page says on screen that the
     result is an estimate — so replacing them with the real rates is
     editing two numbers, not rebuilding anything.

     Distance is approximated from the first digit of the ZIP, which is
     how the US postal regions are laid out west-to-east. It is a band,
     not a route, and the copy does not pretend otherwise. */
  var BASE = 450;          // pickup, loading, admin
  var PER_100_MILES = 78;  // enclosed transport

  var form = document.querySelector('.ship');
  if (!form) return;

  // rough road miles from Naperville (ZIP region 6) to each ZIP region
  var MILES_BY_REGION = { 0: 900, 1: 800, 2: 750, 3: 900, 4: 350,
                          5: 400, 6: 150, 7: 900, 8: 1300, 9: 2000 };

  var to = form.querySelector('#s-to');
  var type = form.querySelector('#s-type');
  var out = form.querySelector('#s-cost');

  function run() {
    var z = (to.value || '').replace(/\D/g, '');
    if (z.length < 5) { out.textContent = '—'; return; }
    var miles = MILES_BY_REGION[z[0]];
    if (miles === undefined) { out.textContent = '—'; return; }
    var cost = BASE + (miles / 100) * PER_100_MILES;
    if (type.value === 'open') cost *= 0.72;
    var lo = Math.round(cost * 0.9 / 25) * 25;
    var hi = Math.round(cost * 1.1 / 25) * 25;
    out.textContent = '$' + lo.toLocaleString('en-US') + ' – $' + hi.toLocaleString('en-US');
  }

  ['input', 'change'].forEach(function (ev) { form.addEventListener(ev, run); });
  form.addEventListener('submit', function (e) { e.preventDefault(); run(); });
  run();
})();


/* ============================================================
   A FILM BAND, BOUND TO A ROLE INSTEAD OF TO A SECTION
   ============================================================
   Same contract as the break and the service bands above: the <source>
   ships with data-src and no src, this attaches it a viewport out, and
   under prefers-reduced-motion it is never fetched at all. The poster is
   a real frame of the same subject, so a visitor who has asked for less
   movement gets a photograph rather than a black rectangle waiting for
   something.

   WHY A THIRD COPY IS NOT WHAT THIS IS. The two modules above are the
   same machine written twice, once against `.brk` and once against
   `.svc` — which is why a new page inherits neither, and inherits them
   SILENTLY: nothing errors, the film simply never plays and every check
   that asks whether something is broken passes. This one is bound to
   [data-film], so any section that declares the role gets the behaviour
   without a line of JavaScript being added for it.

   The existing two are deliberately left alone. Folding them in means
   editing index.html's markup, and index.html is the approved page; that
   is a change with its own verification and it is not this one. When
   someone next has a reason to touch them, this is the function they
   collapse into — the only difference is the selector.
   ============================================================ */
(function () {
  'use strict';

  var bands = document.querySelectorAll('[data-film]');
  if (!bands.length) return;

  var calm = window.matchMedia('(prefers-reduced-motion: reduce)');

  Array.prototype.forEach.call(bands, function (band) {
    var video  = band.querySelector('video');
    var source = band.querySelector('video source');
    if (!video || !source) return;

    var attached = false;

    function attach() {
      if (attached || calm.matches) return;
      attached = true;
      source.src = source.getAttribute('data-src');
      video.load();
    }

    function play() {
      if (calm.matches) return;
      attach();
      var p = video.play();
      /* Autoplay can be refused even when muted. If it is, the band keeps
         its poster, which is a real frame of the same room — so a refusal
         costs the movement and nothing else. */
      if (p && p.catch) p.catch(function () {});
    }

    /* HOW EARLY TO FETCH IS THE BAND'S OWN DECISION, and it has to be,
       because the right answer depends on how many films share the page.
       100% is correct for a single band far down a long page: one file,
       ready by the time you reach it. On a page of FIVE bands stacked
       one after another it prefetched three of them before the visitor
       scrolled at all — 6.3MB spent on two showrooms nobody had asked
       to see yet. Measured, not assumed: the request log showed
       west-chicago, naperville and rock-hill all on the wire at 500ms.

       So the value of data-film is the margin, and an empty attribute
       keeps the old default. A page with one film says nothing and gets
       100%; a page with five says data-film="25%" and each arrives
       about a quarter-screen ahead of itself. */
    var margin = band.getAttribute('data-film') || '100%';

    if ('IntersectionObserver' in window) {
      /* Two observers, two margins. The outer attaches the source early
         enough that the film is ready when the band arrives; the inner
         starts and stops playback, so a film left running four sections
         up is not still decoding behind the page. */
      new IntersectionObserver(function (entries) {
        entries.forEach(function (e) { if (e.isIntersecting) attach(); });
      }, { rootMargin: margin + ' 0px' }).observe(band);

      new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) play();
          else if (!video.paused) video.pause();
        });
      }, { threshold: 0.25 }).observe(band);
    } else {
      attach();
    }

    /* Turning the setting on mid-visit stops the film and leaves the
       poster. Turning it off does not start one nobody asked for. */
    var onCalm = function () { if (calm.matches) video.pause(); };
    if (calm.addEventListener) calm.addEventListener('change', onCalm);
    else if (calm.addListener) calm.addListener(onCalm);
  });
})();

/* ============================================================
   THE REACH — the shipping map's one move, played once
   ============================================================
   Arms the map (dark land, no rings) only when the move can actually
   play; otherwise the markup already is the finished map. Fires once at
   60% in view and never replays — scrolling back finds the map finished,
   not waiting to be performed again. Timing lives in geneva.css 4c. */
(function () {
  'use strict';

  var map = document.querySelector('.gmh-map');
  if (!map) return;

  var calm = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (calm.matches || !('IntersectionObserver' in window)) return;

  map.classList.add('is-armed');

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      io.disconnect();
      map.classList.add('is-go');
    });
  }, { threshold: 0.6 });

  io.observe(map);
})();

/* ============================================================
   THE HERO SUBJECT — where the navy 997 actually is on screen
   ============================================================
   gates/composition.mjs finds masses by their text, so it cannot see a
   car inside a photograph and reported the right third of the hero as
   dead air. Its contract for a subject it cannot read is window.__subject.
   This projects the declared box in the source frame (.gates/declare.json
   → hero.samples: the navy 997) through the photo's real object-fit and
   object-position — measured on every crop, never a fixed rectangle. */
(function () {
  'use strict';

  var img = document.querySelector('.gmh-hero__haus');
  if (!img) return;
  /* the PAIR — the event is two 911s with the name between them; measured
     off the source frame: grey 997 0.048–0.452, navy 997 0.652–0.973 */
  var BOX = { x: 0.048, y: 0.372, w: 0.927, h: 0.3 };

  function project() {
    if (!img.naturalWidth) return;
    var r = img.getBoundingClientRect();
    var s = Math.max(r.width / img.naturalWidth, r.height / img.naturalHeight);
    var w = img.naturalWidth * s, h = img.naturalHeight * s;
    var pos = getComputedStyle(img).objectPosition.split(' ');
    var px = parseFloat(pos[0]) / 100, py = parseFloat(pos[1] || pos[0]) / 100;
    var ox = r.left + (r.width - w) * px, oy = r.top + (r.height - h) * py;
    window.__subject = {
      label: 'the two 911s (hero photograph)',
      left: ox + BOX.x * w, top: oy + BOX.y * h,
      right: ox + (BOX.x + BOX.w) * w, bottom: oy + (BOX.y + BOX.h) * h
    };
  }

  // v2 (index.html) wraps the frame in .hero__media, v3 (index2.html) in .gmh-hero__media
  var media = img.closest('.gmh-hero__media, .hero__media');
  if (media) media.setAttribute('data-mass', 'stage');
  if (img.complete) project(); else img.addEventListener('load', project);
  window.addEventListener('resize', project);
})();

/* ============================================================
   THE SELL PILL — the live site's floating "Sell your car"
   ============================================================
   The markup ships it visible, so a failed script still leaves the
   action on screen. This only stands it down where it would repeat
   what is already in view — the hero (which carries the name and its
   own doors), the v3 catalogue .gmh-cat (where it covered the index),
   the Sell chapter itself, Contact (where it covered the
   hours and the map) and the footer — so it is never
   a second overlay over the one thing that answers it (U10). */
(function () {
  'use strict';

  var pill = document.querySelector('.gmh-float');
  if (!pill || !('IntersectionObserver' in window)) return;

  var quiet = [].slice.call(document.querySelectorAll('.gmh-hero, .gmh-cat, #sell, .sell-band, #contact, .foot'));
  var seen = new Map();

  function update() {
    var any = false;
    seen.forEach(function (v) { if (v) any = true; });
    if (any) pill.setAttribute('data-hidden', ''); else pill.removeAttribute('data-hidden');
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { seen.set(e.target, e.isIntersecting); });
    update();
  }, { threshold: 0.2 });

  quiet.forEach(function (q) { seen.set(q, false); io.observe(q); });
})();

/* ============================================================
   THE MAP, ON REQUEST — the live site's own Google embed
   ============================================================
   The door photograph holds the place; a click puts the map there and
   moves focus into it. Without JS the same element is a link to the
   address on Google Maps. See geneva.css 15k for why it waits. */
(function () {
  'use strict';

  var box = document.querySelector('.gmh-door__map[data-embed]');
  if (!box) return;
  var go = box.querySelector('.gmh-door__map-go');
  if (!go) return;

  go.addEventListener('click', function (e) {
    e.preventDefault();
    var f = document.createElement('iframe');
    f.title = 'Map of 600 Faust Rd, Unit 8, Burlington, WI 53105';
    f.src = box.getAttribute('data-embed');
    f.referrerPolicy = 'no-referrer-when-downgrade';
    f.setAttribute('tabindex', '0');
    box.classList.add('is-live');
    box.replaceChildren(f);
    f.focus();
  });
})();
