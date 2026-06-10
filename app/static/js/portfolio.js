/* ============================================================================
   PORTFOLIO.JS — Slide 3: load, render, autoplay, modal, filter, load-more
   ============================================================================ */

var Portfolio = (function () {

  var PER_PAGE = 4;
  var useTestData = false;

  var allItems = [];
  var visibleIds = [];
  var currentPage = 1;
  var currentCategory = 'all';
  var hasMore = false;
  var modalIndex = 0;

  var siteAutoplay = true;
  var siteColumns  = 2;

  var grid, filtersEl, loadMoreBtn, emptyEl;
  var modalEl, modalOverlay, modalClose, modalPrev, modalNext, modalPrevM, modalNextM, modalCloseM;
  var modalVideo, modalIframe, modalVideoWrap, modalTitle, modalSubtitle, modalTags, modalDesc;
  var relatedEl, relatedTrack;

  // ── autoplay observer ──────────────────────────────────────────────────
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      var vid = entry.target;
      if (entry.isIntersecting) {
        vid.play().catch(function () {});
      } else {
        vid.pause();
      }
    });
  }, { threshold: 0.3 });

  // ── utility ────────────────────────────────────────────────────────────
  function escapeHtml(str) {
    return String(str || '')
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function extractYoutubeId(url) {
    if (!url) return null;
    var m = url.match(/(?:youtube\.com\/(?:watch\?.*v=|shorts\/|embed\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
    return m ? m[1] : null;
  }

  function youtubeThumbnail(ytId) {
    return 'https://img.youtube.com/vi/' + ytId + '/hqdefault.jpg';
  }

  function extractVimeoId(url) {
    if (!url) return null;
    var m = url.match(/vimeo\.com\/(?:video\/)?(\d+)/);
    return m ? m[1] : null;
  }

  // ── filters ────────────────────────────────────────────────────────────
  function syncFilters() {
    if (!filtersEl) return;

    // collect all unique category names from categories[] (or fallback to category)
    var seen = {};
    allItems.forEach(function (item) {
      var cats = Array.isArray(item.categories) && item.categories.length
        ? item.categories
        : (item.category ? [item.category] : []);
      cats.forEach(function (cat) { if (cat) seen[cat] = true; });
    });

    Object.keys(seen).forEach(function (cat) {
      if (filtersEl.querySelector('[data-filter="' + CSS.escape(cat) + '"]')) return;
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'filter-btn';
      btn.dataset.filter = cat;
      btn.textContent = cat;
      btn.addEventListener('click', function () { setActiveFilter(cat); });
      filtersEl.appendChild(btn);
    });
  }

  function setActiveFilter(category) {
    currentCategory = category;
    filtersEl.querySelectorAll('.filter-btn').forEach(function (btn) {
      btn.classList.toggle('filter-btn--active', btn.dataset.filter === category);
    });
    applyFilter(category);
    rebuildModalIds();
  }

  // ── build card ─────────────────────────────────────────────────────────
  function buildCard(item) {
    var art = document.createElement('article');
    art.className = 'portfolio-card';
    // store all categories as JSON for multi-tag filtering
    var cats = Array.isArray(item.categories) && item.categories.length
      ? item.categories : (item.category ? [item.category] : []);
    art.dataset.categories = JSON.stringify(cats);
    art.dataset.category = item.category || '';
    art.dataset.id = item.id;

    var wrap = document.createElement('div');
    wrap.className = 'portfolio-card__image-wrap';

    var ytId = item.youtube_id || extractYoutubeId(item.video_url);
    var isYoutube = item.video_type === 'youtube' || !!ytId;
    var vimeoId = item.vimeo_id || extractVimeoId(item.video_url);
    var isVimeo = item.video_type === 'vimeo' || !!vimeoId;

    if (isYoutube && ytId) {
      var img = document.createElement('img');
      img.className = 'portfolio-card__img portfolio-card__img--youtube';
      img.src = youtubeThumbnail(ytId);
      img.alt = escapeHtml(item.title);
      img.loading = 'lazy';
      wrap.appendChild(img);
    } else if (isVimeo && item.thumbnail) {
      var img = document.createElement('img');
      img.className = 'portfolio-card__img portfolio-card__img--vimeo';
      img.src = item.thumbnail;
      img.alt = escapeHtml(item.title);
      img.loading = 'lazy';
      wrap.appendChild(img);
    } else if (item.video_url && siteAutoplay) {
      var vid = document.createElement('video');
      vid.className = 'portfolio-card__video';
      vid.src = item.video_url;
      vid.muted = true;
      vid.loop = true;
      vid.setAttribute('playsinline', '');
      vid.setAttribute('preload', 'none');
      wrap.appendChild(vid);
      observer.observe(vid);
    } else if (item.thumbnail || item.video_url) {
      var img = document.createElement('img');
      img.className = 'portfolio-card__img';
      img.src = item.thumbnail || '';
      img.alt = escapeHtml(item.title);
      img.loading = 'lazy';
      wrap.appendChild(img);
    } else {
      wrap.style.background = '#1a1a1a';
    }

    var h3 = document.createElement('h3');
    h3.className = 'portfolio-card__title';
    h3.textContent = item.title || '';

    var p = document.createElement('p');
    p.className = 'portfolio-card__subtitle';
    p.textContent = item.subtitle || '';

    art.appendChild(wrap);
    art.appendChild(h3);
    art.appendChild(p);

    art.addEventListener('click', function () { openModal(item.id); });
    return art;
  }

  // ── render ─────────────────────────────────────────────────────────────
  function renderItems(items, append) {
    if (!grid) return;
    if (!append) {
      grid.querySelectorAll('video').forEach(function (v) { observer.unobserve(v); v.pause(); });
      grid.innerHTML = '';
    }
    items.forEach(function (item) { grid.appendChild(buildCard(item)); });
    rebuildVisibleIds();
  }

  function rebuildVisibleIds() {
    visibleIds = [];
    grid.querySelectorAll('.portfolio-card').forEach(function (el) {
      if (el.style.display !== 'none') visibleIds.push(el.dataset.id);
    });
  }

  // Full list for modal navigation — all items matching current filter, regardless of pagination
  var modalIds = [];

  function rebuildModalIds() {
    modalIds = allItems
      .filter(function (item) {
        if (currentCategory === 'all') return true;
        var cats = Array.isArray(item.categories) ? item.categories : (item.category ? [item.category] : []);
        return cats.indexOf(currentCategory) !== -1 || item.category === currentCategory;
      })
      .map(function (item) { return item.id; });
  }

  // ── filter ─────────────────────────────────────────────────────────────
  function applyFilter(category) {
    grid.querySelectorAll('.portfolio-card').forEach(function (card) {
      var cats = [];
      try { cats = JSON.parse(card.dataset.categories || '[]'); } catch (e) {}
      var visible = category === 'all' || cats.indexOf(category) !== -1 || card.dataset.category === category;
      card.style.display = visible ? '' : 'none';
      var vid = card.querySelector('video');
      if (vid && !visible) vid.pause();
    });

    var anyVisible = !!grid.querySelector('.portfolio-card:not([style*="display: none"])');
    if (emptyEl) {
      anyVisible ? emptyEl.setAttribute('hidden', '') : emptyEl.removeAttribute('hidden');
    }
    rebuildVisibleIds();
  }

  // ── load from API ──────────────────────────────────────────────────────
  async function loadPage(page, append) {
    var cat = currentCategory && currentCategory !== 'all'
      ? '&category=' + encodeURIComponent(currentCategory) : '';
    var test = useTestData ? '&test=1' : '';
    // load all items without per_page limit to build complete filter list
    var url = '/api/portfolio?page=' + page + '&per_page=' + PER_PAGE + cat + test;

    try {
      var res = await fetch(url);
      if (!res.ok) throw new Error(res.statusText);
      var data = await res.json();
      var items = data.items || [];
      hasMore = Boolean(data.has_more);

      items.forEach(function (item) {
        if (!allItems.find(function (i) { return i.id === item.id; })) {
          allItems.push(item);
        }
      });

      syncFilters();
      renderItems(items, append);
      updateLoadMoreBtn();
    } catch (e) {
      console.error('Portfolio load error:', e);
    }
  }

  // load ALL items once to populate filter buttons fully
  async function preloadAllForFilters() {
    try {
      var test = useTestData ? '&test=1' : '';
      var res = await fetch('/api/portfolio?page=1&per_page=100' + test);
      if (!res.ok) return;
      var data = await res.json();
      var items = data.items || [];
      items.forEach(function (item) {
        if (!allItems.find(function (i) { return i.id === item.id; })) {
          allItems.push(item);
        }
      });
      syncFilters();
      rebuildModalIds();
    } catch (e) {}
  }

  function updateLoadMoreBtn() {
    if (!loadMoreBtn) return;
    loadMoreBtn.style.display = hasMore ? '' : 'none';
    loadMoreBtn.disabled = false;
  }

  // ── modal ──────────────────────────────────────────────────────────────
  function openModal(itemId, preloadedItem) {
    if (preloadedItem && preloadedItem.hidden) {
      showModalItem(preloadedItem);
      return;
    }
    rebuildModalIds();
    var idx = modalIds.indexOf(itemId);
    showModalAt(idx === -1 ? 0 : idx);
  }

  function showModalItem(item) {
    if (!modalEl) return;
    modalIndex = -1;
    populateModal(item);
    modalEl.removeAttribute('hidden');
    document.body.style.overflow = 'hidden';
  }

  function showModalAt(idx) {
    if (!modalEl) return;
    modalIndex = idx;

    var item = allItems.find(function (i) { return i.id === modalIds[idx]; });
    if (!item) return;

    populateModal(item);

    var isFirst = idx === 0;
    var isLast  = idx === modalIds.length - 1;
    modalPrev.disabled = isFirst;
    modalNext.disabled = isLast;
    if (modalPrevM) modalPrevM.disabled = isFirst;
    if (modalNextM) modalNextM.disabled = isLast;

    modalEl.removeAttribute('hidden');
    document.body.style.overflow = 'hidden';
  }

  function populateModal(item) {
    document.querySelectorAll('.portfolio-card video').forEach(function (v) { v.pause(); });

    modalTitle.textContent    = item.title || '';
    modalSubtitle.textContent = item.subtitle || '';
    modalDesc.innerHTML       = item.description || '';

    modalTags.innerHTML = '';
    var tags = Array.isArray(item.tags) ? item.tags : (item.tag ? [item.tag] : []);
    tags.forEach(function (tag) {
      var span = document.createElement('span');
      span.className = 'pf-modal__tag';
      span.textContent = tag;
      modalTags.appendChild(span);
    });

    var ytId = item.youtube_id || extractYoutubeId(item.video_url);
    var isYoutube = item.video_type === 'youtube' || !!ytId;
    var vimeoId = item.vimeo_id || extractVimeoId(item.video_url);
    var isVimeo = item.video_type === 'vimeo' || !!vimeoId;

    if (isYoutube && ytId) {
      modalVideo.style.display = 'none';
      modalVideo.pause();
      modalVideo.src = '';
      if (!modalIframe) {
        modalIframe = document.createElement('iframe');
        modalIframe.className = 'pf-modal__video pf-modal__iframe';
        modalIframe.setAttribute('allowfullscreen', '');
        modalIframe.setAttribute('allow', 'autoplay; encrypted-media');
        modalIframe.setAttribute('frameborder', '0');
        modalVideoWrap.appendChild(modalIframe);
      }
      modalIframe.src = 'https://www.youtube.com/embed/' + ytId + '?autoplay=1&rel=0';
      modalIframe.style.display = '';
    } else if (isVimeo && vimeoId) {
      modalVideo.style.display = 'none';
      modalVideo.pause();
      modalVideo.src = '';
      if (!modalIframe) {
        modalIframe = document.createElement('iframe');
        modalIframe.className = 'pf-modal__video pf-modal__iframe';
        modalIframe.setAttribute('allowfullscreen', '');
        modalIframe.setAttribute('allow', 'autoplay; fullscreen; picture-in-picture');
        modalIframe.setAttribute('frameborder', '0');
        modalVideoWrap.appendChild(modalIframe);
      }
      modalIframe.src = 'https://player.vimeo.com/video/' + vimeoId + '?autoplay=1&title=0&byline=0&portrait=0';
      modalIframe.style.display = '';
    } else {
      if (modalIframe) { modalIframe.src = ''; modalIframe.style.display = 'none'; }
      modalVideo.style.display = '';
      modalVideo.src = item.video_url || '';
      if (item.video_url) { modalVideo.load(); modalVideo.play().catch(function () {}); }
    }

    renderRelated(item);
  }

  var hiddenItemCache = {};

  function fetchHiddenItem(rid) {
    if (hiddenItemCache[rid]) return Promise.resolve(hiddenItemCache[rid]);
    return fetch('/api/portfolio/' + rid)
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        if (data) hiddenItemCache[rid] = data;
        return data;
      })
      .catch(function () { return null; });
  }

  function renderRelated(item) {
    if (!relatedEl || !relatedTrack) return;
    var related = Array.isArray(item.related) ? item.related : [];

    if (!related.length) {
      relatedEl.setAttribute('hidden', '');
      return;
    }

    relatedTrack.innerHTML = '';
    relatedEl.setAttribute('hidden', '');

    var promises = related.map(function (rid) {
      var rel = allItems.find(function (i) { return i.id === rid; });
      if (rel) return Promise.resolve(rel);
      return fetchHiddenItem(rid);
    });

    Promise.all(promises).then(function (rels) {
      relatedTrack.innerHTML = '';
      var anyVisible = false;
      rels.forEach(function (rel, idx) {
        if (!rel) return;
        var rid = related[idx];
        anyVisible = true;

        var ytId = rel.youtube_id || extractYoutubeId(rel.video_url);
        var isYt = rel.video_type === 'youtube' || !!ytId;
        var thumbSrc = isYt && ytId
          ? youtubeThumbnail(ytId)
          : (rel.thumbnail || rel.thumb_url || '');

        var li = document.createElement('li');
        li.className = 'pf-modal__related-item';

        var imgWrap = document.createElement('div');
        imgWrap.className = 'pf-modal__related-thumb';
        if (thumbSrc) {
          var img = document.createElement('img');
          img.src = thumbSrc;
          img.alt = escapeHtml(rel.title);
          img.loading = 'lazy';
          imgWrap.appendChild(img);
        }

        var title = document.createElement('span');
        title.className = 'pf-modal__related-title';
        title.textContent = rel.title || '';

        li.appendChild(imgWrap);
        li.appendChild(title);
        li.addEventListener('click', function () { openModal(rid, rel); });
        relatedTrack.appendChild(li);
      });

      if (anyVisible) {
        relatedEl.removeAttribute('hidden');
        relatedTrack.scrollLeft = 0;
      }
    });
  }

  function closeModal() {
    if (!modalEl) return;
    modalVideo.pause();
    modalVideo.src = '';
    if (modalIframe) { modalIframe.src = ''; modalIframe.style.display = 'none'; }
    modalVideo.style.display = '';
    modalEl.setAttribute('hidden', '');
    document.body.style.overflow = '';

    document.querySelectorAll('.portfolio-card').forEach(function (card) {
      if (card.style.display === 'none') return;
      var vid = card.querySelector('video');
      if (!vid) return;
      var r = card.getBoundingClientRect();
      if (r.top < window.innerHeight && r.bottom > 0) vid.play().catch(function () {});
    });
  }

  // ── init ───────────────────────────────────────────────────────────────
  function init() {
    grid       = document.getElementById('portfolio-grid');
    filtersEl  = document.getElementById('portfolio-filters');
    loadMoreBtn= document.getElementById('load-more-btn');
    emptyEl    = document.getElementById('portfolio-empty');

    if (grid) {
      siteAutoplay = grid.dataset.autoplay !== 'false';
      siteColumns  = parseInt(grid.dataset.columns) || 2;
      if (siteColumns === 1) grid.classList.add('slide-3__grid--single');
    }

    modalEl       = document.getElementById('pf-modal');
    modalOverlay  = document.getElementById('pf-modal-overlay');
    modalClose    = document.getElementById('pf-modal-close');
    modalPrev     = document.getElementById('pf-modal-prev');
    modalNext     = document.getElementById('pf-modal-next');
    modalCloseM   = document.getElementById('pf-modal-close-m');
    modalPrevM    = document.getElementById('pf-modal-prev-m');
    modalNextM    = document.getElementById('pf-modal-next-m');
    modalVideo     = document.getElementById('pf-modal-video');
    modalVideoWrap = modalVideo ? modalVideo.closest('.pf-modal__video-wrap') : null;
    modalIframe    = null;
    relatedEl      = document.getElementById('pf-modal-related');
    relatedTrack   = document.getElementById('pf-related-track');
    modalTitle    = document.getElementById('pf-modal-title');
    modalSubtitle = document.getElementById('pf-modal-subtitle');
    modalTags     = document.getElementById('pf-modal-tags');
    modalDesc     = document.getElementById('pf-modal-desc');

    if (!grid) return;

    // wire «Все» button
    if (filtersEl) {
      filtersEl.querySelector('[data-filter="all"]').addEventListener('click', function () {
        setActiveFilter('all');
      });
    }

    // preload all items to build complete filter list, then load first page
    preloadAllForFilters().then(function () {
      loadPage(1, false);
    });

    if (loadMoreBtn) {
      loadMoreBtn.addEventListener('click', function () {
        loadMoreBtn.disabled = true;
        currentPage += 1;
        loadPage(currentPage, true);
      });
    }

    if (modalOverlay) modalOverlay.addEventListener('click', closeModal);
    if (modalClose)   modalClose.addEventListener('click', closeModal);
    if (modalCloseM)  modalCloseM.addEventListener('click', closeModal);
    if (modalPrev)    modalPrev.addEventListener('click', function () {
      if (modalIndex > 0) showModalAt(modalIndex - 1);
    });
    if (modalNext)    modalNext.addEventListener('click', function () {
      if (modalIndex < modalIds.length - 1) showModalAt(modalIndex + 1);
    });
    if (modalPrevM)   modalPrevM.addEventListener('click', function () {
      if (modalIndex > 0) showModalAt(modalIndex - 1);
    });
    if (modalNextM)   modalNextM.addEventListener('click', function () {
      if (modalIndex < visibleIds.length - 1) showModalAt(modalIndex + 1);
    });

    document.addEventListener('keydown', function (e) {
      if (!modalEl || modalEl.hasAttribute('hidden')) return;
      if (e.key === 'Escape') closeModal();
      if (e.key === 'ArrowLeft'  && modalIndex > 0) showModalAt(modalIndex - 1);
      if (e.key === 'ArrowRight' && modalIndex < visibleIds.length - 1) showModalAt(modalIndex + 1);
    });
  }

  return {
    init: init,
    setTestMode: function (on) {
      useTestData = on;
      allItems = [];
      currentPage = 1;
      // reset filters to just «Все»
      if (filtersEl) {
        filtersEl.querySelectorAll('.filter-btn:not([data-filter="all"])').forEach(function (b) { b.remove(); });
        setActiveFilter('all');
      }
      preloadAllForFilters().then(function () { loadPage(1, false); });
    },
  };
})();

document.addEventListener('DOMContentLoaded', function () {
  Portfolio.init();
});
