from flask import Blueprint, render_template, jsonify, request
import os
import json

main_bp = Blueprint('main', __name__)

TAG_TO_CATEGORY = {
    'ad':        'Реклама',
    'kids':      'Детский контент',
    'art':       'Арт-проекты',
    'clips':     'Клипы',
    'backstage': 'Бекстейджи',
    'reels':     'Reels',
    'corp':      'Арт-проекты',
}


@main_bp.route('/')
def index():
    """Main page - one-page scroll layout"""
    return render_template('index.html')


@main_bp.route('/api/portfolio')
def portfolio_api():
    """Get portfolio items with pagination and category filter.

    Query params:
        page      (int, default 1)
        per_page  (int, default 4)
        category  (str, Russian category name; omit or 'all' for all)
    Returns:
        {"items": [...], "has_more": bool}
    """
    page = max(1, int(request.args.get('page', 1)))
    per_page = max(1, min(20, int(request.args.get('per_page', 4))))
    category_filter = request.args.get('category', 'all').strip()

    portfolio_dir = 'data/portfolio'
    all_items = []

    if os.path.exists(portfolio_dir):
        for video_id in sorted(os.listdir(portfolio_dir)):
            video_path = os.path.join(portfolio_dir, video_id)
            if not os.path.isdir(video_path):
                continue
            data_file = os.path.join(video_path, 'data.json')
            if not os.path.exists(data_file):
                continue
            with open(data_file, 'r', encoding='utf-8-sig') as f:
                item = json.load(f)
            item['id'] = video_id
            item['category'] = TAG_TO_CATEGORY.get(item.get('tag', ''), '')
            item['thumbnail'] = item.get('thumb_url', '')
            all_items.append(item)

    if category_filter and category_filter != 'all':
        all_items = [i for i in all_items if i.get('category') == category_filter]

    start = (page - 1) * per_page
    page_items = all_items[start:start + per_page]
    has_more = (start + per_page) < len(all_items)

    return jsonify({'items': page_items, 'has_more': has_more})
