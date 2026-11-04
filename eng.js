/* Engineering page: topic filter with a soft fade. */
(function () {
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return [].slice.call((r || document).querySelectorAll(s)); };
  var bar = $('.efil'), cards = $$('.note-card'), count = $('.ecount');
  if (!bar || !cards.length) return;
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  function toggle(card, show) {
    if (show) {
      if (card.hidden) {
        card.hidden = false;
        requestAnimationFrame(function () { requestAnimationFrame(function () { card.classList.remove('out'); }); });
      } else card.classList.remove('out');
    } else {
      card.classList.add('out');
      setTimeout(function () { if (card.classList.contains('out')) card.hidden = true; }, reduce ? 0 : 300);
    }
  }

  bar.addEventListener('click', function (e) {
    var b = e.target.closest('.ef');
    if (!b) return;
    $$('.ef', bar).forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
    var t = b.getAttribute('data-t'), n = 0;
    cards.forEach(function (c) {
      var show = t === 'all' || c.getAttribute('data-topics').split('|').indexOf(t) > -1;
      if (show) n++;
      toggle(c, show);
    });
    count.textContent = n + (n === 1 ? ' note' : ' notes') + (t === 'all' ? '' : ' on ' + b.textContent);
  });
})();
