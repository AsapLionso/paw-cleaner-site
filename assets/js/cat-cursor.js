// Curseur personnalisé — l'icône patte (assets/img/paw-cursor.svg, même
// silhouette que IconPaw dans l'app RN) suit le pointeur. Version
// volontairement simple : suivi en douceur (lerp) et léger agrandissement
// au survol des éléments interactifs marqués data-magnetic, rien d'autre.
// Une première version portait fidèlement le squash/stretch selon la
// vitesse + le morphing de forme au survol d'un composant GSAP fourni —
// jugée trop complexe et donnant un effet "ovale" étrange au contact du
// texte (le rond s'étirait). Retirée entièrement au profit de ce curseur
// simple. Desktop uniquement — désactivé sur tactile.
(function () {
  var isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  if (isTouchDevice) return;

  var CURSOR_SIZE = 32; // hauteur en px — icône plate simple, pas besoin du gabarit 44px de l'ancienne photo
  var HOVER_SCALE = 1.25;
  // 0.4 plutôt que 0.18 : à 0.18 le curseur accusait un retard perceptible
  // sur la souris (sensation de devoir "trop bouger" pour l'atteindre) —
  // combiné à la transition CSS sur transform (retirée ci-dessous), le
  // retard était doublé. Le lerp JS seul suffit à lisser le mouvement.
  var LERP_AMOUNT = 0.4;
  // Incline la patte comme la pointe d'une flèche de curseur classique
  // (négatif = sens antihoraire, penche le haut de l'icône vers la gauche).
  var CURSOR_ROTATION_DEG = -20;
  // Filtre par défaut vs. survol d'une zone cliquable (data-magnetic) : la
  // patte crème devient noire au survol — brightness(0) fonctionne quelle
  // que soit la couleur source du SVG, pas besoin d'un second fichier. Les
  // deux drop-shadow blancs (au lieu du drop-shadow noir habituel) évitent
  // que la patte devienne invisible sur un bouton déjà sombre.
  var DEFAULT_FILTER = 'drop-shadow(0 2px 6px rgba(0, 0, 0, 0.45))';
  var HOVER_FILTER =
    'brightness(0) drop-shadow(0 0 1px rgba(255, 255, 255, 0.8)) drop-shadow(0 1px 4px rgba(255, 255, 255, 0.35))';

  var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  document.documentElement.style.cursor = 'none';

  var cursor = document.createElement('img');
  cursor.src = '/assets/img/paw-cursor.svg';
  cursor.alt = '';
  cursor.setAttribute('aria-hidden', 'true');
  cursor.className = 'paw-cursor';
  cursor.style.position = 'fixed';
  cursor.style.top = '0';
  cursor.style.left = '0';
  cursor.style.height = CURSOR_SIZE + 'px';
  cursor.style.width = 'auto';
  cursor.style.zIndex = '9999';
  cursor.style.pointerEvents = 'none';
  cursor.style.willChange = 'transform';
  cursor.style.opacity = '0';
  // Ombre douce : garde la patte visible même sur les boutons clairs
  // (fond crème), sans recourir à mix-blend-mode/backdrop-filter.
  cursor.style.filter = DEFAULT_FILTER;
  // Pas de transition CSS sur `transform` : il est réécrit à chaque frame
  // par la boucle rAF (tick), une transition dessus s'empilait sur le lerp
  // JS et doublait le retard perçu. opacity/filter restent des changements
  // d'état ponctuels (survol, sortie de viewport) — eux gardent une
  // transition.
  cursor.style.transitionProperty = 'opacity, filter';
  cursor.style.transitionDuration = prefersReducedMotion ? '0s' : '0.2s, 0.15s';
  cursor.style.transitionTimingFunction = 'ease-out';
  document.body.appendChild(cursor);

  var pos = { x: -100, y: -100 };
  var target = { x: -100, y: -100 };
  var isHovering = false;

  function render() {
    var scale = isHovering ? HOVER_SCALE : 1;
    cursor.style.transform =
      'translate(-50%, -50%) translate(' + pos.x + 'px, ' + pos.y + 'px) rotate(' + CURSOR_ROTATION_DEG + 'deg) scale(' + scale + ')';
    cursor.style.filter = isHovering ? HOVER_FILTER : DEFAULT_FILTER;
  }

  window.addEventListener(
    'pointermove',
    function (e) {
      pos.x = target.x = e.clientX;
      pos.y = target.y = e.clientY;
      cursor.style.opacity = '1';
      render();
    },
    { once: true }
  );

  window.addEventListener('pointermove', function (e) {
    target.x = e.clientX;
    target.y = e.clientY;
    var inViewport = e.clientX >= 0 && e.clientX <= window.innerWidth && e.clientY >= 0 && e.clientY <= window.innerHeight;
    cursor.style.opacity = inViewport ? '1' : '0';
  });

  document.addEventListener('mouseleave', function () {
    cursor.style.opacity = '0';
  });
  document.addEventListener('mouseenter', function () {
    cursor.style.opacity = '1';
  });

  function tick() {
    requestAnimationFrame(tick);
    var lerp = prefersReducedMotion ? 1 : LERP_AMOUNT;
    pos.x += (target.x - pos.x) * lerp;
    pos.y += (target.y - pos.y) * lerp;
    render();
  }
  requestAnimationFrame(tick);

  document.querySelectorAll('[data-magnetic]').forEach(function (el) {
    el.addEventListener('pointerenter', function () {
      isHovering = true;
    });
    el.addEventListener('pointerleave', function () {
      isHovering = false;
    });
  });
})();
