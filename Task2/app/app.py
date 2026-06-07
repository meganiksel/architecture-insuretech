"""
Минимальная замена образа ghcr.io/yandex-practicum/scaletestapp.
Тот образ собран только под linux/amd64, поэтому на arm64-хосте
(Apple Silicon) приходится использовать локально собранный аналог
с эквивалентным контрактом:
  GET /          -> отдаёт идентификатор пода
  GET /metrics   -> метрики Prometheus, в т.ч. http_requests_total
Дополнительно намеренно аллоцирует немного памяти на каждый запрос,
чтобы HPA по memory срабатывал быстрее.
"""
import os
import socket
from flask import Flask
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)
POD_ID = os.environ.get("HOSTNAME", socket.gethostname())

REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests served",
    ["path", "method"],
)

# Намеренная аллокация для прогрева HPA по памяти.
_memory_ballast = []


@app.route("/")
def index():
    REQUESTS.labels(path="/", method="GET").inc()
    # ~50 KiB на запрос, не освобождаем — память растёт.
    _memory_ballast.append("x" * 50_000)
    return f"pod: {POD_ID}\n"


@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


@app.route("/healthz")
def healthz():
    return "ok\n"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
