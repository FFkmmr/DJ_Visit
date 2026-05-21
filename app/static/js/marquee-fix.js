/* ============================================================================
   MARQUEE-FIX.JS — Synchronize 4 marquee items for seamless loop
   ============================================================================ */

document.addEventListener('DOMContentLoaded', function () {
  // Find the marquee container
  const marqueeContainer = document.querySelector('.slide-1__marquee');
  if (!marqueeContainer) return;

  // Get all items
  const items = marqueeContainer.querySelectorAll('.marquee__item--bottom');
  if (items.length < 4) {
    console.warn('Marquee: Expected at least 4 items, found', items.length);
    return;
  }

  const item1 = items[0];

  function syncMarquee() {
    // Get actual width of first item (content width)
    const itemWidth = item1.offsetWidth;
    
    if (itemWidth <= 0) {
      requestAnimationFrame(syncMarquee);
      return;
    }

    // Set CSS variable with actual width for all items to use
    const itemWidthPx = itemWidth + 'px';
    document.documentElement.style.setProperty('--marquee-item-width', itemWidthPx);
    
    // Animation duration: 80s (3× faster than 240s)
    const duration = 80;
    items.forEach(item => {
      item.style.setProperty('--duration', duration + 's');
    });
    
    console.log('Marquee synced (4 items):', { itemWidth, duration });
  }

  // Initial sync
  syncMarquee();

  // Re-sync on window load and resize
  window.addEventListener('load', syncMarquee);
  window.addEventListener('resize', syncMarquee);
  
  // Wait for fonts to load
  setTimeout(syncMarquee, 1000);
});




