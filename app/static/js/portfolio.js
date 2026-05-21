/* ============================================================================
   PORTFOLIO.JS — Filter + Load More for Slide 3
   - Cards for first page are rendered server-side by Jinja2.
   - "Load More" fetches /api/portfolio?page=N&category=X and appends cards.
   - Alpine.js component `portfolioFilter()` toggles active filter state.
   ============================================================================ */

// ── Alpine component: filter state ─────────────────────────────────────────
window.portfolioFilter = function () {
  return {
    activeFilter: 'all',

    setFilter(category) {
      this.activeFilter = category;
      applyFilterToGrid(category);
    },
  };
};

// ── Filter visible cards in the grid by data-category ──────────────────────
function applyFilterToGrid(category) {
  const grid = document.getElementById('portfolio-grid');
  const empty = document.getElementById('portfolio-empty');
  if (!grid) return;

  const cards = grid.querySelectorAll('.portfolio-card');
  let visibleCount = 0;

  cards.forEach((card) => {
    const cat = card.dataset.category || '';
    const visible = category === 'all' || cat === category;
    card.style.display = visible ? '' : 'none';
    if (visible) visibleCount += 1;
  });

  if (empty) {
    if (visibleCount === 0) {
      empty.removeAttribute('hidden');
    } else {
      empty.setAttribute('hidden', '');
    }
  }
}

// ── Load-more (paginated fetch) ────────────────────────────────────────────
(function () {
  let currentPage = 1;
  const perPage = 4;

  const grid = document.getElementById('portfolio-grid');
  const loadMoreBtn = document.getElementById('load-more-btn');

  if (!grid) return;

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function buildCard(item) {
    const art = document.createElement('article');
    art.className = 'portfolio-card';
    art.dataset.category = item.category || '';

    const title = escapeHtml(item.title || '');
    const subtitle = escapeHtml(item.subtitle || item.client || '');
    const thumbnail = escapeHtml(item.thumbnail || item.thumb_url || item.img || '');

    art.innerHTML =
      '<div class="portfolio-card__image-wrap">' +
        '<img src="' + thumbnail + '" alt="' + title + '" class="portfolio-card__img" loading="lazy">' +
      '</div>' +
      '<h3 class="portfolio-card__title">' + title + '</h3>' +
      '<p class="portfolio-card__subtitle">' + subtitle + '</p>';
    return art;
  }

  async function loadMore(category) {
    currentPage += 1;
    const cat = category && category !== 'all'
      ? '&category=' + encodeURIComponent(category)
      : '';

    try {
      const res = await fetch(
        '/api/portfolio?page=' + currentPage + '&per_page=' + perPage + cat
      );
      if (!res.ok) throw new Error(res.statusText);
      const data = await res.json();
      const items = Array.isArray(data) ? data : (data.items || []);
      items.forEach((item) => grid.appendChild(buildCard(item)));

      const activeBtn = document.querySelector('.filter-btn--active');
      const activeCategory = activeBtn ? (activeBtn.dataset.filter || 'all') : 'all';
      applyFilterToGrid(activeCategory);

      const hasMore = Array.isArray(data) ? false : Boolean(data.has_more);
      if (!hasMore && loadMoreBtn) {
        loadMoreBtn.style.display = 'none';
      } else if (loadMoreBtn) {
        loadMoreBtn.disabled = false;
      }
    } catch (e) {
      if (loadMoreBtn) {
        loadMoreBtn.disabled = false;
      }
      const empty = document.getElementById('portfolio-empty');
      if (empty) {
        empty.removeAttribute('hidden');
        empty.textContent = 'Не удалось загрузить работы. Попробуйте позже.';
      }
    }
  }

  if (loadMoreBtn) {
    loadMoreBtn.addEventListener('click', function () {
      const activeBtn = document.querySelector('.filter-btn--active');
      const category = activeBtn ? activeBtn.dataset.filter : 'all';
      loadMoreBtn.disabled = true;
      loadMore(category);
    });
  }
})();
