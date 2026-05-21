# Tech Stack

## Backend

- **Python:** 3.11
- **Web Framework:** Flask 3.0.0
- **WSGI Server:** Gunicorn 21.2.0
- **Configuration:** python-dotenv 1.0.0
- **Templating:** Jinja2 (built-in with Flask)

## Frontend

- **HTML:** HTML5 (semantic markup)
- **CSS:** CSS3 (Flexbox, Grid, custom properties)
- **JavaScript:** 
  - **Alpine.js 3.x** - Micro-framework for reactive HTML (scroll tracking, navigation, lazy-loading triggers)
  - **Vanilla JS** - Custom video player, marquee animations
- **Video:** HTML5 `<video>` element (no third-party player libs)

## DevOps

- **Containerization:** Docker
- **Orchestration:** Docker Compose (dev environment)
- **Reverse Proxy:** Nginx (production)
- **Deployment:** Railway.app (container-based PaaS)

## Development

- **Code Quality:** Linting (flake8 or similar, optional for small project)
- **Type Checking:** mypy (optional)
- **Formatting:** black (optional)
- **Testing:** pytest (optional for Phase 4+)

## Why This Stack?

| Choice | Rationale |
|--------|-----------|
| Flask (not FastAPI) | Simpler for template rendering, minimal overkill for a one-page static site |
| Jinja2 | Flask default, lightweight, no build step |
| Alpine.js | Tiny (~15KB), no build tool, stays in HTML, perfect for scroll/lazy-load logic |
| Vanilla JS | No React/Vue overhead, total control over video player UX |
| Docker | Consistent dev/prod environment, Railway deployment native |
| Railway | Simple PaaS, automatic SSL, custom domain support, free tier for small projects |

## Rationale: Minimal JS

The user requested "minimal JS". This stack achieves that:
- No JS framework (no React, Vue, Svelte)
- Alpine.js replaces simple interactivity (~15KB total)
- Video player: native HTML5 + vanilla JS (no player.js, not third-party library)
- CSS animations handle marquee, wavy shapes (no animation libraries)

## Browser Support

- Modern browsers (ES2020+)
- Chrome/Firefox/Safari/Edge latest
- No IE11 support (not necessary for a business card site)

---

## Dependency Chain

```
Flask
  ├── Jinja2 (built-in)
  ├── Werkzeug (built-in)
  └── Click (built-in)

python-dotenv
Gunicorn
```

**Total production dependencies:** ~5 packages

---

## Development Workflow

### Local

```bash
# Install
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run
flask run  # starts on http://localhost:5000

# Or Docker
docker-compose -f docker-compose.dev.yml up
```

### Production (Railway)

```bash
# Push to git
git push railway main

# Railway automatically:
# 1. Detects Dockerfile
# 2. Builds image
# 3. Runs: gunicorn app:app --bind 0.0.0.0:8080
# 4. Routes custom domain to container
```

---

## Design Tools

- **Figma:** Design source (not used in code, manual CSS translation)
- **Design Tokens:** CSS custom properties (colors, fonts, spacing)

