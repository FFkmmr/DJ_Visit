/* ============================================================================
   MARQUEE.JS — Pause CSS marquee animation on hover
   Animation is CSS-driven; this file only toggles animationPlayState.
   ============================================================================ */

document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.marquee__track').forEach(function (track) {
    var wrapper = track.closest('.marquee');
    if (!wrapper) return;

    wrapper.addEventListener('mouseenter', function () {
      track.style.animationPlayState = 'paused';
    });

    wrapper.addEventListener('mouseleave', function () {
      track.style.animationPlayState = 'running';
    });
  });
});
