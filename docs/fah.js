(function () {
  var root = document.querySelector('.fah');
  if (!root || root.getAttribute('data-fah-ready')) return;
  root.setAttribute('data-fah-ready', '1');
  root.classList.add('is-js');
  var cfg = {};
  try { cfg = JSON.parse(root.getAttribute('data-fah')) || {}; } catch (err) { cfg = {}; }
  var $ = function (sel, el) { return (el || root).querySelector(sel); };
  var $$ = function (sel, el) { return Array.prototype.slice.call((el || root).querySelectorAll(sel)); };
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- header ---------- */
  var header = $('.fah-header');
  var hero = $('.fah-hero');
  var lastY = window.scrollY;
  function onScrollHeader() {
    var y = window.scrollY;
    header.classList.toggle('is-solid', y > 40);
    header.classList.toggle('is-hidden', y > 500 && y > lastY + 4 && !header.classList.contains('is-menu'));
    if (y < lastY - 4) header.classList.remove('is-hidden');
    lastY = y;
  }
  window.addEventListener('scroll', onScrollHeader, { passive: true });
  onScrollHeader();

  var burger = $('.fah-burger');
  var menu = $('.fah-menu');
  function setMenu(open) {
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    menu.classList.toggle('is-open', open);
    header.classList.toggle('is-menu', open);
    document.documentElement.style.overflow = open ? 'hidden' : '';
  }
  burger.addEventListener('click', function () { setMenu(burger.getAttribute('aria-expanded') !== 'true'); });
  menu.addEventListener('click', function (ev) { if (ev.target.closest('a')) setMenu(false); });

  /* ---------- sky: Bangkok time, draggable sun ---------- */
  var KEYS = [
    [0, '#060F1E', '#0E2140', '#1B3358'], [4.8, '#0C1830', '#23335C', '#5A5584'], [6, '#3E5F98', '#C98E98', '#F4C49E'],
    [7.2, '#5E9BD4', '#A8CBEA', '#F3E1C6'], [12, '#3F86CC', '#86BCE8', '#D5E9F7'], [16.5, '#4C86C2', '#A7C4DF', '#F1DDBE'],
    [18.2, '#2D3D78', '#C0627A', '#F2A65A'], [19.3, '#141E44', '#3B3A6E', '#9A5C7A'], [20.5, '#081427', '#10264A', '#1F3A60'],
    [24, '#060F1E', '#0E2140', '#1B3358']
  ];
  function hex(h) { return [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)]; }
  function mix(a, b, t) { var x = hex(a), y = hex(b); return 'rgb(' + [0, 1, 2].map(function (i) { return Math.round(x[i] + (y[i] - x[i]) * t); }).join(',') + ')'; }
  function lum(rgb) { var p = rgb.match(/\d+/g).map(Number); return (0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]) / 255; }
  function phaseOf(h) { return h < 5.3 || h >= 19.6 ? 'night' : h < 7 ? 'dawn' : h < 17.6 ? 'day' : 'dusk'; }
  function bangkokHours() { var d = new Date(); return ((d.getUTCHours() + 7) % 24) + d.getUTCMinutes() / 60; }
  var dial = $('.fah-dial__range');
  var timeOut = $('.fah-dial__time');
  var phaseOut = $('.fah-dial__phase');
  var nowBtn = $('.fah-dial__now');
  var phases = {};
  try { phases = JSON.parse(root.getAttribute('data-phases') || '{}'); } catch (err) { phases = {}; }
  function setSky(h, live) {
    var i = 0;
    while (i < KEYS.length - 2 && h >= KEYS[i + 1][0]) i++;
    var a = KEYS[i], b = KEYS[i + 1], t = (h - a[0]) / (b[0] - a[0]);
    var c1 = mix(a[1], b[1], t), c2 = mix(a[2], b[2], t), c3 = mix(a[3], b[3], t);
    var light = (lum(c1) + lum(c2)) / 2 > 0.55;
    var s = hero.style;
    s.setProperty('--sky1', c1); s.setProperty('--sky2', c2); s.setProperty('--sky3', c3);
    var day = h >= 6 && h < 18.6;
    var p = day ? (h - 6) / 12.6 : ((h >= 18.6 ? h - 18.6 : h + 5.4) / 11.4);
    var x = 8 + p * 84, y = 62 - Math.sin(p * Math.PI) * 50;
    s.setProperty('--sun-x', x + '%'); s.setProperty('--sun-y', y + '%');
    var sunEl = $('.fah-sun'), textBox = $('.fah-hero__text');
    if (sunEl && textBox && window.innerWidth > 900) {
      var hr = hero.getBoundingClientRect(), tr = textBox.getBoundingClientRect();
      var cx = hr.width * x / 100, cy = hr.height * y / 100, pad = 40;
      sunEl.classList.toggle('is-behind', cx > tr.left - hr.left - pad && cx < tr.right - hr.left + pad &&
        cy > tr.top - hr.top - pad && cy < tr.bottom - hr.top + pad);
    } else if (sunEl) sunEl.classList.remove('is-behind');
    s.setProperty('--sun-c', day ? (h < 7.5 || h > 17 ? '#FFC98A' : '#FFF4D6') : '#E9EEF6');
    s.setProperty('--sun-glow', day ? 'rgba(255,214,150,.45)' : 'rgba(233,238,246,.25)');
    s.setProperty('--sun-glow2', day ? 'rgba(255,214,150,.18)' : 'rgba(233,238,246,.08)');
    s.setProperty('--sun-s', day ? '54px' : '34px');
    var night = h < 5.6 || h >= 19.2 ? 1 : h < 6.6 ? (6.6 - h) : h > 18.2 ? (h - 18.2) : 0;
    s.setProperty('--stars', String(Math.min(1, night)));
    s.setProperty('--lights', String(Math.max(0.12, Math.min(1, night * 1.2 + (h > 17.4 && h < 19.2 ? 0.5 : 0)))));
    s.setProperty('--city', light ? 'rgba(16,40,67,.88)' : mix('#040A15', a[1], 0.25));
    var fg = light ? '#102843' : '#F7F4EE';
    s.setProperty('--hero-fg', fg);
    header.style.setProperty('--hero-fg', fg);
    hero.setAttribute('data-phase', phaseOf(h));
    hero.setAttribute('data-fg', light ? 'dark' : 'light');
    var hh = Math.floor(h), mm = Math.round((h - hh) * 60);
    if (mm === 60) { hh = (hh + 1) % 24; mm = 0; }
    timeOut.textContent = (hh < 10 ? '0' : '') + hh + ':' + (mm < 10 ? '0' : '') + mm;
    phaseOut.textContent = (phases[phaseOf(h)] || phaseOf(h)) + (live ? ' · ' + (phases.now || 'now') : '');
    nowBtn.hidden = !!live;
  }
  var live = true;
  function tick() { if (live) { var h = bangkokHours(); dial.value = h; setSky(h, true); } }
  tick();
  setInterval(tick, 60000);
  dial.addEventListener('input', function () { live = false; hero.classList.add('is-dragging'); setSky(parseFloat(dial.value), false); });
  dial.addEventListener('change', function () { hero.classList.remove('is-dragging'); });
  nowBtn.addEventListener('click', function () { live = true; tick(); });
  window.addEventListener('resize', function () { setSky(parseFloat(dial.value), live); });

  /* hero slideshow */
  var slides = $$('.fah-arch__slide');
  var si = 0;
  if (slides.length > 1 && !reduce) {
    setInterval(function () {
      if (document.hidden) return;
      slides[si].classList.remove('is-on');
      si = (si + 1) % slides.length;
      slides[si].classList.add('is-on');
    }, 5200);
  }

  /* ---------- booking widget ---------- */
  function iso(d) { return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2); }
  function addDays(s, n) { var d = new Date(s + 'T12:00:00'); d.setDate(d.getDate() + n); return iso(d); }
  function nightsBetween(a, b) { return Math.round((new Date(b + 'T12:00:00') - new Date(a + 'T12:00:00')) / 864e5); }
  function nightsWord(n) {
    var f = cfg.nights || ['night', 'nights'];
    if (f.length === 3) { var m = n % 100, k = n % 10; return m > 10 && m < 20 ? f[2] : k === 1 ? f[0] : k > 1 && k < 5 ? f[1] : f[2]; }
    return n === 1 ? f[0] : f[1];
  }
  var today = iso(new Date());
  var bform = $('[data-fah-booking]');
  var bin = bform.elements.checkin, bout = bform.elements.checkout, nightsOut = $('.fah-booking__nights');
  bin.min = today; bin.value = today; bout.min = addDays(today, 1); bout.value = addDays(today, 1);
  function syncNights() {
    if (bout.value <= bin.value) bout.value = addDays(bin.value, 1);
    bout.min = addDays(bin.value, 1);
    var n = nightsBetween(bin.value, bout.value);
    nightsOut.textContent = n > 0 ? n + ' ' + nightsWord(n) : '';
  }
  bin.addEventListener('change', syncNights);
  bout.addEventListener('change', syncNights);
  syncNights();
  var reqForm = $('[data-fah-request]');
  function toRequest(data) {
    if (data) {
      ['checkin', 'checkout', 'guests'].forEach(function (k) { if (data[k] && reqForm.elements[k]) reqForm.elements[k].value = data[k]; });
    }
    $('#fah-request').scrollIntoView({ behavior: reduce ? 'auto' : 'smooth' });
    setTimeout(function () { reqForm.elements.name.focus({ preventScroll: true }); }, 700);
  }
  function barData() {
    return { checkin: bin.value, checkout: bout.value, guests: bform.elements.guests.value,
      nights: String(Math.max(1, nightsBetween(bin.value, bout.value))) };
  }
  function withDates(url, data) {
    var p = cfg.params || {}, q = [];
    Object.keys(p).forEach(function (k) { if (data && data[k]) q.push(encodeURIComponent(p[k]) + '=' + encodeURIComponent(data[k])); });
    return q.length ? url + (url.indexOf('?') < 0 ? '?' : '&') + q.join('&') : url;
  }
  bform.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var data = barData();
    if (cfg.booking) location.href = withDates(cfg.booking, data); else toRequest(data);
  });
  $$('[data-fah-book]').forEach(function (a) {
    a.addEventListener('click', function (ev) {
      ev.preventDefault();
      if (cfg.booking) location.href = withDates(a.getAttribute('href'), barData()); else toRequest();
    });
  });

  /* ---------- intro: words light up while scrolling ---------- */
  var words = $$('[data-fah-words] span');
  var wordsBox = $('[data-fah-words]');
  function onWords() {
    var r = wordsBox.getBoundingClientRect(), vh = window.innerHeight;
    var p = (vh * 0.85 - r.top) / (r.height + vh * 0.35);
    var lit = Math.round(Math.max(0, Math.min(1, p)) * words.length);
    for (var i = 0; i < words.length; i++) words[i].classList.toggle('is-lit', i < lit);
  }
  if (!wordsBox) { /* no intro block */ }
  else if (reduce) words.forEach(function (w) { w.classList.add('is-lit'); });
  else { window.addEventListener('scroll', onWords, { passive: true }); onWords(); }

  /* ---------- galleries (rooms) ---------- */
  function gallery(box) {
    var track = $('.fah-track', box), prev = $('.fah-prev', box), next = $('.fah-next', box), count = $('.fah-count', box);
    if (!track) return function () {};
    var total = track.children.length;
    function idx() { return Math.round(track.scrollLeft / Math.max(track.clientWidth, 1)); }
    function update() { var i = idx(); count.textContent = (i + 1) + ' / ' + total; prev.disabled = i <= 0; next.disabled = i >= total - 1; }
    function go(step) { track.scrollTo({ left: (idx() + step) * track.clientWidth, behavior: reduce ? 'auto' : 'smooth' }); }
    prev.addEventListener('click', function () { go(-1); });
    next.addEventListener('click', function () { go(1); });
    var t; track.addEventListener('scroll', function () { clearTimeout(t); t = setTimeout(update, 60); }, { passive: true });
    update();
    return update;
  }
  var galleryUpdaters = {};
  $$('.fah-room').forEach(function (room) { galleryUpdaters[room.getAttribute('data-room')] = gallery($('.fah-room__media', room)); });

  /* ---------- rooms: tabs, "who's travelling", size to scale ---------- */
  var tabs = $$('[data-room-tab]');
  var rooms = $$('.fah-room');
  var squares = $$('.fah-scale rect');
  function showRoom(id, scroll) {
    tabs.forEach(function (t) { var on = t.getAttribute('data-room-tab') === id; t.classList.toggle('is-on', on); t.setAttribute('aria-selected', on ? 'true' : 'false'); });
    rooms.forEach(function (r) { r.classList.toggle('is-on', r.getAttribute('data-room') === id); });
    squares.forEach(function (s) { s.classList.toggle('is-on', s.getAttribute('data-room-ref') === id); });
    if (galleryUpdaters[id]) setTimeout(galleryUpdaters[id], 30);
    var tab = tabs.filter(function (t) { return t.getAttribute('data-room-tab') === id; })[0];
    if (tab && tab.parentNode.scrollWidth > tab.parentNode.clientWidth) tab.parentNode.scrollTo({ left: tab.offsetLeft - 16, behavior: 'smooth' });
    if (scroll && window.innerWidth < 900) $('.fah-rooms__stage').scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
  }
  tabs.forEach(function (t) { t.addEventListener('click', function () { showRoom(t.getAttribute('data-room-tab')); }); });
  squares.forEach(function (s) { s.style.cursor = 'pointer'; s.addEventListener('click', function () { showRoom(s.getAttribute('data-room-ref')); }); });
  showRoom(tabs[0].getAttribute('data-room-tab'));
  var fitChips = $$('[data-fit]');
  fitChips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      var on = chip.getAttribute('aria-pressed') !== 'true';
      fitChips.forEach(function (c) { c.setAttribute('aria-pressed', c === chip && on ? 'true' : 'false'); });
      var fit = on ? chip.getAttribute('data-fit') : '';
      var first = null;
      tabs.forEach(function (t) {
        var m = fit && (' ' + t.getAttribute('data-fits') + ' ').indexOf(' ' + fit + ' ') > -1;
        t.classList.toggle('is-match', !!m);
        if (m && !first) first = t;
      });
      if (first) showRoom(first.getAttribute('data-room-tab'), true);
    });
  });
  if (location.hash) {
    var hashRoom = rooms.filter(function (r) { return '#' + r.id === location.hash; })[0];
    if (hashRoom) showRoom(hashRoom.getAttribute('data-room'));
  }

  /* ---------- hotel strip: drag to scroll ---------- */
  $$('[data-fah-drag]').forEach(function (strip) {
    var down = false, moved = false, x0 = 0, s0 = 0;
    strip.addEventListener('pointerdown', function (ev) { if (ev.pointerType !== 'mouse') return; down = true; moved = false; x0 = ev.clientX; s0 = strip.scrollLeft; });
    window.addEventListener('pointermove', function (ev) {
      if (!down) return;
      var dx = ev.clientX - x0;
      if (Math.abs(dx) > 5) { moved = true; strip.classList.add('is-grabbing'); }
      strip.scrollLeft = s0 - dx;
    });
    window.addEventListener('pointerup', function () { down = false; setTimeout(function () { strip.classList.remove('is-grabbing'); }, 0); });
    strip.addEventListener('click', function (ev) { if (moved) { ev.stopPropagation(); ev.preventDefault(); moved = false; } }, true);
  });

  /* ---------- neighbourhood map ---------- */
  var placeItems = $$('[data-place]', $('.fah-places'));
  var markers = $$('.fah-marker');
  function focusPlace(id) {
    placeItems.forEach(function (li) { li.classList.toggle('is-on', li.getAttribute('data-place') === id); });
    markers.forEach(function (m) {
      var on = m.getAttribute('data-place') === id;
      m.classList.toggle('is-on', on);
      if (on) m.parentNode.appendChild(m);
    });
    var pin = $('.fah-hotelpin'); if (pin) pin.parentNode.appendChild(pin);
  }
  placeItems.forEach(function (li) {
    var b = $('button', li), id = li.getAttribute('data-place');
    b.addEventListener('mouseenter', function () { focusPlace(id); });
    b.addEventListener('focus', function () { focusPlace(id); });
    b.addEventListener('click', function () {
      focusPlace(id);
      if (window.innerWidth < 900) $('.fah-map').scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'center' });
    });
  });
  markers.forEach(function (m) {
    m.addEventListener('mouseenter', function () { focusPlace(m.getAttribute('data-place')); });
    m.addEventListener('click', function () { focusPlace(m.getAttribute('data-place')); });
  });
  $$('[data-cat]', $('.fah-area .fah-chips')).forEach(function (chip, _, all) {
    chip.addEventListener('click', function () {
      var cat = chip.getAttribute('data-cat');
      all.forEach(function (c) { var on = c === chip; c.classList.toggle('is-on', on); c.setAttribute('aria-pressed', on ? 'true' : 'false'); });
      placeItems.forEach(function (li) { li.hidden = cat !== 'all' && li.getAttribute('data-cat') !== cat; });
      markers.forEach(function (m) { m.classList.toggle('is-dim', cat !== 'all' && m.getAttribute('data-cat') !== cat); });
      var first = placeItems.filter(function (li) { return !li.hidden; })[0];
      if (first) focusPlace(first.getAttribute('data-place'));
    });
  });
  if (placeItems[0]) focusPlace(placeItems[0].getAttribute('data-place'));

  /* ---------- transit planner ---------- */
  var dests = $$('[data-route-btn]');
  var routes = $$('[data-route]');
  dests.forEach(function (b) {
    b.addEventListener('click', function () {
      var id = b.getAttribute('data-route-btn');
      dests.forEach(function (d) { var on = d === b; d.classList.toggle('is-on', on); d.setAttribute('aria-pressed', on ? 'true' : 'false'); });
      routes.forEach(function (r) { r.classList.toggle('is-on', r.getAttribute('data-route') === id); });
      focusPlace(b.getAttribute('data-walk'));
    });
  });

  /* walk / transit switch in the Silom block */
  var segs = $$('.fah-seg__btn'), modePanels = $$('[data-mode-panel]');
  segs.forEach(function (b) {
    b.addEventListener('click', function () {
      var mode = b.getAttribute('data-mode');
      segs.forEach(function (x) { var on = x === b; x.classList.toggle('is-on', on); x.setAttribute('aria-selected', on ? 'true' : 'false'); });
      modePanels.forEach(function (p) { p.classList.toggle('is-on', p.getAttribute('data-mode-panel') === mode); });
      markers.forEach(function (m) { m.classList.remove('is-dim'); });
      if (mode === 'transit') {
        var cur = dests.filter(function (d) { return d.classList.contains('is-on'); })[0] || dests[0];
        if (cur) focusPlace(cur.getAttribute('data-walk'));
      } else {
        var first = placeItems.filter(function (li) { return !li.hidden; })[0];
        if (first) focusPlace(first.getAttribute('data-place'));
      }
    });
  });

  /* ---------- request form ---------- */
  var status = $('.fah-form__status');
  var rq = cfg.rq || {};
  reqForm.elements.checkin.min = today;
  reqForm.elements.checkout.min = addDays(today, 1);
  function setStatus(msg, kind) { status.textContent = msg; status.className = 'fah-form__status' + (kind ? ' is-' + kind : ''); }
  function tildaForm() {
    var forms = Array.prototype.slice.call(document.querySelectorAll('form.t-form'));
    return forms.filter(function (f) { return !root.contains(f); })[0];
  }
  /* readable field names for the e-mail the hotel receives */
  var LABELS = { type: 'Тип запроса', name: 'Имя', contact: 'Контакт', checkin: 'Заезд', checkout: 'Выезд',
    guests: 'Гости', rooms: 'Номера', message: 'Комментарий', lang: 'Язык страницы', page: 'Страница' };
  function setField(form, names, value) {
    for (var i = 0; i < names.length; i++) {
      var f = form.querySelector('[name="' + names[i] + '"]');
      if (f) { f.value = value; f.dispatchEvent(new Event('input', { bubbles: true })); f.dispatchEvent(new Event('change', { bubbles: true })); return; }
    }
  }
  function hideBridge() {
    var bridge = tildaForm(), rec = bridge && bridge.closest('.t-rec');
    if (rec) rec.style.cssText = 'position:absolute!important;left:-10000px!important;top:auto!important;width:1px;height:1px;overflow:hidden';
  }
  hideBridge();
  document.addEventListener('DOMContentLoaded', hideBridge);
  window.addEventListener('load', hideBridge);
  reqForm.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var el = reqForm.elements, ok = true;
    ['name', 'contact'].forEach(function (k) {
      var bad = !el[k].value.trim();
      el[k].closest('.fah-field').classList.toggle('is-error', bad);
      if (bad) ok = false;
    });
    if (!ok) { setStatus(rq.required, 'err'); return; }
    var data = {};
    ['type', 'name', 'contact', 'checkin', 'checkout', 'guests', 'rooms', 'message'].forEach(function (k) { data[k] = el[k] ? el[k].value : ''; });
    data.lang = cfg.lang; data.page = location.href;
    var form = tildaForm();
    if (form) {
      Array.prototype.slice.call(form.querySelectorAll('[data-fah-added]')).forEach(function (n) { n.parentNode.removeChild(n); });
      Object.keys(LABELS).forEach(function (k) {
        if (!data[k]) return;
        if (form.querySelector('[name="' + k + '"]')) { setField(form, [k], data[k]); return; }
        var h = document.createElement('input');
        h.type = 'hidden'; h.name = LABELS[k]; h.value = data[k]; h.setAttribute('data-fah-added', '1');
        form.appendChild(h);
      });
      /* standard Tilda fields, in case the form keeps them */
      setField(form, ['Name', 'name'], data.name);
      if (/@/.test(data.contact)) setField(form, ['Email', 'email'], data.contact);
      else setField(form, ['Phone', 'phone', 'tel'], data.contact);
      setStatus(rq.sending);
      form.classList.remove('js-send-form-success', 'js-send-form-error');  /* left over from an earlier request */
      var btn = form.querySelector('[type="submit"]');
      if (btn) btn.click(); else form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
      var tries = 0;
      var poll = setInterval(function () {
        tries++;
        var okBox = form.querySelector('.js-successbox'), errBox = form.querySelector('.js-errorbox-all');
        var shown = function (n) { return n && n.offsetParent !== null && getComputedStyle(n).display !== 'none'; };
        /* Tilda marks the form js-send-form-success / js-send-form-error once its server answers */
        var sent = form.classList.contains('js-send-form-success') || shown(okBox);
        var failed = form.classList.contains('js-send-form-error') || shown(errBox);
        if (sent) { clearInterval(poll); setStatus(rq.success, 'ok'); reqForm.reset(); }
        else if (failed || tries > 40) { clearInterval(poll); setStatus(failed ? rq.error : rq.success, failed ? 'err' : 'ok'); }
      }, 250);
      return;
    }
    if (cfg.email) {
      var lines = Object.keys(data).filter(function (k) { return data[k]; }).map(function (k) { return k + ': ' + data[k]; });
      location.href = 'mailto:' + cfg.email + '?subject=' + encodeURIComponent(cfg.subject || 'Request') + '&body=' + encodeURIComponent(lines.join('\n'));
      setStatus(rq.success, 'ok');
      return;
    }
    setStatus(rq.preview, 'err');
  });
  $$('.fah-field input').forEach(function (i) { i.addEventListener('input', function () { i.closest('.fah-field').classList.remove('is-error'); }); });

  /* ---------- lightbox ---------- */
  var box = $('.fah-lightbox'), boxImg = $('img', box), caption = $('.fah-lightbox__caption', box);
  var items = [], pos = 0, lastFocus = null;
  function show(i) {
    pos = (i + items.length) % items.length;
    var im = items[pos];
    boxImg.src = im.getAttribute('data-full') || im.currentSrc || im.src;
    boxImg.alt = im.alt;
    caption.textContent = im.alt + '  ·  ' + (pos + 1) + ' / ' + items.length;
  }
  function close() { box.hidden = true; boxImg.removeAttribute('src'); document.documentElement.style.overflow = ''; if (lastFocus) lastFocus.focus(); }
  root.addEventListener('click', function (ev) {
    var btn = ev.target.closest('.fah-zoom');
    if (!btn) return;
    var group = btn.closest('.fah-track, .fah-strip__track, .fah-peek, .fah-hotel__photos, .fah-hero__photo');
    var all = $$('.fah-zoom', group);
    items = all.map(function (z) { return $('img', z); });
    lastFocus = btn;
    show(all.indexOf(btn));
    box.hidden = false;
    document.documentElement.style.overflow = 'hidden';
    $('.fah-lb-close', box).focus();
  });
  $('.fah-lb-close', box).addEventListener('click', close);
  $('.fah-prev', box).addEventListener('click', function () { show(pos - 1); });
  $('.fah-next', box).addEventListener('click', function () { show(pos + 1); });
  box.addEventListener('click', function (ev) { if (ev.target === box) close(); });
  document.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape' && menu.classList.contains('is-open')) setMenu(false);
    if (box.hidden) return;
    if (ev.key === 'Escape') close();
    else if (ev.key === 'ArrowLeft') show(pos - 1);
    else if (ev.key === 'ArrowRight') show(pos + 1);
  });
  var x0 = null;
  box.addEventListener('touchstart', function (ev) { x0 = ev.touches[0].clientX; }, { passive: true });
  box.addEventListener('touchend', function (ev) {
    if (x0 === null) return;
    var dx = ev.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 50) show(pos + (dx < 0 ? 1 : -1));
    x0 = null;
  });

  /* ---------- reveal on scroll, mobile booking bar ---------- */
  if ('IntersectionObserver' in window) {
    $$('.fah-head, .fah-numbers li, .fah-rooms__grid, .fah-hotel__head, .fah-stay, .fah-hotel__photos, .fah-rooms__intro, .fah-area__grid, .fah-request__grid, .fah-footer__grid')
      .forEach(function (el) { if (el.getBoundingClientRect().top > window.innerHeight) el.classList.add('fah-reveal'); });
    var rio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('is-in'); rio.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    $$('.fah-reveal').forEach(function (el) { rio.observe(el); });
    var bar = $('.fah-bookbar'), footer = $('.fah-footer'), heroOn = true, footOn = false;
    var bio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.target === hero) heroOn = en.isIntersecting; else footOn = en.isIntersecting; });
      bar.classList.toggle('is-visible', !heroOn && !footOn);
    });
    bio.observe(hero); bio.observe(footer);
  }
})();
