# DJ_Visit — Web Business Card

One-page web business card (визитка) for music producer **Dmitry Zhulkov**. A single-page
scroll layout with background video, custom HTML5 video player, animations, a filterable
portfolio, and a password-protected admin panel for managing portfolio videos.

## Tech Stack

- **Backend:** Python 3.11 + Flask 3.0 + Jinja2
- **Frontend:** HTML5, CSS3 (CSS variables), Alpine.js 3.x, Vanilla JS
- **Media:** Cloudinary (hosted video/thumbnails) + local `/data` volume + YouTube / Vimeo / direct URLs
- **Server:** Gunicorn
- **Deployment:** Docker + Railway.app

## Page Structure

A single scroll page composed of 7 sections (`app/templates/components/`):

1. **Header** — sticky navigation + logo
2. **Slide 1 — Hero** (Главная) — background video, wavy shape, marquee
3. **Slide 2 — Why Me** (Почему я?) — typing animation
4. **Slide 3 — Portfolio** (Портфолио) — video cards, category filters, "Load More", related videos
5. **Slide 4 — Acting** (Актёрский опыт) — video player + modal
6. **Slide 5 — Process** (Как рождается результат) — horizontal scroll
7. **Footer** — contacts + copyright

## Quick Start

### Prerequisites
- Docker + Docker Compose, or Python 3.11
- A Cloudinary account (for the background videos / hosted portfolio media)

### With Docker

```bash
cp .env.example .env        # then fill in the values
docker-compose up --build
# open http://localhost:5000
```

### Without Docker

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then fill in the values
flask run --host=0.0.0.0 --port=5000
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | yes (prod) | Flask session secret. Production startup fails if unset. |
| `DM_PASSWORD` | yes | Password for the `/dm` admin panel. |
| `CLOUDINARY_URL` | yes | `cloudinary://api_key:api_secret@cloud_name` — video/thumbnail hosting + signed uploads. |
| `PORTFOLIO_DIR` | yes | Path to portfolio data (Railway volume, e.g. `/data/portfolio`). |
| `MOVIES_DIR` | no | Folder of pre-uploaded videos importable from the admin panel. |
| `FLASK_ENV` / `FLASK_DEBUG` | no | `development` / `production`, debug toggle. |
| `BEGET_HOST` / `BEGET_USER` / `BEGET_PASSWORD` / `BEGET_MEDIA_DIR` / `BEGET_MEDIA_URL` | no | Optional Beget SFTP upload target for large videos. |

## Admin Panel (`/dm`)

Password-protected (CSRF + rate-limited login) panel for managing portfolio content
without redeploying:

- Create / edit / delete portfolio cards
- Upload video to Cloudinary (signed direct upload), local `/data` volume, or Beget SFTP;
  or reference YouTube / Vimeo / direct URLs
- Custom thumbnails, tags/categories, hidden cards
- Drag-and-drop ordering and "related videos" links
- Site settings (autoplay, grid columns)

`/dm` is disallowed in `robots.txt`.

## Portfolio Data Model

Each portfolio item is a folder under `PORTFOLIO_DIR/<id>/` containing `data.json`
(and optionally `video.mp4`, `thumb.*`, or `source_path.txt`):

```json
{
  "title": "LIT ENERGY",
  "subtitle": "Яндекс",
  "description": "Full description",
  "tags": ["ad"],
  "video_url": "https://res.cloudinary.com/.../video.mp4",
  "video_type": "cloudinary",
  "thumb_url": "",
  "hidden": false,
  "related": []
}
```

`order.json` (card ordering) and `settings.json` (autoplay/columns) live alongside the
item folders. Tags map to display categories in `app/routes.py`
(`ad` → Реклама, `kids` → Детский контент, `art` → Арт-проекты, `clips` → Клипы,
`backstage` → Бекстейджи, `reels` → Reels, `corp` → Корп. видео).

## Project Layout

```
DJ_Visit/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes.py            # Public + /dm admin + portfolio API
│   ├── extensions.py        # limiter, csrf
│   ├── templates/           # index.html, components/, dm_login.html, dm_admin.html
│   └── static/              # css/, js/, img/
├── config.py                # Config + Cloudinary setup
├── wsgi.py                  # Gunicorn entrypoint
├── requirements.txt
├── Dockerfile               # gunicorn on :8080
├── docker-compose.yml       # local dev (flask run on :5000)
├── .env.example
├── docs/                    # architecture, tech stack, design tokens, module specs
└── CLAUDE.md                # project vision & conventions
```

## Deployment (Railway)

- Build from `Dockerfile`; Gunicorn serves `wsgi:app` on port `8080`.
- Attach a persistent volume mounted at `/data` and set `PORTFOLIO_DIR=/data/portfolio`
  so uploaded videos/thumbnails survive redeploys.
- Set `SECRET_KEY`, `DM_PASSWORD`, `CLOUDINARY_URL` (and any `BEGET_*` if used) as
  service variables.

## Documentation

- `CLAUDE.md` — project vision & conventions
- `docs/01-architecture.md`, `docs/02-tech-stack.md`, `docs/05-design-tokens.md`
- `docs/modules/*/README.md` — component specs
