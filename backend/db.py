"""Работа с PostgreSQL."""

import os
import time

import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'db'),
    'port': int(os.environ.get('DB_PORT', '5432')),
    'user': os.environ.get('POSTGRES_USER', 'admin'),
    'password': os.environ.get('POSTGRES_PASSWORD', 'admin'),
    'dbname': os.environ.get('POSTGRES_DB', 'analytics'),
}


def wait_for_db(max_retries: int = 30, delay: float = 2.0):
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.close()
            return
        except psycopg2.OperationalError:
            if attempt == max_retries - 1:
                raise
            time.sleep(delay)


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def init_schema():
    wait_for_db()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS analysis_runs (
                    id SERIAL PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    n_clusters INTEGER NOT NULL,
                    n_samples INTEGER NOT NULL
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS cluster_points (
                    id SERIAL PRIMARY KEY,
                    run_id INTEGER REFERENCES analysis_runs(id) ON DELETE CASCADE,
                    x DOUBLE PRECISION NOT NULL,
                    y DOUBLE PRECISION NOT NULL,
                    cluster_id INTEGER NOT NULL
                );
                """
            )
        conn.commit()


def save_analysis_result(df, n_clusters: int) -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO analysis_runs (n_clusters, n_samples) VALUES (%s, %s) RETURNING id',
                (n_clusters, len(df)),
            )
            run_id = cur.fetchone()[0]
            rows = [
                (run_id, float(row.x), float(row.y), int(row.cluster))
                for row in df.itertuples(index=False)
            ]
            cur.executemany(
                'INSERT INTO cluster_points (run_id, x, y, cluster_id) VALUES (%s, %s, %s, %s)',
                rows,
            )
        conn.commit()
    return run_id


def get_latest_summary():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT r.id, r.created_at, r.n_clusters, r.n_samples,
                       COUNT(DISTINCT p.cluster_id) AS clusters_found
                FROM analysis_runs r
                LEFT JOIN cluster_points p ON p.run_id = r.id
                GROUP BY r.id
                ORDER BY r.created_at DESC
                LIMIT 1
                """
            )
            return cur.fetchone()
