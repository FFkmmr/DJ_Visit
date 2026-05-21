# DJ_Visit - Web Business Card

Professional one-page web business card for a music producer with animations, custom video player, and responsive design.

## Quick Start (Phase 1 Bootstrap)

### Prerequisites

- Docker and Docker Compose installed
- Git

### Local Development

```bash
# Clone or navigate to project
cd DJ_Visit

# Start dev environment
docker-compose -f docker-compose.dev.yml up

# Open browser
open http://localhost:5000
```

The Flask app will run in development mode with hot-reload.

### Project Structure

```
DJ_Visit/
├── CLAUDE.md                 # Project vision & conventions
├── TZ.md                     # Technical specification & phases
├── docs/                     # Architecture documentation
│   ├── 01-architecture.md
│   ├── 02-tech-stack.md
│   ├── 05-design-tokens.md
│   └── modules/              # Module specifications
│       ├── header/
│       └── slide-1/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes.py            # Routes
│   ├── templates/           # Jinja2 templates
│   │   ├── index.html
│   │   └── components/
│   └── static/              # CSS, JS, images
│       ├── css/
│       ├── js/
│       └── img/
├── data/
│   └── portfolio/           # Portfolio video data
├── requirements.txt
├── config.py
├── .env                     # Local dev config
├── Dockerfile
└── docker-compose.dev.yml
```

## Development Workflow

### Adding a New Slide

1. Create template: `app/templates/components/slide-N.html`
2. Create styles: `app/static/css/slide-N.css`
3. Include in `index.html`
4. Add documentation: `docs/modules/slide-N/README.md`

### Adding Portfolio Videos

```
data/portfolio/
├── video-1/
│   ├── video.mp4
│   └── data.json
└── video-2/
    ├── video.mp4
    └── data.json
```

**data.json schema:**
```json
{
  "id": "video-1",
  "title": "Project Name",
  "caption": "Short description",
  "tag": "реклама",
  "description": "Full description"
}
```

## Phases

- **Phase 1** ✅ Bootstrap + Header + Slide 1 (hero)
- **Phase 2** → Slides 2-5 + Footer
- **Phase 3** → Animations, lazy-loading, polish
- **Phase 4** → Responsive design, Railway deployment

See `TZ.md` for detailed phase breakdown.

## Tech Stack

- **Backend:** Flask 3.0 + Jinja2
- **Frontend:** HTML5, CSS3, Alpine.js 3.x, Vanilla JS
- **Deployment:** Docker + Railway.app
- **Dev:** `docker-compose up` (hot-reload)

## Design Tokens

All colors, fonts, and spacing defined in:
- `docs/05-design-tokens.md`
- `app/static/css/main.css` (CSS variables)

## Key Features

✅ One-page scroll layout (1920x6093px desktop)
⏳ Background video with lazy-loading
⏳ Custom video player with modal
⏳ Animated marquee text
⏳ Horizontal scroll sections
⏳ Responsive design (desktop/tablet/mobile)

## Documentation

- `CLAUDE.md` - Project conventions and vision
- `TZ.md` - Technical specification and phases
- `docs/` - Architecture, modules, design tokens
- `docs/modules/*/README.md` - Component specs

## Support

For questions or issues, see the documentation or check `docs/99-open-questions.md` (TBD).

---

**Status:** Phase 1 bootstrap complete. Ready for Phase 2 (slides 2-5).
