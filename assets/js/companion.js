// Le monde du Compagnon sur le site (build 9, 2026-09-17).
//
// Trois gestes, et seulement quand ils se voient :
//   • les chats clignent comme dans l'app (LivingCat.tsx) : toutes les 3 à
//     7 secondes, 140 ms les yeux fermés, une fois sur cinq un double
//     clignement — le même sprite « yeux fermés » que l'app ;
//   • les marches de pixels entre les deux mondes se posent quand on arrive ;
//   • le coffre du jour s'ouvre (fermé → entrouvert → ouvert, les trois
//     sprites de l'app) et laisse sortir ses quatre raretés.
// Les boucles des vignettes de jeux (CSS) ne tournent que lorsque leur scène
// est à l'écran. Sous « réduire les animations », rien ne bouge : les
// marches sont posées, le coffre est ouvert, les chats gardent les yeux
// ouverts.
(function () {
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var canObserve = 'IntersectionObserver' in window;

  function whenVisible(elements, threshold, onEnter, onLeave) {
    if (!elements.length) return;
    if (!canObserve) {
      elements.forEach(function (el) { onEnter(el); });
      return;
    }
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) onEnter(entry.target);
        else if (onLeave) onLeave(entry.target);
      });
    }, { threshold: threshold });
    elements.forEach(function (el) { observer.observe(el); });
  }

  var toArray = function (list) { return Array.prototype.slice.call(list); };

  // ── Les marches de pixels ─────────────────────────────────────────────
  // On observe la section qui SUIT chaque marche, jamais la marche : rognée à
  // zéro avant d'être dessinée, elle ne croise jamais l'écran aux yeux de
  // l'observateur. La marge basse déclenche quand la section voisine monte
  // au tiers inférieur de l'écran — la marche, juste au-dessus, est alors
  // bien visible pendant qu'elle se pose.
  var edges = toArray(document.querySelectorAll('.pixel-edge'));
  if (reduceMotion || !canObserve) {
    edges.forEach(function (edge) { edge.classList.add('is-drawn'); });
  } else {
    var edgeObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.__pixelEdge.classList.add('is-drawn');
        edgeObserver.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -30% 0px' });
    edges.forEach(function (edge) {
      var next = edge.nextElementSibling || (edge.parentElement && edge.parentElement.nextElementSibling);
      if (!next) {
        edge.classList.add('is-drawn');
        return;
      }
      next.__pixelEdge = edge;
      edgeObserver.observe(next);
    });
  }

  // ── Les scènes de jeux : jouées à l'écran, en pause hors écran ────────
  var scenes = toArray(document.querySelectorAll('.scene'));
  if (!reduceMotion) {
    whenVisible(
      scenes,
      0.05,
      function (scene) { scene.classList.add('is-playing'); },
      function (scene) { scene.classList.remove('is-playing'); }
    );
  }

  // ── Le clignement ─────────────────────────────────────────────────────
  var BLINK_MIN_DELAY_MS = 3000;
  var BLINK_MAX_DELAY_MS = 7000;
  var BLINK_CLOSED_MS = 140;
  var DOUBLE_BLINK_GAP_MS = 180;
  var DOUBLE_BLINK_CHANCE = 0.2;

  function startBlinking(img) {
    var open = img.getAttribute('src');
    var closed = img.getAttribute('data-blink');
    if (!closed) return;
    var preload = new Image();
    preload.src = closed;

    function blinkOnce(then) {
      img.src = closed;
      window.setTimeout(function () {
        img.src = open;
        then();
      }, BLINK_CLOSED_MS);
    }

    function schedule() {
      var delay = BLINK_MIN_DELAY_MS + Math.random() * (BLINK_MAX_DELAY_MS - BLINK_MIN_DELAY_MS);
      window.setTimeout(function () {
        blinkOnce(function () {
          if (Math.random() < DOUBLE_BLINK_CHANCE) {
            window.setTimeout(function () { blinkOnce(schedule); }, DOUBLE_BLINK_GAP_MS);
          } else {
            schedule();
          }
        });
      }, delay);
    }

    schedule();
  }

  if (!reduceMotion) {
    var blinkers = toArray(document.querySelectorAll('img[data-blink]'));
    var started = [];
    whenVisible(blinkers, 0.2, function (img) {
      if (started.indexOf(img) !== -1) return;
      started.push(img);
      startBlinking(img);
    });
  }

  // ── Le coffre du jour ─────────────────────────────────────────────────
  var chests = toArray(document.querySelectorAll('[data-chest]'));
  chests.forEach(function (chest) {
    var sprite = chest.querySelector('.chest__sprite');
    var frames = sprite ? (sprite.getAttribute('data-frames') || '').split(/\s+/).filter(Boolean) : [];
    frames.forEach(function (src) {
      var preload = new Image();
      preload.src = src;
    });

    function open(immediately) {
      if (chest.classList.contains('is-open')) return;
      if (immediately || !frames.length) {
        if (frames.length) sprite.src = frames[frames.length - 1];
        chest.classList.add('is-open');
        return;
      }
      var step = 0;
      function next() {
        sprite.src = frames[step];
        step += 1;
        if (step < frames.length) window.setTimeout(next, 260);
        else chest.classList.add('is-open');
      }
      window.setTimeout(next, 220);
    }

    if (reduceMotion) open(true);
    else whenVisible([chest], 0.55, function () { open(false); });
  });
})();
