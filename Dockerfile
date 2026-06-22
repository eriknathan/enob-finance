# ─── Base ────────────────────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# ─── Dependencies ────────────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ─── Application ─────────────────────────────────────────────────────────────
COPY . .

# ─── Security (non-root user) ────────────────────────────────────────────────
RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup --home /app appuser \
    && mkdir -p /app/staticfiles \
    && chown -R appuser:appgroup /app

USER appuser

# ─── Runtime ─────────────────────────────────────────────────────────────────
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')" || exit 1

CMD ["gunicorn", "enobfinance.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
