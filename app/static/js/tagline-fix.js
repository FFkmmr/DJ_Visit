/* ============================================================================
   TAGLINE-FIX.JS — Synchronize 4 tagline items for seamless loop
   ============================================================================ */

document.addEventListener('DOMContentLoaded', function () {
  // Find the tagline container
  const taglineContainer = document.querySelector('.slide-1__tagline');
  if (!taglineContainer) return;

  // Get all tagline items
  const items = taglineContainer.querySelectorAll('.marquee__item--tagline');
  if (items.length < 4) {
    console.warn('Tagline: Expected at least 4 items, found', items.length);
    return;
  }

  const item1 = items[0];

  function syncTagline() {
    // Get actual width of first tagline item
    const taglineWidth = item1.offsetWidth;
    
    if (taglineWidth <= 0) {
      requestAnimationFrame(syncTagline);
      return;
    }

    // Set CSS variable with actual width for all items to use
    const taglineWidthPx = taglineWidth + 'px';
    document.documentElement.style.setProperty('--tagline-width', taglineWidthPx);
    
    // Animation duration: 16s (5× faster than 80s)
    const duration = 16;
    items.forEach(item => {
      item.style.setProperty('--tagline-duration', duration + 's');
    });
    
    console.log('Tagline synced (4 items):', { taglineWidth, duration });
  }

  // Initial sync
  syncTagline();

  // Re-sync on window load and resize
  window.addEventListener('load', syncTagline);
  window.addEventListener('resize', syncTagline);
  
  // Wait for fonts to load
  setTimeout(syncTagline, 1000);
});
