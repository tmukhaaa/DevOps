# Secure Analytics — тема 159 (forced browsing)

Flask-приложение (вариант 2) с кластеризацией K-Means (вариант 3) в архитектуре из 4 Docker-контейнеров.

## Быстрый старт (Docker)

```bash
cd data && python3 generate.py && cd ..
docker compose up --build -d
./scripts/test_app.sh
```

- Приложение: http://localhost:8080  
- pgAdmin: http://localhost:5050 (admin@mail.com / admin)

## Kubernetes

```bash
docker build -t backend-image:latest -f backend/Dockerfile .
kubectl apply -f k8s/nginx-configmap.yaml
kubectl apply -f contig.yaml
```

## Документация

- [Техническое задание](docs/TZ.md)

