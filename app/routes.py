from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for, abort
import os
import json
import cloudinary
import cloudinary.uploader
from config import CLOUDINARY_VIDEOS

main_bp = Blueprint('main', __name__)

DM_PASSWORD = '123'
PORTFOLIO_DIR = 'data/portfolio'

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


def _load_portfolio_items():
    all_items = []
    if not os.path.exists(PORTFOLIO_DIR):
        return all_items
    for video_id in sorted(os.listdir(PORTFOLIO_DIR)):
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
        # all tags as display names for dynamic filter building
        all_tags = item.get('tags', [primary_tag] if primary_tag else [])
        item['categories'] = list(dict.fromkeys(
            TAG_TO_CATEGORY.get(t, t) for t in all_tags if t
        ))
        item['thumbnail'] = item.get('thumb_url', '')
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
    return render_template('index.html', videos=CLOUDINARY_VIDEOS)


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


@main_bp.route('/api/dm/upload-video', methods=['POST'])
def dm_upload_video():
    if not session.get('dm_auth'):
        abort(403)
    f = request.files.get('video')
    if not f:
        return jsonify({'error': 'No file'}), 400
    try:
        result = cloudinary.uploader.upload(
            f,
            resource_type='video',
            folder='dj_visit/portfolio',
        )
        return jsonify({'url': result['secure_url'], 'public_id': result['public_id']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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

    item = {
        'title':       data.get('title', ''),
        'subtitle':    data.get('subtitle', ''),
        'description': data.get('description', ''),
        'tag':         primary_tag,
        'tags':        tags,
        'video_url':   data.get('video_url', ''),
        'thumb_url':   data.get('thumb_url', ''),
    }
    with open(os.path.join(folder, 'data.json'), 'w', encoding='utf-8') as f:
        json.dump(item, f, ensure_ascii=False, indent=2)

    item['id'] = new_id
    item['category'] = TAG_TO_CATEGORY.get(primary_tag, '')
    item['thumbnail'] = item['thumb_url']
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

    existing.update({
        'title':       patch.get('title', existing.get('title', '')),
        'subtitle':    patch.get('subtitle', existing.get('subtitle', '')),
        'description': patch.get('description', existing.get('description', '')),
        'tag':         primary_tag,
        'tags':        tags,
        'video_url':   patch.get('video_url', existing.get('video_url', '')),
        'thumb_url':   patch.get('thumb_url', existing.get('thumb_url', '')),
    })
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    existing['id'] = item_id
    existing['category'] = TAG_TO_CATEGORY.get(primary_tag, '')
    existing['thumbnail'] = existing['thumb_url']
    return jsonify(existing)


@main_bp.route('/api/dm/portfolio/<item_id>', methods=['DELETE'])
def dm_portfolio_delete(item_id):
    if not session.get('dm_auth'):
        abort(403)
    folder = os.path.join(PORTFOLIO_DIR, item_id)
    if not os.path.isdir(folder):
        abort(404)
    import shutil
    shutil.rmtree(folder)
    return jsonify({'ok': True})
