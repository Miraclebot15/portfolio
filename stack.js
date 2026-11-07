/* Stack page: filters, tilt, click reactions, details sheet, count-up. */
(function () {
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return [].slice.call((r || document).querySelectorAll(s)); };
  var usage = {};
  try { usage = JSON.parse($('#stack-usage').textContent); } catch (e) {}
  var sheet = $('#sheet'), grid = $('.stkg'), last = null;
  if (!sheet || !grid) return;

  function burst(li) {
    if (reduce) return;
    li.classList.remove('pop'); void li.offsetWidth; li.classList.add('pop');
    for (var i = 0; i < 8; i++) {
      var a = (Math.PI * 2 * i) / 8, d = 34 + (i % 2) * 14, b = document.createElement('i');
      b.className = 'bt'; b.setAttribute('aria-hidden', 'true');
      b.style.setProperty('--dx', Math.round(Math.cos(a) * d) + 'px');
      b.style.setProperty('--dy', Math.round(Math.sin(a) * d) + 'px');
      li.appendChild(b);
      setTimeout(function (n) { return function () { n.remove(); }; }(b), 760);
    }
    setTimeout(function () { li.classList.remove('pop'); }, 520);
  }

  function openSheet(btn) {
    var name = btn.getAttribute('data-n'), d = usage[name.toLowerCase()] || { p: [], t: '', h: 'stack.html' }, list = d.p;
    var ic = $('#sh-ic'), svg = $('svg', btn);
    ic.innerHTML = ''; ic.className = 'sh-ic';
    if (svg) ic.appendChild(svg.cloneNode(true)); else { ic.className = 'sh-ic tmono'; ic.textContent = name.charAt(0); }
    $('#sh-cat').textContent = btn.getAttribute('data-c');
    $('#sh-name').textContent = name;
    $('#sh-tag').textContent = d.t; $('#sh-go').href = d.h;
    $('#sh-lbl').textContent = list.length ? 'Listed on these project pages' : btn.classList.contains('cn') ? 'A design idea rather than a tool.' : 'No project page lists this yet.';
    var ul = $('#sh-list'); ul.innerHTML = '';
    list.forEach(function (p) {
      var li = document.createElement('li'), a = document.createElement('a');
      a.href = p.h; a.textContent = p.n; li.appendChild(a); ul.appendChild(li);
    });
    last = btn; sheet.classList.add('open');
    setTimeout(function () { $('#sh-x').focus({ preventScroll: true }); }, reduce ? 0 : 120);
  }
  function closeSheet() {
    if (!sheet.classList.contains('open')) return;
    sheet.classList.remove('open');
    if (last) last.focus({ preventScroll: true });
  }

  grid.addEventListener('click', function (e) {
    var btn = e.target.closest('.sb[data-n]');
    if (!btn || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button) return;
    e.preventDefault();
    burst(btn.parentNode); openSheet(btn);
  });
  $('#sh-x').addEventListener('click', closeSheet);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeSheet(); });
  document.addEventListener('click', function (e) {
    if (!sheet.classList.contains('open')) return;
    if (!e.target.closest('#sheet') && !e.target.closest('.sb[data-n]')) closeSheet();
  });

  // Category filter: spotlight one card, dim the rest.
  var cards = $$('.stkc', grid);
  $('.frail').addEventListener('click', function (e) {
    var b = e.target.closest('.fp');
    if (!b) return;
    $$('.fp').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
    var f = b.getAttribute('data-f');
    cards.forEach(function (c) { c.classList.toggle('dim', f !== 'all' && c.getAttribute('data-k') !== f); });
    if (f !== 'all') {
      var t = cards[+f];
      if (t) t.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'center' });
    }
  });

  // Pointer tilt and glare. A mouse tracks hover; a finger tilts the card toward the press point.
  if (!reduce) {
    cards.forEach(function (c) {
      var inner = $('.stkc-i', c), raf = 0, ev = null;
      function frame() {
        raf = 0;
        var r = inner.getBoundingClientRect(), x = (ev.clientX - r.left) / r.width, y = (ev.clientY - r.top) / r.height;
        inner.style.setProperty('--ry', ((x - 0.5) * 9).toFixed(2) + 'deg');
        inner.style.setProperty('--rx', ((0.5 - y) * 7).toFixed(2) + 'deg');
        inner.style.setProperty('--gx', (x * 100).toFixed(1) + '%');
        inner.style.setProperty('--gy', (y * 100).toFixed(1) + '%');
      }
      inner.addEventListener('pointerenter', function () { inner.classList.add('mv'); });
      function move(e) { ev = e; if (!raf) raf = requestAnimationFrame(frame); }
      function rest() {
        inner.classList.remove('mv');
        inner.style.setProperty('--rx', '0deg'); inner.style.setProperty('--ry', '0deg');
      }
      inner.addEventListener('pointermove', move);
      inner.addEventListener('pointerdown', function (e) { inner.classList.add('mv'); move(e); });
      ['pointerleave', 'pointerup', 'pointercancel'].forEach(function (t) { inner.addEventListener(t, rest); });
    });
  }

  // Count-up for the headline numbers.
  var stats = $('.stats');
  if (stats && !reduce && 'IntersectionObserver' in window) {
    var nums = $$('[data-count]', stats);
    nums.forEach(function (n) { n.textContent = '0'; });
    new IntersectionObserver(function (es, o) {
      if (!es[0].isIntersecting) return;
      o.disconnect();
      var t0 = performance.now();
      (function step(t) {
        var k = Math.min(1, (t - t0) / 1300), e = 1 - Math.pow(1 - k, 3);
        nums.forEach(function (n) { n.textContent = Math.round(+n.getAttribute('data-count') * e); });
        if (k < 1) requestAnimationFrame(step);
      })(t0);
    }, { threshold: 0.4 }).observe(stats);
  }
})();
