ARG PYTHON_VERSION=3.11.0
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt && \
    apt-get update && \
    apt-get install -y postgresql-client && \
    apt-get install -y libpq-dev && \
    apt-get install -y binutils libproj-dev gdal-bin

COPY . app
WORKDIR /app

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

USER appuser

EXPOSE 8000

# CMD ["entrypoint.sh"]

CMD ["python", "manage.py", "migrate"]
ENTRYPOINT ["/bin/sh", "-c" , "python manage.py migrate && gunicorn --preload --env DJANGO_SETTINGS_MODULE=core.settings -c python:core.config.gunicorn_config core.wsgi"]
