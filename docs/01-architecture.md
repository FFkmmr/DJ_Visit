# DJ_Visit Architecture

## Project Structure

```
DJ_Visit/
├── CLAUDE.md (project vision & conventions)
├── TZ.md (technical specification for phases)
├── app/
│   ├── __init__.py (Flask app factory)
│   ├── routes.py (Flask routes)
│   ├── config.py (configuration from .env)
│   ├── templates/
│   │   ├── base.html (main layout)
│   │   └── components/ (reusable partials)
│   │       ├── header.html
│   │       ├── slide-1.html
│   │       ├── slide-2.html
│   │       └── ... (more slides)
│   └── static/
│       ├── css/
│       │   ├── main.css (reset + tokens + layout)
│       │   ├── header.css
│       │   └── slides/ (per-slide styles)
│       ├── js/
│       │   ├── video-lazy-load.js
│       │   ├── video-player.js
│       │   └── marquee.js
│       └── img/ (images, icons)
├── data/
│   └── portfolio/ (portfolio video data)
│       ├── video-1/
│       │   ├── video.mp4
│       │   └── data.json
│       └── ... (more videos)
├── requirements.txt
├── config.py
├── .env (local dev, gitignored)
├── .env.example
├── Dockerfile
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── .dockerignore
└── docs/ (this directory)
    ├── README.md
    ├── 01-architecture.md (this file)
    ├── 02-tech-stack.md
    ├── 03-data-model.md
    ├── 04-frontend-components.md
    ├── 05-design-tokens.md
    ├── 06-deployment.md
    └── modules/
        ├── header/
        │   └── README.md
        └── slide-1/
            └── README.md
```

## Flask App Factory

**File:** `app/__init__.py`

```python
from flask import Flask
from app.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app
```

## Routes

**File:** `app/routes.py`

- `GET /` → Render `base.html` (one-page scroll layout)
- `GET /api/portfolio` → JSON list of portfolio videos (for slide 3)
- `GET /static/<path>` → Flask static file serving

## Single-Page Architecture

Since the design is one tall scroll page (1920x6093px), the layout uses:

- One `base.html` with all 7 sections
- Alpine.js `x-data` for scroll navigation (active slide tracking)
- Sections: `.slide-1`, `.slide-2`, etc.
- Navigation anchors: `#slide-1`, `#slide-2`, etc.

## CSS Organization

- **main.css:** Reset, design tokens (CSS variables), global layout
- **Per-component:** header.css, slides/slide-1.css, slides/slide-2.css, etc.
- **Responsive:** Flexbox/Grid for tablet/mobile adaptations

## Video Handling

- **Background video (slide 1):** Lazy-load with Intersection Observer (Alpine.js)
- **Portfolio cards (slide 3):** Video thumbnails with play button, lazy-load on scroll
- **Video player (slide 4):** HTML5 `<video>` with custom controls (Alpine.js)

## Data Model: Portfolio Videos

Each video stored in a directory:

```
data/portfolio/video-1/
  ├── video.mp4
  └── data.json
```

`data.json` schema:
```json
{
  "id": "video-1",
  "title": "Project Name",
  "caption": "Short description",
  "tag": "реклама",
  "description": "Full description for later use"
}
```

Backend route `/api/portfolio` returns list of all video data.

## Environment Configuration

**File:** `config.py`

- Loads `.env` via `python-dotenv`
- Dev config: `FLASK_ENV=development`, `FLASK_DEBUG=True`
- Prod config: `FLASK_ENV=production`, `RAILWAY_ENVIRONMENT=production`

## Deployment: Railway.app

(See `06-deployment.md` for details)

- Container: Docker (Dockerfile + gunicorn)
- Environment: Railway-managed secrets (.env)
- Domain: Custom domain via Railway DNS/proxy
- SSL: Automatic (Railway)

---

## Open Questions

- Which video format/codec for background video? (H.264 compatibility)
- Portfolio video resolution/bitrate targets?
- Font names/families for typography? (Extract from Figma)
