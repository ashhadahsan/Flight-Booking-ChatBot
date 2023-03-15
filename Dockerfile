FROM python:3.9
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=120 \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

# we probably need build tools?
RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    python3-dev

WORKDIR /app
RUN chmod -R 777 /app
COPY . /app



RUN --mount=type=cache,target=/root/.cache \
    pip3 install -r requirements.txt
RUN python3 -m spacy download en_core_web_sm
RUN xargs -a packages.txt apt-get install --yes
EXPOSE 80
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]