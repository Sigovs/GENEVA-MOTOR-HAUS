/* ============================================================
   GENEVA MOTOR HAUS — sell-v2.js — the sell-your-car page
   ============================================================
   finance-v2.js runs the form (the panel, send, clear). This adds:

   · THE PHOTOGRAPH DROP — AAN's uploader, held in the page: pick or drag
     files, up to twelve, JPG/PNG/GIF/PDF/DOC as AAN allows; each shows as a
     thumbnail with its own remove button. The list lives on the file input
     itself, so the form's own data carries it. Nothing is uploaded: a
     static preview has nowhere to send it.
   · THE CAR LINE in the panel — year, make and model as they are typed.

   Without this file the file input is a plain multiple-file field.
   ============================================================ */
(function () {
  'use strict';

  var form = document.getElementById('fin-form');
  if (!form) return;

  /* ---- the car line ---- */
  var carLine = document.querySelector('[data-car]');
  var year = form.elements.year, make = form.elements.make, model = form.elements.model;
  function syncCar() {
    if (!carLine) return;
    var m = make && make.value ? make.options[make.selectedIndex].text : '';
    var text = [year && year.value, m, model && model.value.trim()].filter(Boolean).join(' ');
    carLine.textContent = text || 'Year, make and model';
    carLine.classList.toggle('is-set', !!text);
  }
  [year, make, model].forEach(function (el) { if (el) { el.addEventListener('input', syncCar); el.addEventListener('change', syncCar); } });

  /* ---- the photograph drop ---- */
  var input = document.getElementById('f-uploader');
  var drop = document.querySelector('.sl-drop');
  var list = document.querySelector('[data-thumbs]');
  var msg = document.querySelector('[data-drop-msg]');
  var MAX = 12;
  var OK = /\.(jpe?g|png|gif|pdf|doc)$/i;
  var X = '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true"><path d="M2.5 2.5l7 7M9.5 2.5l-7 7" stroke="currentColor" stroke-width="1.6"/></svg>';
  var files = [];
  var syncing = false;
  var canHold = input && typeof DataTransfer === 'function';

  function same(a, b) { return a.name === b.name && a.size === b.size && a.lastModified === b.lastModified; }

  function render() {
    list.textContent = '';
    files.forEach(function (f, k) {
      var li = document.createElement('li');
      li.className = 'sl-thumb';
      if (/^image\//.test(f.type)) {
        var img = document.createElement('img');
        img.alt = '';
        img.src = URL.createObjectURL(f);
        img.onload = function () { URL.revokeObjectURL(img.src); };
        li.appendChild(img);
      } else {
        var doc = document.createElement('span');
        doc.className = 'sl-thumb__doc';
        doc.textContent = (f.name.split('.').pop() || 'file').toUpperCase();
        li.appendChild(doc);
      }
      var x = document.createElement('button');
      x.type = 'button';
      x.className = 'sl-thumb__x';
      x.setAttribute('aria-label', 'Remove ' + f.name);
      x.innerHTML = X;
      x.addEventListener('click', function () {
        files.splice(k, 1);
        hold();
        say(files.length ? files.length + ' of ' + MAX + ' attached.' : '');
        var next = list.querySelectorAll('.sl-thumb__x')[Math.min(k, files.length - 1)];
        (next || input).focus();
      });
      li.appendChild(x);
      list.appendChild(li);
    });
    list.hidden = !files.length;
  }

  function hold() {
    syncing = true;
    var dt = new DataTransfer();
    files.forEach(function (f) { dt.items.add(f); });
    input.files = dt.files;
    render();
    input.dispatchEvent(new Event('change', { bubbles: true }));   // the panel counts it
    syncing = false;
  }

  function say(text) { if (msg) msg.textContent = text; }

  function add(picked) {
    var bad = [], over = false;
    [].slice.call(picked).forEach(function (f) {
      if (!OK.test(f.name)) { bad.push(f.name); return; }
      if (files.some(function (g) { return same(f, g); })) return;
      if (files.length >= MAX) { over = true; return; }
      files.push(f);
    });
    hold();
    say(over ? 'Only ' + MAX + ' files allowed. ' + files.length + ' attached.'
      : bad.length ? bad.join(', ') + (bad.length > 1 ? ' aren’t' : ' isn’t') + ' a JPG, PNG, GIF, PDF or DOC file.'
      : files.length + ' of ' + MAX + ' attached.');
  }

  if (canHold && drop && list) {
    input.addEventListener('change', function () { if (!syncing) add(input.files); });
    ['dragenter', 'dragover'].forEach(function (t) {
      drop.addEventListener(t, function (ev) { ev.preventDefault(); drop.classList.add('is-over'); });
    });
    ['dragleave', 'drop'].forEach(function (t) {
      drop.addEventListener(t, function (ev) { ev.preventDefault(); drop.classList.remove('is-over'); });
    });
    drop.addEventListener('drop', function (ev) { if (ev.dataTransfer && ev.dataTransfer.files.length) add(ev.dataTransfer.files); });
    form.addEventListener('reset', function () { files = []; list.textContent = ''; list.hidden = true; say(''); });
  }
  form.addEventListener('reset', function () { setTimeout(syncCar, 0); });

  syncCar();
})();
