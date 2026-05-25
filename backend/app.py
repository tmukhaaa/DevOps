"""Flask-приложение: кластеризация K-Means (вариант 3) и защита от forced browsing."""

import os

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, render_template_string
from sklearn.cluster import KMeans

from db import get_latest_summary, init_schema, save_analysis_result
from security import forced_browsing_guard

app = Flask(__name__)
forced_browsing_guard(app)

DATA_PATH = os.environ.get('DATA_PATH', 'data/data.csv')
N_CLUSTERS = int(os.environ.get('N_CLUSTERS', '3'))
os.makedirs('static', exist_ok=True)

HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Secure Analytics — вариант 2 (Flask)</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 720px; margin: 2rem auto; padding: 0 1rem; }
    a { color: #0b5; }
    .badge { background: #e8f5e9; padding: 0.25rem 0.5rem; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>Контейнер безопасной аналитики</h1>
  <p>Тема 159: защита от <span class="badge">форсированного веб-браузинга</span></p>
  <ul>
    <li><a href="/analyze">Запустить анализ (K-Means, вариант 3)</a></li>
    <li><a href="/health">Проверка состояния</a></li>
  </ul>
  <p><small>Пути /admin, /internal и обход каталогов блокируются nginx и приложением.</small></p>
</body>
</html>
"""

ANALYZE_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Результаты кластеризации</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 960px; margin: 1rem auto; padding: 0 1rem; }
    table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
    th, td { border: 1px solid #ccc; padding: 0.4rem 0.6rem; text-align: left; }
    th { background: #f5f5f5; }
    img { max-width: 100%; border: 1px solid #ddd; }
  </style>
</head>
<body>
  <h1>Интеллектуальная обработка данных (K-Means)</h1>
  <p>Запуск #{{ run_id }} | кластеров: {{ n_clusters }} | точек: {{ n_samples }}</p>
  <h2>Табличное представление (первые 20 строк)</h2>
  {{ table_html|safe }}
  <h2>Визуальное представление</h2>
  <img src="/static/result.png" alt="Scatter plot кластеров">
  <p><a href="/">На главную</a></p>
</body>
</html>
"""


@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE)


@app.route('/health')
def health():
    summary = get_latest_summary()
    return {
        'status': 'ok',
        'database': 'connected',
        'last_run': dict(summary) if summary else None,
    }


@app.route('/analyze')
def analyze():
    data = pd.read_csv(DATA_PATH)
    model = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10)
    data['cluster'] = model.fit_predict(data[['x', 'y']])

    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(data['x'], data['y'], c=data['cluster'], cmap='viridis', alpha=0.7)
    plt.colorbar(scatter, label='Кластер')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title(f'K-Means кластеризация (k={N_CLUSTERS})')
    plt.tight_layout()
    plt.savefig('static/result.png', dpi=120)
    plt.close()

    run_id = save_analysis_result(data, N_CLUSTERS)
    table_html = data.head(20).to_html(classes='data-table', index=False)

    return render_template_string(
        ANALYZE_TEMPLATE,
        run_id=run_id,
        n_clusters=N_CLUSTERS,
        n_samples=len(data),
        table_html=table_html,
    )


def _bootstrap_db():
    try:
        init_schema()
    except Exception as exc:
        app.logger.warning('Database init deferred: %s', exc)


_bootstrap_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
