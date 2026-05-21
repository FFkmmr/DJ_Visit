# DJ_Visit: Web Business Card for Music Producer

## Project Vision

**Goal:** Create a sophisticated, one-page web business card (визитка) for a DJ/music producer.

**Type:** Single-page scroll layout (1920x6093px desktop design)

**Tech Stack:**
- **Backend:** Python 3.11 + Flask + Jinja2
- **Frontend:** HTML5 + CSS3 + Alpine.js + Vanilla JS
- **Media:** HTML5 video (background + custom player)
- **Deployment:** Railway.app + custom domain

## Architecture Overview

### Structure: 7 Components

1. **Header** (sticky/fixed, black, navigation + logo)
2. **Slide 1 - Hero** (Главная) - background video + wavy shape + marquee
3. **Slide 2 - Why Me** (Почему я?) - typing animation + text
4. **Slide 3 - Portfolio** (Портфолио) - video cards + sticky filters + "Load More"
5. **Slide 4 - Acting** (Актёрский опыт) - video player + modal
6. **Slide 5 - Process** (Как рождается результат) - horizontal scroll sections
7. **Footer** - contacts + copyright

### Design Tokens (from Figma)

- **Primary Color:** Orange (accent, CTA, stars)
- **Background:** Black (#000000)
- **Text:** White (#FFFFFF) / Gray with opacity
- **Typography:** (TBD - extract from Figma)

### Deployment

- **Local Dev:** `docker-compose -f docker-compose.dev.yml up` (Flask dev server)
- **Production:** Railway.app (gunicorn + nginx)
- **Domain:** Custom domain (TLS via Railway)

---

## Development Phases

### Phase 1: Bootstrap & Header + Hero Slide
- Architect designs project structure (docs/)
- Backend creates Flask skeleton
- Frontend implements header + slide 1 (static, no animations)
- **Deliverable:** Working dev environment, header + hero visible

### Phase 2: Slides 2-5 Implementation
- Typing animation (slide 2)
- Portfolio carousel with video (slide 3)
- Video player + modal (slide 4)
- Horizontal scroll process (slide 5)
- Footer

### Phase 3: Animations & Polish
- Video lazy-loading
- Marquee animations
- Scroll animations
- Interactions polish

### Phase 4: Responsive & Deployment
- Tablet/mobile adaptations
- Railway deployment setup
- Custom domain configuration

---

## Conventions

- **No hardcoding:** All colors, fonts, sizes → CSS variables
- **Minimal JS:** Alpine.js for micro-interactions, Vanilla JS for video logic
- **Components:** Modular HTML/CSS per section
- **Assets:** All images/videos in `/app/static/`
- **Data:** Portfolio videos in `/data/portfolio/{id}/` (video.mp4 + data.json)

---

## Next Steps

1. Architect: Create docs/ structure
2. Backend: Flask skeleton + Docker setup
3. Frontend: Header + Slide 1 templates + CSS
