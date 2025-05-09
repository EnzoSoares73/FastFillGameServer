FROM python:3.13 AS builder

RUN pip install poetry==2.1.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR

FROM python:3.13-slim AS runtime

ENV TZ="America/Sao_Paulo"
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"
ENV APP_HOME=/home/web/app

RUN mkdir -p /home/web

RUN addgroup --system web && adduser --system web --ingroup web

RUN mkdir $APP_HOME
WORKDIR $APP_HOME

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY . $APP_HOME

RUN . ${VIRTUAL_ENV}/bin/activate

RUN chown -R web:web $APP_HOME

RUN ["chmod", "+x", "/home/web/app/entrypoint.sh"]

USER web

ENTRYPOINT ["/home/web/app/entrypoint.sh"]