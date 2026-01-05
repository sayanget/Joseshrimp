"""
语言切换视图
"""
from flask import Blueprint, session, redirect, request, url_for

language_bp = Blueprint('language', __name__)

@language_bp.route('/set-language/<lang>')
def set_language(lang):
    """设置语言"""
    supported_languages = ['zh', 'en', 'es']
    if lang in supported_languages:
        session['language'] = lang
    
    # 重定向回之前的页面
    return redirect(request.referrer or url_for('main.index'))
