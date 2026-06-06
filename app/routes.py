from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for, abort, send_file, current_app
import os
import re
import json
import cloudinary
import cloudinary.uploader
from config import CLOUDINARY_VIDEOS

main_bp = Blueprint('main', __name__)

DM_PASSWORD = '123'
PORTFOLIO_DIR = os.environ.get('PORTFOLIO_DIR', '/data/portfolio')
MOVIES_DIR = os.environ.get('MOVIES_DIR', '/data/movies')

VIDEO_EXTS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v', '.wmv'}
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.svg'}

PREDEFINED_TAGS = ['ad', 'kids', 'art', 'clips', 'backstage', 'reels', 'corp']

TAG_TO_CATEGORY = {
    'ad':        'Реклама',
    'kids':      'Детский контент',
    'art':       'Арт-проекты',
    'clips':     'Клипы',
    'backstage': 'Бекстейджи',
    'reels':     'Reels',
    'corp':      'Арт-проекты',
}

TAG_LABELS = {
    'ad':        'Реклама',
    'kids':      'Детский контент',
    'art':       'Арт-проекты',
    'clips':     'Клипы',
    'backstage': 'Бекстейджи',
    'reels':     'Reels',
    'corp':      'Корп. видео',
}


def _extract_youtube_id(url):
    """Extract YouTube video ID from various URL formats."""
    if not url:
        return None
    patterns = [
        r'(?:youtube\.com/watch\?.*v=|youtu\.be/|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        m = re.search(pattern, url)
        if m:
            return m.group(1)
    return None


def _extract_vimeo_id(url):
    if not url:
        return None
    m = re.search(r'vimeo\.com/(?:video/)?(\d+)', url)
    return m.group(1) if m else None


def _detect_video_type(video_url):
    """Infer video_type from URL if not explicitly stored."""
    if not video_url:
        return 'cloudinary'
    if _extract_youtube_id(video_url):
        return 'youtube'
    if _extract_vimeo_id(video_url):
        return 'vimeo'
    if video_url.startswith('/api/portfolio-video/'):
        return 'local'
    lower = video_url.lower()
    if lower.startswith('http') and (lower.endswith('.mp4') or lower.endswith('.webm')):
        return 'direct'
    return 'cloudinary'


ORDER_FILE    = os.path.join(PORTFOLIO_DIR, 'order.json') if PORTFOLIO_DIR else None
SETTINGS_FILE = os.path.join(PORTFOLIO_DIR, 'settings.json') if PORTFOLIO_DIR else None


def _load_settings():
    if SETTINGS_FILE and os.path.isfile(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {'autoplay': True, 'columns': 2}


def _save_settings(s):
    if not SETTINGS_FILE:
        return
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(s, f, ensure_ascii=False)


def _load_order():
    if ORDER_FILE and os.path.isfile(ORDER_FILE):
        try:
            with open(ORDER_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return []


def _save_order(order):
    if not ORDER_FILE:
        return
    os.makedirs(os.path.dirname(ORDER_FILE), exist_ok=True)
    with open(ORDER_FILE, 'w', encoding='utf-8') as f:
        json.dump(order, f, ensure_ascii=False)


def _load_portfolio_items():
    all_items = []
    if not os.path.exists(PORTFOLIO_DIR):
        return all_items

    saved_order = _load_order()

    all_ids = sorted(
        d for d in os.listdir(PORTFOLIO_DIR)
        if os.path.isdir(os.path.join(PORTFOLIO_DIR, d)) and d != '__pycache__'
    )
    # merge: saved order first, then any new ids not yet in order
    ordered_ids = [i for i in saved_order if i in all_ids]
    ordered_ids += [i for i in all_ids if i not in ordered_ids]

    for video_id in ordered_ids:
        video_path = os.path.join(PORTFOLIO_DIR, video_id)
        if not os.path.isdir(video_path):
            continue
        data_file = os.path.join(video_path, 'data.json')
        if not os.path.exists(data_file):
            continue
        with open(data_file, 'r', encoding='utf-8-sig') as f:
            item = json.load(f)
        item['id'] = video_id
        primary_tag = item.get('tag', '')
        item['category'] = TAG_TO_CATEGORY.get(primary_tag, primary_tag) if primary_tag else ''
        all_tags = item.get('tags', [primary_tag] if primary_tag else [])
        item['categories'] = list(dict.fromkeys(
            TAG_TO_CATEGORY.get(t, t) for t in all_tags if t
        ))
        if 'video_type' not in item:
            item['video_type'] = _detect_video_type(item.get('video_url', ''))
        # auto-generate cloudinary thumbnail for cards where thumb_url == video_url
        vtype = item['video_type']
        thumb = item.get('thumb_url', '')
        vurl  = item.get('video_url', '')
        if vtype == 'cloudinary' and vurl and (not thumb or thumb == vurl):
            thumb = re.sub(
                r'/video/upload/',
                '/video/upload/so_0,f_jpg,q_auto/',
                vurl
            ).rsplit('.', 1)[0] + '.jpg'
            item['thumb_url'] = thumb
        item['thumbnail'] = thumb
        if item['video_type'] == 'youtube':
            item['youtube_id'] = _extract_youtube_id(item.get('video_url', ''))
        if item['video_type'] == 'vimeo':
            item['vimeo_id'] = _extract_vimeo_id(item.get('video_url', ''))
        if 'related' not in item:
            item['related'] = []
        all_items.append(item)
    return all_items


def _next_portfolio_id():
    if not os.path.exists(PORTFOLIO_DIR):
        os.makedirs(PORTFOLIO_DIR)
    existing = [d for d in os.listdir(PORTFOLIO_DIR)
                if os.path.isdir(os.path.join(PORTFOLIO_DIR, d))]
    nums = []
    for name in existing:
        try:
            nums.append(int(name))
        except ValueError:
            pass
    return str((max(nums) + 1) if nums else 1).zfill(2)


# ── Public routes ──────────────────────────────────────────────────────────────

@main_bp.route('/')
def index():
    settings = _load_settings()
    return render_template('index.html', videos=CLOUDINARY_VIDEOS, settings=settings)


@main_bp.route('/api/dm/site-settings', methods=['GET'])
def dm_site_settings_get():
    if not session.get('dm_auth'):
        abort(403)
    return jsonify(_load_settings())


@main_bp.route('/api/dm/site-settings', methods=['POST'])
def dm_site_settings_save():
    if not session.get('dm_auth'):
        abort(403)
    data = request.get_json(force=True)
    s = _load_settings()
    if 'autoplay' in data:
        s['autoplay'] = bool(data['autoplay'])
    if 'columns' in data:
        s['columns'] = int(data['columns'])
    _save_settings(s)
    return jsonify(s)


@main_bp.route('/api/portfolio')
def portfolio_api():
    page = max(1, int(request.args.get('page', 1)))
    per_page = max(1, min(20, int(request.args.get('per_page', 4))))
    category_filter = request.args.get('category', 'all').strip()
    use_test = request.args.get('test', '0') == '1'

    if use_test:
        test_items = [
            {'id': 'test-1', 'title': 'LIT ENERGY', 'subtitle': 'Яндекс', 'category': 'Реклама',
             'thumbnail': '/static/img/portfolio-1.png', 'video_url': '', 'tags': ['ad'], 'story': ''},
            {'id': 'test-2', 'title': 'НОВЫЙ ГОД', 'subtitle': 'Град', 'category': 'Арт-проекты',
             'thumbnail': '/static/img/portfolio-2.png', 'video_url': '', 'tags': ['art'], 'story': ''},
            {'id': 'test-3', 'title': 'ДМИТРИЙ ЖУЛЬКОВ', 'subtitle': 'Шоурил', 'category': 'Reels',
             'thumbnail': '/static/img/portfolio-3.png', 'video_url': '', 'tags': ['reels'], 'story': ''},
            {'id': 'test-4', 'title': 'НОЕВ КРУГОВОРОТ', 'subtitle': 'Стихи', 'category': 'Арт-проекты',
             'thumbnail': '/static/img/portfolio-4.png', 'video_url': '', 'tags': ['art'], 'story': ''},
            {'id': 'test-5', 'title': 'ЦЕНА СЛОВА', 'subtitle': 'Подкаст', 'category': 'Бекстейджи',
             'thumbnail': '/static/img/portfolio-5.png', 'video_url': '', 'tags': ['backstage'], 'story': ''},
            {'id': 'test-6', 'title': 'ШЕСТАКОВА КСЕНИЯ', 'subtitle': 'Шоурил', 'category': 'Reels',
             'thumbnail': '/static/img/portfolio-6.png', 'video_url': '', 'tags': ['reels'], 'story': ''},
        ]
        if category_filter and category_filter != 'all':
            test_items = [i for i in test_items if i.get('category') == category_filter]
        start = (page - 1) * per_page
        return jsonify({'items': test_items[start:start + per_page],
                        'has_more': (start + per_page) < len(test_items)})

    all_items = _load_portfolio_items()

    all_items = [i for i in all_items if not i.get('hidden')]

    if category_filter and category_filter != 'all':
        all_items = [i for i in all_items if i.get('category') == category_filter]

    start = (page - 1) * per_page
    page_items = all_items[start:start + per_page]
    has_more = (start + per_page) < len(all_items)

    return jsonify({'items': page_items, 'has_more': has_more})


# ── /dm admin ──────────────────────────────────────────────────────────────────

@main_bp.route('/dm', methods=['GET', 'POST'], strict_slashes=False)
def dm():
    if not session.get('dm_auth'):
        error = None
        if request.method == 'POST':
            if request.form.get('password') == DM_PASSWORD:
                session['dm_auth'] = True
                return redirect(url_for('main.dm'))
            error = 'Неверный пароль'
        return render_template('dm_login.html', error=error)

    items = _load_portfolio_items()
    return render_template('dm_admin.html',
                           items=items,
                           predefined_tags=PREDEFINED_TAGS,
                           tag_labels=TAG_LABELS)


@main_bp.route('/dm/logout')
def dm_logout():
    session.pop('dm_auth', None)
    return redirect(url_for('main.dm'))


@main_bp.route('/api/portfolio-video/<item_id>')
def portfolio_video_stream(item_id):
    """Serve locally stored portfolio video with byte-range support."""
    from flask import Response, stream_with_context
    safe_id = re.sub(r'[^a-zA-Z0-9_-]', '', item_id)
    video_path = os.path.join(PORTFOLIO_DIR, safe_id, 'video.mp4')
    if not os.path.isfile(video_path):
        ref_file = os.path.join(PORTFOLIO_DIR, safe_id, 'source_path.txt')
        if os.path.isfile(ref_file):
            with open(ref_file, 'r', encoding='utf-8') as f:
                video_path = f.read().strip()
        if not os.path.isfile(video_path):
            abort(404)

    ext = os.path.splitext(video_path)[1].lower()
    mime_map = {'.mp4': 'video/mp4', '.mov': 'video/quicktime', '.mkv': 'video/x-matroska',
                '.webm': 'video/webm', '.avi': 'video/x-msvideo', '.m4v': 'video/mp4'}
    video_mime = mime_map.get(ext, 'video/mp4')

    file_size = os.path.getsize(video_path)
    range_header = request.headers.get('Range')
    chunk = 1024 * 1024  # 1 MB chunks

    if range_header:
        # parse "bytes=start-end"
        byte_range = range_header.replace('bytes=', '').split('-')
        start = int(byte_range[0])
        end = int(byte_range[1]) if byte_range[1] else min(start + chunk - 1, file_size - 1)
        length = end - start + 1

        def generate():
            with open(video_path, 'rb') as f:
                f.seek(start)
                remaining = length
                while remaining > 0:
                    data = f.read(min(chunk, remaining))
                    if not data:
                        break
                    remaining -= len(data)
                    yield data

        resp = Response(stream_with_context(generate()), 206,
                        mimetype=video_mime, direct_passthrough=True)
        resp.headers['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        resp.headers['Content-Length'] = length
    else:
        def generate():
            with open(video_path, 'rb') as f:
                while True:
                    data = f.read(chunk)
                    if not data:
                        break
                    yield data

        resp = Response(stream_with_context(generate()), 200,
                        mimetype=video_mime, direct_passthrough=True)
        resp.headers['Content-Length'] = file_size

    resp.headers['Accept-Ranges'] = 'bytes'
    resp.headers['Cache-Control'] = 'public, max-age=3600'
    return resp


@main_bp.route('/api/dm/upload-video-local', methods=['POST'])
def dm_upload_video_local():
    """Upload video file to Railway /data volume."""
    if not session.get('dm_auth'):
        abort(403)
    f = request.files.get('video')
    if not f:
        return jsonify({'error': 'No file'}), 400
    new_id = _next_portfolio_id()
    folder = os.path.join(PORTFOLIO_DIR, new_id)
    os.makedirs(folder, exist_ok=True)
    dest = os.path.join(folder, 'video.mp4')
    try:
        import shutil
        with open(dest, 'wb') as out:
            shutil.copyfileobj(f.stream, out, length=1024 * 1024)
        url = '/api/portfolio-video/' + new_id
        return jsonify({'url': url, 'local_id': new_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/dm/upload-video-beget', methods=['POST'])
def dm_upload_video_beget():
    """Upload video to Beget via SFTP, return direct HTTP URL."""
    if not session.get('dm_auth'):
        abort(403)
    f = request.files.get('video')
    if not f:
        return jsonify({'error': 'No file'}), 400

    host     = os.environ.get('BEGET_HOST')
    user     = os.environ.get('BEGET_USER')
    password = os.environ.get('BEGET_PASSWORD')
    media_dir = os.environ.get('BEGET_MEDIA_DIR')
    media_url = os.environ.get('BEGET_MEDIA_URL', '').rstrip('/')

    if not all([host, user, password, media_dir]):
        return jsonify({'error': 'Beget SFTP not configured'}), 500

    import uuid
    import paramiko

    new_id  = uuid.uuid4().hex
    remote_name = new_id + '.mp4'
    remote_path = media_dir.rstrip('/') + '/' + remote_name

    import traceback
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=user, password=password, timeout=30,
                    banner_timeout=60, auth_timeout=60)
        sftp = ssh.open_sftp()
        sftp.get_channel().settimeout(600)
        # Save to temp file first — f.stream may be partially consumed by Flask
        import tempfile, shutil
        with tempfile.SpooledTemporaryFile(max_size=512 * 1024 * 1024) as tmp:
            shutil.copyfileobj(f.stream, tmp, length=1024 * 1024)
            tmp.seek(0)
            sftp.putfo(tmp, remote_path)
        sftp.close()
        ssh.close()
    except Exception as e:
        tb = traceback.format_exc()
        current_app.logger.error('Beget SFTP upload failed: %s\n%s', e, tb)
        return jsonify({'error': repr(e)}), 500

    url = media_url + '/' + remote_name
    return jsonify({'url': url, 'video_type': 'direct'})


@main_bp.route('/api/dm/upload-thumb-cloudinary', methods=['POST'])
def dm_upload_thumb_cloudinary():
    """Upload custom thumbnail image to Cloudinary for a cloudinary-type video."""
    if not session.get('dm_auth'):
        abort(403)
    f = request.files.get('thumb')
    if not f:
        return jsonify({'error': 'No file'}), 400
    try:
        result = cloudinary.uploader.upload(
            f,
            resource_type='image',
            folder='dj_visit/portfolio/thumbs',
            format='jpg',
            quality='auto',
        )
        return jsonify({'thumb_url': result['secure_url']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/dm/upload-thumb-local', methods=['POST'])
def dm_upload_thumb_local():
    """Upload thumbnail image for a locally stored video."""
    if not session.get('dm_auth'):
        abort(403)
    f = request.files.get('thumb')
    item_id = request.form.get('item_id', '').strip()
    if not f or not item_id:
        return jsonify({'error': 'No file or item_id'}), 400
    safe_id = re.sub(r'[^a-zA-Z0-9_-]', '', item_id)
    folder = os.path.join(PORTFOLIO_DIR, safe_id)
    os.makedirs(folder, exist_ok=True)
    ext = os.path.splitext(f.filename)[1].lower() or '.jpg'
    dest = os.path.join(folder, 'thumb' + ext)
    try:
        f.save(dest)
        url = '/api/portfolio-thumb/' + safe_id
        return jsonify({'thumb_url': url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/dm/server-videos')
def dm_server_videos():
    """List folders and video/thumb files inside MOVIES_DIR."""
    if not session.get('dm_auth'):
        abort(403)
    result = []
    if not os.path.isdir(MOVIES_DIR):
        return jsonify([])
    for folder_name in sorted(os.listdir(MOVIES_DIR)):
        folder_path = os.path.join(MOVIES_DIR, folder_name)
        if not os.path.isdir(folder_path):
            continue
        videos = []
        thumbs = []
        for fname in sorted(os.listdir(folder_path)):
            ext = os.path.splitext(fname)[1].lower()
            if ext in VIDEO_EXTS:
                videos.append(fname)
            elif ext in IMAGE_EXTS:
                thumbs.append(fname)
        if videos:
            result.append({'folder': folder_name, 'videos': videos, 'thumbs': thumbs})
    return jsonify(result)


@main_bp.route('/api/dm/import-server-video', methods=['POST'])
def dm_import_server_video():
    """Create a portfolio card from a file already on the server in MOVIES_DIR."""
    if not session.get('dm_auth'):
        abort(403)
    data = request.get_json(force=True)
    folder = data.get('folder', '').strip()
    video_file = data.get('video', '').strip()
    thumb_file = data.get('thumb', '').strip()

    # Sanitise — block path traversal but allow unicode filenames
    safe_folder = os.path.basename(folder)
    safe_video  = os.path.basename(video_file)
    safe_thumb  = os.path.basename(thumb_file) if thumb_file else ''

    src_video = os.path.join(MOVIES_DIR, safe_folder, safe_video)
    if not os.path.isfile(src_video):
        return jsonify({'error': 'Video file not found'}), 404

    new_id = _next_portfolio_id()
    dest_folder = os.path.join(PORTFOLIO_DIR, new_id)
    os.makedirs(dest_folder, exist_ok=True)

    import shutil
    # Store reference to original — no copy needed
    ref_file = os.path.join(dest_folder, 'source_path.txt')
    with open(ref_file, 'w', encoding='utf-8') as f:
        f.write(src_video)

    thumb_url = ''
    if safe_thumb:
        src_thumb = os.path.join(MOVIES_DIR, safe_folder, safe_thumb)
        if os.path.isfile(src_thumb):
            ext = os.path.splitext(safe_thumb)[1].lower()
            dest_thumb = os.path.join(dest_folder, 'thumb' + ext)
            try:
                shutil.copy2(src_thumb, dest_thumb)
                thumb_url = '/api/portfolio-thumb/' + new_id
            except Exception as e:
                current_app.logger.error('import-server-video thumb copy failed: %s', e)

    video_url = '/api/portfolio-video/' + new_id
    return jsonify({'url': video_url, 'local_id': new_id, 'thumb_url': thumb_url})


@main_bp.route('/api/portfolio-thumb/<item_id>')
def portfolio_thumb_stream(item_id):
    """Serve locally stored thumbnail from Railway /data volume."""
    safe_id = re.sub(r'[^a-zA-Z0-9_-]', '', item_id)
    folder = os.path.join(PORTFOLIO_DIR, safe_id)
    for ext in ('.jpg', '.jpeg', '.png', '.webp'):
        p = os.path.join(folder, 'thumb' + ext)
        if os.path.isfile(p):
            return send_file(p)
    abort(404)


@main_bp.route('/api/dm/upload-signature', methods=['GET'])
def dm_upload_signature():
    """Return a signed upload params for direct browser→Cloudinary upload."""
    if not session.get('dm_auth'):
        abort(403)
    import time
    timestamp = int(time.time())
    params = {
        'folder': 'dj_visit/portfolio',
        'timestamp': timestamp,
    }
    signature = cloudinary.utils.api_sign_request(params, cloudinary.config().api_secret)
    return jsonify({
        'signature': signature,
        'timestamp': timestamp,
        'api_key': cloudinary.config().api_key,
        'cloud_name': cloudinary.config().cloud_name,
        'folder': 'dj_visit/portfolio',
    })


@main_bp.route('/api/portfolio/<item_id>')
def portfolio_item(item_id):
    """Get a single portfolio item by ID (including hidden ones — for related links)."""
    safe_id = re.sub(r'[^a-zA-Z0-9_-]', '', item_id)
    data_file = os.path.join(PORTFOLIO_DIR, safe_id, 'data.json')
    if not os.path.isfile(data_file):
        abort(404)
    with open(data_file, 'r', encoding='utf-8-sig') as f:
        item = json.load(f)
    item['id'] = safe_id
    primary_tag = item.get('tag', '')
    item['category'] = TAG_TO_CATEGORY.get(primary_tag, primary_tag) if primary_tag else ''
    all_tags = item.get('tags', [primary_tag] if primary_tag else [])
    item['categories'] = list(dict.fromkeys(TAG_TO_CATEGORY.get(t, t) for t in all_tags if t))
    if 'video_type' not in item:
        item['video_type'] = _detect_video_type(item.get('video_url', ''))
    thumb = item.get('thumb_url', '')
    vurl  = item.get('video_url', '')
    if item['video_type'] == 'cloudinary' and vurl and (not thumb or thumb == vurl):
        thumb = re.sub(r'/video/upload/', '/video/upload/so_0,f_jpg,q_auto/', vurl).rsplit('.', 1)[0] + '.jpg'
        item['thumb_url'] = thumb
    item['thumbnail'] = thumb
    if item['video_type'] == 'youtube':
        item['youtube_id'] = _extract_youtube_id(item.get('video_url', ''))
    if item['video_type'] == 'vimeo':
        item['vimeo_id'] = _extract_vimeo_id(item.get('video_url', ''))
    if 'related' not in item:
        item['related'] = []
    return jsonify(item)


@main_bp.route('/api/dm/portfolio', methods=['POST'])
def dm_portfolio_create():
    if not session.get('dm_auth'):
        abort(403)
    data = request.get_json(force=True)
    new_id = _next_portfolio_id()
    folder = os.path.join(PORTFOLIO_DIR, new_id)
    os.makedirs(folder, exist_ok=True)

    # tags: list → pick first as primary tag for backward compat
    tags = data.get('tags', [])
    primary_tag = tags[0] if tags else ''

    video_url = data.get('video_url', '')
    video_type = data.get('video_type') or _detect_video_type(video_url)
    item = {
        'title':       data.get('title', ''),
        'subtitle':    data.get('subtitle', ''),
        'description': data.get('description', ''),
        'tag':         primary_tag,
        'tags':        tags,
        'video_url':   video_url,
        'video_type':  video_type,
        'thumb_url':   data.get('thumb_url', ''),
        'hidden':      bool(data.get('hidden', False)),
    }
    with open(os.path.join(folder, 'data.json'), 'w', encoding='utf-8') as f:
        json.dump(item, f, ensure_ascii=False, indent=2)

    item['id'] = new_id
    item['category'] = TAG_TO_CATEGORY.get(primary_tag, '')
    item['thumbnail'] = item['thumb_url']
    if video_type == 'youtube':
        item['youtube_id'] = _extract_youtube_id(video_url)
    if video_type == 'vimeo':
        item['vimeo_id'] = _extract_vimeo_id(video_url)
    return jsonify(item), 201


@main_bp.route('/api/dm/portfolio/<item_id>', methods=['PUT'])
def dm_portfolio_update(item_id):
    if not session.get('dm_auth'):
        abort(403)
    folder = os.path.join(PORTFOLIO_DIR, item_id)
    if not os.path.isdir(folder):
        abort(404)
    data_file = os.path.join(folder, 'data.json')
    with open(data_file, 'r', encoding='utf-8-sig') as f:
        existing = json.load(f)

    patch = request.get_json(force=True)
    tags = patch.get('tags', existing.get('tags', []))
    primary_tag = tags[0] if tags else existing.get('tag', '')

    new_video_url = patch.get('video_url', existing.get('video_url', ''))
    new_video_type = patch.get('video_type') or _detect_video_type(new_video_url)
    existing.update({
        'title':       patch.get('title', existing.get('title', '')),
        'subtitle':    patch.get('subtitle', existing.get('subtitle', '')),
        'description': patch.get('description', existing.get('description', '')),
        'tag':         primary_tag,
        'tags':        tags,
        'video_url':   new_video_url,
        'video_type':  new_video_type,
        'thumb_url':   patch.get('thumb_url', existing.get('thumb_url', '')),
        'hidden':      bool(patch.get('hidden', existing.get('hidden', False))),
    })
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    existing['id'] = item_id
    existing['category'] = TAG_TO_CATEGORY.get(primary_tag, '')
    existing['thumbnail'] = existing['thumb_url']
    if new_video_type == 'youtube':
        existing['youtube_id'] = _extract_youtube_id(new_video_url)
    if new_video_type == 'vimeo':
        existing['vimeo_id'] = _extract_vimeo_id(new_video_url)
    return jsonify(existing)


@main_bp.route('/api/dm/portfolio/<item_id>', methods=['DELETE'])
def dm_portfolio_delete(item_id):
    if not session.get('dm_auth'):
        abort(403)
    folder = os.path.join(PORTFOLIO_DIR, item_id)
    if not os.path.isdir(folder):
        abort(404)

    # delete from Cloudinary if applicable
    data_file = os.path.join(folder, 'data.json')
    if os.path.isfile(data_file):
        try:
            with open(data_file, 'r', encoding='utf-8-sig') as f:
                item_data = json.load(f)
            if item_data.get('video_type') == 'cloudinary':
                video_url = item_data.get('video_url', '')
                # extract public_id: everything between /upload/ and file extension
                m = re.search(r'/upload/(?:v\d+/)?(.+)\.[a-z0-9]+$', video_url)
                if m:
                    public_id = m.group(1)
                    cloudinary.uploader.destroy(public_id, resource_type='video')
        except Exception:
            pass  # don't block deletion if Cloudinary call fails

    import shutil
    shutil.rmtree(folder)
    # remove from order file
    order = _load_order()
    if item_id in order:
        order.remove(item_id)
        _save_order(order)
    return jsonify({'ok': True})


@main_bp.route('/api/dm/portfolio/<item_id>/related', methods=['POST'])
def dm_related_save(item_id):
    if not session.get('dm_auth'):
        abort(403)
    folder = os.path.join(PORTFOLIO_DIR, item_id)
    if not os.path.isdir(folder):
        abort(404)

    data = request.get_json(force=True)
    new_related = [str(i) for i in data.get('related', []) if str(i) != item_id]

    def _read_item(vid):
        p = os.path.join(PORTFOLIO_DIR, vid, 'data.json')
        if not os.path.isfile(p):
            return None
        with open(p, 'r', encoding='utf-8-sig') as f:
            return json.load(f)

    def _write_item(vid, obj):
        p = os.path.join(PORTFOLIO_DIR, vid, 'data.json')
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)

    # load current item
    current = _read_item(item_id)
    if current is None:
        abort(404)
    old_related = current.get('related', [])

    # update current item
    current['related'] = new_related
    _write_item(item_id, current)

    # symmetric sync: add item_id to every new related, remove from old ones no longer related
    removed = [r for r in old_related if r not in new_related]
    added   = [r for r in new_related if r not in old_related]

    for rid in added:
        obj = _read_item(rid)
        if obj is None:
            continue
        rels = obj.get('related', [])
        if item_id not in rels:
            rels.append(item_id)
            obj['related'] = rels
            _write_item(rid, obj)

    for rid in removed:
        obj = _read_item(rid)
        if obj is None:
            continue
        rels = obj.get('related', [])
        if item_id in rels:
            rels.remove(item_id)
            obj['related'] = rels
            _write_item(rid, obj)

    return jsonify({'ok': True, 'related': new_related})


@main_bp.route('/api/dm/order', methods=['GET'])
def dm_order_get():
    if not session.get('dm_auth'):
        abort(403)
    items = _load_portfolio_items()
    result = []
    for item in items:
        ytid = item.get('youtube_id') or _extract_youtube_id(item.get('video_url', ''))
        thumb = ''
        if item.get('video_type') == 'youtube' and ytid:
            thumb = 'https://img.youtube.com/vi/' + ytid + '/mqdefault.jpg'
        else:
            thumb = item.get('thumb_url', '') or item.get('thumbnail', '')
        result.append({
            'id':       item['id'],
            'title':    item.get('title', ''),
            'subtitle': item.get('subtitle', ''),
            'thumb':    thumb,
            'video_type': item.get('video_type', 'cloudinary'),
        })
    return jsonify(result)


@main_bp.route('/api/dm/order', methods=['POST'])
def dm_order_save():
    if not session.get('dm_auth'):
        abort(403)
    data = request.get_json(force=True)
    order = data.get('order', [])
    if not isinstance(order, list):
        return jsonify({'error': 'order must be a list'}), 400
    _save_order(order)
    return jsonify({'ok': True})
