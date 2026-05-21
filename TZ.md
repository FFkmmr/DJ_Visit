# Technical Specification (TZ)

## Overview

DJ_Visit is a one-page web business card (визитка) for a music producer. Single-page scroll layout, 7 sections, sophisticated animations and interactions.

## Phases

### Phase 1: Bootstrap & Header + Slide 1

**Scope:** Project infrastructure, header navigation, hero slide

**Deliverables:**
- ✅ Project structure (docs/, CLAUDE.md, Flask skeleton)
- ✅ Docker setup (docker-compose.dev.yml, Dockerfile)
- ✅ Flask app factory (app/__init__.py, routes.py, config.py)
- ✅ Header component (HTML + CSS)
- ✅ Slide 1 hero (HTML + CSS, background video placeholder)
- ✅ Marquee text (bottom marquee, CSS animation)
- ✅ Basic Alpine.js navigation (scroll to slide)

**Acceptance Criteria:**
- [ ] Local dev environment: `docker-compose up` works
- [ ] Header visible with clickable navigation
- [ ] Slide 1 displays with layout (wave shape, photo area, marquee)
- [ ] No errors in console, responsive to desktop
- [ ] No animations yet (just layout)

---

### Phase 2: Slides 2-5 Implementation

**Scope:** All remaining slides (2-5) with content structure

**Deliverables:**
- ✅ Slide 2 (Почему я?) - Text block + typing animation
- ✅ Slide 3 (Портфолио) - Video cards grid, sticky filter menu, "Load More" button
- ✅ Slide 4 (Актёрский опыт) - Video player + custom controls + modal
- ✅ Slide 5 (Как рождается результат) - Horizontal scroll sections
- ✅ Footer - Contact info + copyright + logo

**Acceptance Criteria:**
- [ ] All 7 slides visible (desktop scroll view)
- [ ] Slide navigation works (header links + smooth scroll)
- [ ] Portfolio data structure working (/api/portfolio)
- [ ] Video player basic functionality (play/pause)
- [ ] No animations yet (just layout + data)

---

### Phase 3: Animations & Interactivity

**Scope:** All animations, lazy-loading, interactive effects

**Deliverables:**
- ✅ Typing animation (Slide 2) - Alpine.js + Vanilla JS
- ✅ Video lazy-loading (Slides 1, 3, 4) - Intersection Observer
- ✅ Marquee animations (Slide 1 bottom) - CSS @keyframes
- ✅ Custom video player controls - HTML5 API + Vanilla JS
- ✅ Modal for fullscreen video - Alpine.js
- ✅ Horizontal scroll (Slide 5) - CSS scroll-snap or JS

**Acceptance Criteria:**
- [ ] All animations smooth (60fps)
- [ ] Video lazy-loading working (dev tools Network tab)
- [ ] Typing animation cycles correctly
- [ ] Video player modal opens/closes
- [ ] Horizontal scroll feels natural
- [ ] Parallax/scroll effects (if in design)

---

### Phase 4: Responsive Design & Deployment

**Scope:** Tablet/mobile adaptations, Railway deployment

**Deliverables:**
- ✅ Tablet breakpoint (768px) - reflow to 2-column or stacked layouts
- ✅ Mobile breakpoint (640px) - single column, hamburger menu (if needed)
- ✅ Image optimization for mobile
- ✅ Touch interactions (if needed)
- ✅ Railway deployment setup (.env.prod, gunicorn config)
- ✅ Custom domain configuration
- ✅ SSL certificate (Railway automatic)
- ✅ Health checks + monitoring setup

**Acceptance Criteria:**
- [ ] Tablet view looks good (manual testing)
- [ ] Mobile view functional (manual testing on device or emulator)
- [ ] Deployed to Railway with custom domain
- [ ] HTTPS working
- [ ] Page load time < 3s on 4G
- [ ] Lighthouse score > 80

---

## Constraints & Notes

### Performance

- Background videos: H.264 codec, <10MB each (for fast load)
- Images: Optimized, responsive (srcset for tablet/mobile)
- Lazy-loading: Videos/images only load when in viewport
- CSS: No framework (custom), <50KB total

### Browser Support

- Modern browsers only (Chrome, Firefox, Safari, Edge latest)
- ES2020+ JavaScript
- No IE11 support

### Accessibility

- Semantic HTML5
- ARIA labels where needed
- Keyboard navigation (tab through buttons)
- Color contrast ratios (WCAG AA)

### Responsive Strategy

**Desktop (1920px):** Full design as Figma
**Tablet (768px):** 
  - Slide 1: Stack photo + info vertically
  - Slide 3: 2-column grid instead of 4
  - Slide 5: Horizontal scroll → vertical stack
**Mobile (640px):**
  - All single column
  - Reduced padding/margins
  - Hamburger nav (if needed)
  - Vertical video stacking

---

## File Structure Overview

```
DJ_Visit/
├── CLAUDE.md (project vision)
├── TZ.md (this file)
├── docs/ (architecture & module specs)
├── app/ (Flask application)
│   ├── __init__.py
│   ├── routes.py
│   ├── config.py
│   ├── templates/
│   └── static/
├── data/portfolio/ (video data)
├── requirements.txt
├── Dockerfile
├── docker-compose.dev.yml
└── docker-compose.prod.yml
```

---

## Success Criteria (Overall)

- ✅ Fully functional one-page website deployed
- ✅ All 7 sections visible and interactive
- ✅ Smooth animations and video playback
- ✅ Responsive on desktop/tablet/mobile
- ✅ Fast load time and optimized media
- ✅ Running on Railway with custom domain
- ✅ Code is maintainable (no hardcoding, clean structure)
