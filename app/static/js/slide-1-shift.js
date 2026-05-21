// slide-1-shift.js — keep `.slide-1__info` right edge at least 75px from viewport
(function () {
  var photo, info, container;
  var disabledWidth = 1000;
  var marginRight = 50; // minimum gap to keep from right edge
  var rafId = null;

  function update() {
    if (!photo || !info) return;
    var vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
    if (vw <= disabledWidth) {
      photo.style.transform = '';
      info.style.transform = '';
      return;
    }

    var prevPhotoTransform = photo.style.transform;
    var prevInfoTransform = info.style.transform;
    photo.style.transform = '';
    info.style.transform = '';

    var infoRect = info.getBoundingClientRect();
    var infoRight = infoRect.right; // distance from viewport left to right edge
    var gap = vw - infoRight; // pixels between info right edge and viewport right edge
    var effectiveMargin = vw <= 1350 ? 0 : marginRight;

    if (gap < effectiveMargin) {
      var shift = Math.ceil(effectiveMargin - gap);
      var transformValue = 'translateX(' + -shift + 'px)';
      photo.style.transform = transformValue;
      info.style.transform = transformValue;
    } else {
      photo.style.transform = '';
      info.style.transform = '';
    }

    if (photo.style.transform === prevPhotoTransform && info.style.transform === prevInfoTransform) {
      return;
    }
  }

  function scheduleUpdate() {
    if (rafId) cancelAnimationFrame(rafId);
    rafId = requestAnimationFrame(update);
  }

  document.addEventListener('DOMContentLoaded', function () {
    photo = document.querySelector('.slide-1__lines');
    info = document.querySelector('.slide-1__info');
    container = document.querySelector('.slide-1');
    if (!photo || !info || !container) return;

    photo.style.willChange = 'transform';
    info.style.willChange = 'transform';
    photo.style.transition = 'none';
    info.style.transition = 'none';

    // initial update and on resize/orientation change
    update();
    window.addEventListener('resize', scheduleUpdate, { passive: true });
    window.addEventListener('orientationchange', scheduleUpdate, { passive: true });
  });
})();
