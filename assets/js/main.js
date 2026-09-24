(function () {
  var toggle = document.querySelector('.nav__toggle');
  var nav = document.querySelector('.nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var isOpen = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });
    nav.querySelectorAll('.nav__mobile a').forEach(function (link) {
      link.addEventListener('click', function () {
        nav.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Les chats animés (DA Paw) : lus seulement quand ils sont à l'écran, jamais en mouvement réduit (la première
  // image, déjà servie en affiche, reste posée).
  var loops = document.querySelectorAll('video.paw-loop');
  loops.forEach(function (video) {
    if (prefersReducedMotion) {
      video.removeAttribute('autoplay');
      video.pause();
    }
  });
  if (loops.length && !prefersReducedMotion && 'IntersectionObserver' in window) {
    var loopObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          var playing = entry.target.play();
          if (playing && playing.catch) playing.catch(function () {});
        } else {
          entry.target.pause();
        }
      });
    }, { threshold: 0.1 });
    loops.forEach(function (video) { loopObserver.observe(video); });
  }
  var revealEls = document.querySelectorAll('.reveal');
  if (revealEls.length && !prefersReducedMotion && 'IntersectionObserver' in window) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15 }
    );
    revealEls.forEach(function (el) {
      observer.observe(el);
    });
  } else {
    revealEls.forEach(function (el) {
      el.classList.add('is-visible');
    });
  }
})();
