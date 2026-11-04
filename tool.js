/* Deep-dive pages: layers (tabs), next-layer buttons, copy button. */
(function () {
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return [].slice.call((r || document).querySelectorAll(s)); };
  var tabs = $$('.lay [role=tab]'), panels = $$('.lp');
  if (!tabs.length) return;
  var ids = tabs.map(function (t) { return t.getAttribute('data-l'); });

  function show(id, focus, write) {
    if (ids.indexOf(id) < 0) id = ids[0];
    tabs.forEach(function (t) {
      var on = t.getAttribute('data-l') === id;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.tabIndex = on ? 0 : -1;
      if (on && focus) t.focus({ preventScroll: true });
    });
    panels.forEach(function (p) { p.classList.toggle('shown', p.id === id); });
    if (write && history.replaceState) history.replaceState(null, '', '#' + id);
  }

  $('.lay').addEventListener('click', function (e) {
    var t = e.target.closest('[role=tab]');
    if (t) show(t.getAttribute('data-l'), false, true);
  });
  $('.lay').addEventListener('keydown', function (e) {
    var i = ids.indexOf(document.activeElement && document.activeElement.getAttribute('data-l'));
    if (i < 0) return;
    var j = e.key === 'ArrowRight' ? (i + 1) % ids.length : e.key === 'ArrowLeft' ? (i + ids.length - 1) % ids.length : e.key === 'Home' ? 0 : e.key === 'End' ? ids.length - 1 : -1;
    if (j < 0) return;
    e.preventDefault(); show(ids[j], true, true);
  });
  $$('.nx').forEach(function (b) {
    b.addEventListener('click', function () {
      show(b.getAttribute('data-go'), false, true);
      var bar = $('.lay'); if (bar) bar.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
    });
  });

  var cp = $('.cp');
  if (cp) cp.addEventListener('click', function () {
    var text = cp.closest('.cb').getAttribute('data-code') || '';
    function done(ok) { cp.textContent = ok ? 'Copied' : 'Press and hold to copy'; setTimeout(function () { cp.textContent = 'Copy'; }, 1600); }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(function () { done(true); }, function () { done(false); });
    else done(false);
  });

  function fromHash() { show((location.hash || '').slice(1), false, false); }
  window.addEventListener('hashchange', fromHash);
  fromHash();
})();
