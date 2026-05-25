"""Защита от форсированного веб-браузинга (forced browsing)."""

import re
from functools import wraps

from flask import abort, request

# Разрешённые публичные маршруты (whitelist)
ALLOWED_PATHS = {
    '/',
    '/analyze',
    '/health',
    '/static/result.png',
}

# Шаблоны запрещённых путей (внутренние, админ, обход)
FORBIDDEN_PATTERNS = [
    re.compile(r'^/admin', re.I),
    re.compile(r'^/internal', re.I),
    re.compile(r'^/\.', re.I),
    re.compile(r'\.\./'),
    re.compile(r'^/config', re.I),
    re.compile(r'^/backup', re.I),
    re.compile(r'^/db', re.I),
    re.compile(r'^/secret', re.I),
]


def is_forbidden_path(path: str) -> bool:
    for pattern in FORBIDDEN_PATTERNS:
        if pattern.search(path):
            return True
    return False


def forced_browsing_guard(app):
    """Middleware: блокировка несанкционированных URL."""

    @app.before_request
    def check_path():
        path = request.path

        if is_forbidden_path(path):
            app.logger.warning('Blocked forced browsing attempt: %s', path)
            abort(403)

        if path.startswith('/static/'):
            return

        if path not in ALLOWED_PATHS:
            app.logger.warning('Unknown path blocked: %s', path)
            abort(404)

    @app.after_request
    def security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response


def require_internal_token(f):
    """Декоратор для внутренних эндпоинтов (не экспонируются через nginx)."""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-Internal-Token')
        expected = app_internal_token()
        if token != expected:
            abort(403)
        return f(*args, **kwargs)

    return decorated


def app_internal_token() -> str:
    import os
    return os.environ.get('INTERNAL_TOKEN', 'change-me-in-production')
