// Portage vanilla JS du composant React "MagneticCursor" fourni par le
// fondateur (GSAP + lib "vecteur" à l'origine) — aucune des deux dépendances
// n'est nécessaire ici : le suivi du pointeur (lerp), le squash/stretch
// selon la vitesse, l'effet magnétique et le morphing de forme au survol
// sont remplacés par un boucle requestAnimationFrame + des transitions CSS
// natives. Cohérent avec l'architecture zéro-dépendance du site (voir
// README.md). Desktop uniquement — désactivé sur tactile, comme l'original
// (disableOnTouch par défaut).
(function () {
  var isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  if (isTouchDevice) return;

  var CURSOR_SIZE = 24;
  var CURSOR_COLOR = '#ffffff';
  var BLEND_MODE = 'exclusion';
  var CONTRAST_BOOST = 1.5; // visibilité sur fonds à faible contraste, voir composant fourni
  var MAGNETIC_FACTOR = 0.35; // force d'attraction de l'élément survolé vers le pointeur
  var HOVER_PADDING = 12;
  var LERP_AMOUNT = 0.15;
  var SPEED_MULTIPLIER = 0.02;
  var MAX_SCALE_X = 1;
  var MAX_SCALE_Y = 0.3;
  var SNAP_EASE = 'cubic-bezier(0.16, 1, 0.3, 1)'; // approx. power3.out
  var PULL_DURATION_MS = 700; // approx. elastic.out(1, 0.3) sur 1s dans l'original

  var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var detachDuration = prefersReducedMotion ? 100 : 350;

  document.documentElement.style.cursor = 'none';

  var cursor = document.createElement('div');
  cursor.className = 'magnetic-cursor';
  cursor.setAttribute('aria-hidden', 'true');
  cursor.style.position = 'fixed';
  cursor.style.top = '0';
  cursor.style.left = '0';
  cursor.style.zIndex = '9999';
  cursor.style.pointerEvents = 'none';
  cursor.style.willChange = 'transform, width, height, border-radius';
  cursor.style.backgroundColor = CURSOR_COLOR;
  cursor.style.mixBlendMode = BLEND_MODE;
  cursor.style.width = CURSOR_SIZE + 'px';
  cursor.style.height = CURSOR_SIZE + 'px';
  cursor.style.borderRadius = '50%';
  cursor.style.opacity = '0';
  cursor.style.backdropFilter = 'contrast(' + CONTRAST_BOOST + ')';
  cursor.style.webkitBackdropFilter = 'contrast(' + CONTRAST_BOOST + ')';
  cursor.style.transitionProperty = 'width, height, border-radius, background-color, opacity';
  cursor.style.transitionDuration = '0.3s, 0.3s, 0.3s, 0.3s, 0.2s';
  cursor.style.transitionTimingFunction = SNAP_EASE;
  document.body.appendChild(cursor);

  var pos = { x: -100, y: -100 };
  var target = { x: -100, y: -100 };
  var prev = { x: -100, y: -100 };
  var isHovered = false;
  var isDetaching = false;
  var overText = false;
  var detachTimer;

  function setTransform(x, y, rotateDeg, scaleX, scaleY) {
    cursor.style.transform =
      'translate(-50%, -50%) translate(' + x + 'px, ' + y + 'px) rotate(' + (rotateDeg || 0) + 'deg) scale(' + scaleX + ', ' + scaleY + ')';
  }

  function initPosition(e) {
    pos.x = target.x = prev.x = e.clientX;
    pos.y = target.y = prev.y = e.clientY;
    setTransform(pos.x, pos.y, 0, 1, 1);
    cursor.style.opacity = '1';
  }
  window.addEventListener('pointermove', initPosition, { once: true });

  var TEXT_TAGS = ['P', 'SPAN', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6'];
  function onPointerMove(e) {
    target.x = e.clientX;
    target.y = e.clientY;

    var inViewport = e.clientX >= 0 && e.clientX <= window.innerWidth && e.clientY >= 0 && e.clientY <= window.innerHeight;
    cursor.style.opacity = inViewport ? '1' : '0';

    var el = e.target;
    overText = TEXT_TAGS.indexOf(el.tagName) !== -1 || getComputedStyle(el).cursor === 'text';
  }
  window.addEventListener('pointermove', onPointerMove);

  document.addEventListener('mouseleave', function () {
    cursor.style.opacity = '0';
  });
  document.addEventListener('mouseenter', function () {
    cursor.style.opacity = '1';
  });

  function tick() {
    requestAnimationFrame(tick);
    if (isHovered) return;

    var lerp = prefersReducedMotion ? 1 : LERP_AMOUNT;
    pos.x += (target.x - pos.x) * lerp;
    pos.y += (target.y - pos.y) * lerp;
    var dx = pos.x - prev.x;
    var dy = pos.y - prev.y;
    prev.x = pos.x;
    prev.y = pos.y;

    if (isDetaching) {
      setTransform(pos.x, pos.y, 0, 1, 1);
      return;
    }

    if (overText) {
      setTransform(pos.x, pos.y, 0, 0.5, 1.5);
      return;
    }

    var speed = Math.sqrt(dx * dx + dy * dy) * SPEED_MULTIPLIER;
    var rotateDeg = Math.atan2(dy, dx) * (180 / Math.PI);
    var scaleX = 1 + Math.min(speed, MAX_SCALE_X);
    var scaleY = 1 - Math.min(speed, MAX_SCALE_Y);
    setTransform(pos.x, pos.y, rotateDeg, scaleX, scaleY);
  }
  requestAnimationFrame(tick);

  // Approxime elastic.out(1, 0.3) de GSAP, utilisé pour le retour de
  // l'élément magnétique vers son repos (voir handlePointerOut).
  function elasticOut(t) {
    if (t === 0 || t === 1) return t;
    return Math.pow(2, -10 * t) * Math.sin(((t - 0.075) * (2 * Math.PI)) / 0.3) + 1;
  }

  function animateValue(from, to, duration, onUpdate) {
    var start = null;
    function step(ts) {
      if (start === null) start = ts;
      var elapsed = ts - start;
      var t = Math.min(1, elapsed / duration);
      onUpdate(from + (to - from) * elasticOut(t));
      if (t < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  document.querySelectorAll('[data-magnetic]').forEach(function (el) {
    el.style.willChange = 'transform';
    var currentX = 0;
    var currentY = 0;
    var rafPending = false;

    function applyPull() {
      el.style.transform = 'translate(' + currentX.toFixed(2) + 'px, ' + currentY.toFixed(2) + 'px)';
    }

    el.addEventListener('pointerenter', function () {
      isHovered = true;
      isDetaching = false;
      clearTimeout(detachTimer);

      var rect = el.getBoundingClientRect();
      var cs = getComputedStyle(el);
      var padding = HOVER_PADDING * (1 + MAGNETIC_FACTOR);
      var centerX = rect.left + rect.width / 2;
      var centerY = rect.top + rect.height / 2;

      cursor.style.transitionProperty = 'width, height, border-radius, background-color, transform';
      cursor.style.transitionDuration = '0.3s, 0.3s, 0.3s, 0.3s, 0.3s';
      cursor.style.width = rect.width + padding * 2 + 'px';
      cursor.style.height = rect.height + padding * 2 + 'px';
      cursor.style.borderRadius = cs.borderRadius;
      cursor.style.backgroundColor = el.getAttribute('data-magnetic-color') || CURSOR_COLOR;
      setTransform(centerX, centerY, 0, 1, 1);
    });

    el.addEventListener('pointerleave', function () {
      isHovered = false;
      isDetaching = true;

      var cursorRect = cursor.getBoundingClientRect();
      pos.x = prev.x = cursorRect.left + cursorRect.width / 2;
      pos.y = prev.y = cursorRect.top + cursorRect.height / 2;

      cursor.style.transitionProperty = 'width, height, border-radius, background-color';
      cursor.style.transitionDuration = '0.3s, 0.3s, 0.3s, 0.3s';
      cursor.style.width = CURSOR_SIZE + 'px';
      cursor.style.height = CURSOR_SIZE + 'px';
      cursor.style.borderRadius = '50%';
      cursor.style.backgroundColor = CURSOR_COLOR;

      clearTimeout(detachTimer);
      detachTimer = setTimeout(function () {
        isDetaching = false;
      }, detachDuration);

      animateValue(currentX, 0, PULL_DURATION_MS, function (v) {
        currentX = v;
        applyPull();
      });
      animateValue(currentY, 0, PULL_DURATION_MS, function (v) {
        currentY = v;
        applyPull();
      });
    });

    el.addEventListener('pointermove', function (e) {
      if (rafPending) return;
      rafPending = true;
      requestAnimationFrame(function () {
        rafPending = false;
        var rect = el.getBoundingClientRect();
        var targetX = (e.clientX - (rect.left + rect.width / 2)) * MAGNETIC_FACTOR;
        var targetY = (e.clientY - (rect.top + rect.height / 2)) * MAGNETIC_FACTOR;
        animateValue(currentX, targetX, PULL_DURATION_MS, function (v) {
          currentX = v;
          applyPull();
        });
        animateValue(currentY, targetY, PULL_DURATION_MS, function (v) {
          currentY = v;
          applyPull();
        });
      });
    });

    el.addEventListener('pointerout', function () {
      animateValue(currentX, 0, PULL_DURATION_MS, function (v) {
        currentX = v;
        applyPull();
      });
      animateValue(currentY, 0, PULL_DURATION_MS, function (v) {
        currentY = v;
        applyPull();
      });
    });
  });
})();
