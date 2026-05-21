/* ============================================================================
   APP.JS — Alpine.js root state + smooth anchor scrolling
   ============================================================================ */

function appState() {
  return {};
}

// Smooth scroll for anchor links (e.g. header nav, logo)
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (event) {
      var href = anchor.getAttribute('href');
      if (!href || href === '#') return;

      var targetId = href.slice(1);
      var target = document.getElementById(targetId);
      if (!target) return;

      event.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
});
