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

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.13-slim AS runtime

ARG ENTRYPOINT_SCRIPT

ENV ENTRYPOINT_SCRIPT=$ENTRYPOINT_SCRIPT

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

# chown all the files to the app user
RUN chown -R web:web $APP_HOME

# change to the app user
USER web

ENTRYPOINT ["/bin/sh", "-c", "/home/web/app/${ENTRYPOINT_SCRIPT}"]