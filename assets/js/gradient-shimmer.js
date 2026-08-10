// Portage vanilla JS du composant React "GradientShimmer" fourni par le
// fondateur (shadcn/Tailwind à l'origine) — aucune dépendance React/build
// step nécessaire ici, tout l'algorithme (gradient multi-stops, sweep via
// Web Animations API, garde-fous scroll/visibilité/reduced-motion) ne
// touchait déjà que le DOM et CSS natifs. Cohérent avec l'architecture
// zéro-dépendance du reste du site (voir README.md).
(function () {
  var GRADIENT_PRESETS = {
    sunrise: [
      { color: '#B6D3EF', position: 0 },
      { color: '#CAD1D7', position: 0.153 },
      { color: '#D7CFC8', position: 0.252 },
      { color: '#E1CDB9', position: 0.341 },
      { color: '#EAC6A5', position: 0.424 },
      { color: '#EDB185', position: 0.505 },
      { color: '#EF9B62', position: 0.586 },
      { color: '#F18F60', position: 0.669 },
      { color: '#F48D7A', position: 0.758 },
      { color: '#F78A94', position: 0.857 },
      { color: '#F888A0', position: 1 },
    ],
    bubble: [
      { color: '#F5EBD9', position: 0 },
      { color: '#F2D4DB', position: 0.31 },
      { color: '#EBBDDE', position: 0.5 },
      { color: '#CCBAE3', position: 0.65 },
      { color: '#8CBFF0', position: 0.82 },
      { color: '#78B0FF', position: 1 },
    ],
    peach: [
      { color: '#D9F5FA', position: 0 },
      { color: '#FCD9D6', position: 0.31 },
      { color: '#FCBAC9', position: 0.61 },
      { color: '#F0B3F5', position: 1 },
    ],
    tonic: [
      { color: '#E3EDF0', position: 0 },
      { color: '#E8EBB8', position: 0.27 },
      { color: '#F0DEA3', position: 0.43 },
      { color: '#E8B078', position: 0.75 },
      { color: '#F29682', position: 1 },
    ],
    mint: [
      { color: '#DECEE8', position: 0 },
      { color: '#CBBAEE', position: 0.21 },
      { color: '#7DC0FB', position: 0.46 },
      { color: '#00C7A6', position: 1 },
    ],
    spring: [
      { color: '#F7D5C5', position: 0.07 },
      { color: '#46A8C0', position: 0.58 },
      { color: '#43AE7D', position: 1 },
    ],
    twilight: [
      { color: '#E3CCE6', position: 0 },
      { color: '#4E8CD5', position: 0.35 },
      { color: '#6068C2', position: 0.64 },
      { color: '#38364E', position: 1 },
    ],
    bay: [
      { color: '#DBE3D0', position: 0 },
      { color: '#8DB8A7', position: 0.23 },
      { color: '#2D8E9A', position: 0.42 },
      { color: '#076492', position: 0.59 },
      { color: '#154288', position: 0.79 },
      { color: '#262C81', position: 1 },
    ],
  };

  var EASING_PRESETS = {
    smooth: 'cubic-bezier(0.45, 0, 0.55, 1)',
    gentle: 'cubic-bezier(0.76, 0, 0.24, 1)',
    snappy: 'cubic-bezier(0.3, 0, 0.2, 1)',
  };

  var BAND_CORE_RATIO = 0.44;
  var FALLBACK_TEXT_WIDTH_PX = 96;
  var MAX_SPREAD_PX = 48;
  var SPREAD_MID_RATIO = 0.72;
  var BASE_FONT_PX = 14;
  var VIEWPORT_ROOT_MARGIN = '160px';
  var SCROLL_IDLE_MS = 120;

  function buildBandGradient(stops, angle) {
    var sorted = stops.slice().sort(function (a, b) {
      return a.position - b.position;
    });
    var first = (sorted[0] && sorted[0].color) || 'white';
    var last = (sorted[sorted.length - 1] && sorted[sorted.length - 1].color) || 'white';
    var core = sorted
      .map(function (stop) {
        var factor = (stop.position - 0.5) * 2 * BAND_CORE_RATIO;
        return stop.color + ' calc(50% + var(--gs-spread-mid) * ' + factor.toFixed(4) + ')';
      })
      .join(', ');
    return [
      'linear-gradient(' + angle + 'deg',
      'var(--gs-base) calc(50% - var(--gs-spread))',
      'color-mix(in oklab, var(--gs-base) 42%, ' + first + ') calc(50% - var(--gs-spread-mid))',
      core,
      'color-mix(in oklab, var(--gs-base) 42%, ' + last + ') calc(50% + var(--gs-spread-mid))',
      'var(--gs-base) calc(50% + var(--gs-spread)))',
    ].join(', ');
  }

  function supportsBackgroundClipText() {
    if (!window.CSS || typeof window.CSS.supports !== 'function') return false;
    return window.CSS.supports('background-clip', 'text') || window.CSS.supports('-webkit-background-clip', 'text');
  }

  function prefersReducedMotion() {
    return typeof window.matchMedia === 'function' && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  // Gates le sweep sur : dans le viewport (IntersectionObserver) ET page
  // visible ET rien en train de scroller. `onChange(active)` reçoit l'état
  // combiné. Retourne une fonction de nettoyage.
  function observeShimmerActive(el, opts, onChange) {
    var inViewport = !opts.pauseWhenOffscreen || !('IntersectionObserver' in window);
    var pageVisible = !document.hidden;
    var notScrolling = true;

    function compute() {
      onChange(inViewport && pageVisible && notScrolling);
    }

    var io;
    if (opts.pauseWhenOffscreen && 'IntersectionObserver' in window) {
      io = new IntersectionObserver(
        function (entries) {
          var entry = entries[entries.length - 1];
          if (!entry) return;
          inViewport = entry.isIntersecting;
          compute();
        },
        { rootMargin: VIEWPORT_ROOT_MARGIN }
      );
      io.observe(el);
    }

    function onVisibility() {
      pageVisible = !document.hidden;
      compute();
    }
    document.addEventListener('visibilitychange', onVisibility);

    var scrollTimer;
    function onScroll() {
      notScrolling = false;
      compute();
      clearTimeout(scrollTimer);
      scrollTimer = setTimeout(function () {
        notScrolling = true;
        compute();
      }, SCROLL_IDLE_MS);
    }
    if (opts.pauseOnScroll) window.addEventListener('scroll', onScroll, { passive: true, capture: true });

    compute();

    return function () {
      if (io) io.disconnect();
      document.removeEventListener('visibilitychange', onVisibility);
      if (opts.pauseOnScroll) window.removeEventListener('scroll', onScroll, { capture: true });
      clearTimeout(scrollTimer);
    };
  }

  function revealNormalText(el) {
    el.style.removeProperty('background-image');
    el.style.removeProperty('-webkit-text-fill-color');
  }

  // Applique le sweep à un élément. `options` : gradient (nom de preset ou
  // tableau de stops), easing, duration (s), spread (px/caractère), angle
  // (deg), pauseBetween (ms), baseColor, pauseOnScroll, pauseWhenOffscreen,
  // respectReducedMotion — mêmes noms/défauts que le composant React fourni.
  function initGradientShimmer(el, options) {
    options = options || {};
    var stops = typeof options.gradient === 'string'
      ? GRADIENT_PRESETS[options.gradient] || GRADIENT_PRESETS.sunrise
      : options.gradient || GRADIENT_PRESETS.sunrise;
    var easingValue = EASING_PRESETS[options.easing] || EASING_PRESETS.smooth;
    var duration = Number.isFinite(options.duration) ? Math.max(0.001, options.duration) : 1.45;
    var spread = Number.isFinite(options.spread) ? Math.max(0, options.spread) : 3;
    var angle = Number.isFinite(options.angle) ? options.angle : 105;
    var pauseBetween = Number.isFinite(options.pauseBetween) ? options.pauseBetween : 1000;
    var baseColor = options.baseColor || 'currentColor';
    var pauseOnScroll = options.pauseOnScroll !== false;
    var pauseWhenOffscreen = options.pauseWhenOffscreen !== false;
    var respectReducedMotion = options.respectReducedMotion !== false;

    var textLength = (el.textContent || '').length || 1;
    var initialSpread = Math.min(textLength * spread, MAX_SPREAD_PX);

    el.style.position = 'relative';
    el.style.display = 'inline-block';
    el.style.backgroundImage = buildBandGradient(stops, angle);
    el.style.backgroundRepeat = 'no-repeat';
    el.style.backgroundSize = '100% 100%';
    el.style.backgroundColor = 'var(--gs-base)';
    el.style.webkitBackgroundClip = 'text';
    el.style.backgroundClip = 'text';
    el.style.webkitTextFillColor = 'transparent';
    el.style.setProperty('--gs-base', baseColor);
    el.style.setProperty('--gs-spread', initialSpread + 'px');
    el.style.setProperty('--gs-spread-mid', initialSpread * SPREAD_MID_RATIO + 'px');

    function measure() {
      var textWidth = el.getBoundingClientRect().width || FALLBACK_TEXT_WIDTH_PX;
      var fontSize = parseFloat(getComputedStyle(el).fontSize) || BASE_FONT_PX;
      var fontScale = fontSize / BASE_FONT_PX;
      var spreadPx = Math.min(textLength * spread * fontScale, MAX_SPREAD_PX * fontScale);
      var layerWidth = Math.max(1, textWidth + spreadPx * 2);
      var start = -spreadPx - layerWidth / 2;
      var end = textWidth + spreadPx - layerWidth / 2;
      var durationMs = duration * 1000;
      el.style.setProperty('--gs-spread', spreadPx + 'px');
      el.style.setProperty('--gs-spread-mid', spreadPx * SPREAD_MID_RATIO + 'px');
      el.style.backgroundSize = layerWidth + 'px 100%';
      return { start: start, end: end, durationMs: durationMs };
    }

    if (!supportsBackgroundClipText()) {
      revealNormalText(el);
      return function () {};
    }

    measure();

    if ((respectReducedMotion && prefersReducedMotion()) || typeof el.animate !== 'function') {
      return function () {};
    }

    var anim = null;
    var pauseTimer;
    var active = true;
    var cancelled = false;

    function runSweep() {
      if (cancelled) return;
      var m = measure();
      var next = el.animate(
        [{ backgroundPosition: m.start + 'px center' }, { backgroundPosition: m.end + 'px center' }],
        { duration: m.durationMs, easing: easingValue, fill: 'forwards' }
      );
      if (!active) next.pause();
      if (anim) anim.cancel();
      anim = next;
      next.onfinish = function () {
        pauseTimer = setTimeout(runSweep, Math.max(0, pauseBetween));
      };
    }

    var stopVisibility = observeShimmerActive(
      el,
      { pauseOnScroll: pauseOnScroll, pauseWhenOffscreen: pauseWhenOffscreen },
      function (next) {
        active = next;
        if (anim) {
          if (active) anim.play();
          else anim.pause();
        }
      }
    );

    runSweep();

    return function () {
      cancelled = true;
      if (anim) anim.cancel();
      clearTimeout(pauseTimer);
      stopVisibility();
    };
  }

  // Auto-init déclaratif : <span data-gradient-shimmer data-gradient-preset="sunrise">...</span>
  document.querySelectorAll('[data-gradient-shimmer]').forEach(function (el) {
    initGradientShimmer(el, {
      gradient: el.getAttribute('data-gradient-preset') || 'sunrise',
      easing: el.getAttribute('data-gradient-easing') || 'smooth',
      duration: parseFloat(el.getAttribute('data-gradient-duration')),
      spread: parseFloat(el.getAttribute('data-gradient-spread')),
      angle: parseFloat(el.getAttribute('data-gradient-angle')),
      pauseBetween: parseFloat(el.getAttribute('data-gradient-pause')),
    });
  });
})();
