FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup --home /app appuser \
    && mkdir -p /app/staticfiles \
    && chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

CMD ["gunicorn", "enobfinance.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
