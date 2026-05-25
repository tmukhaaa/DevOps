#!/usr/bin/env python3
"""
Генерация тестового набора данных (п. 9).
Вариант 3: двумерные признаки x, y для кластеризации K-Means.
Состав согласован с преподавателем: 1000 точек, 3 скрытых кластера + шум.
"""

import numpy as np
import pandas as pd

ROWS = 1000
CLUSTERS = 3
POINTS_PER_CLUSTER = ROWS // CLUSTERS
OUTPUT = 'data.csv'

# Центры кластеров (для воспроизводимой структуры данных)
CENTERS = np.array([
    [20, 25],
    [75, 80],
    [50, 15],
])

rng = np.random.default_rng(seed=159)

frames = []
for i, center in enumerate(CENTERS):
    n = POINTS_PER_CLUSTER if i < CLUSTERS - 1 else ROWS - POINTS_PER_CLUSTER * (CLUSTERS - 1)
    x = rng.normal(center[0], 8, n).clip(1, 99)
    y = rng.normal(center[1], 8, n).clip(1, 99)
    frames.append(pd.DataFrame({'x': x.round(2), 'y': y.round(2)}))

df = pd.concat(frames, ignore_index=True)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
df.to_csv(OUTPUT, index=False)

print(f'Сгенерировано {len(df)} записей -> {OUTPUT}')
print(df.describe().to_string())
