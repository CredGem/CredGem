FROM python:3.10-bullseye

WORKDIR /app


RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends git openssh-client wget

RUN pip install poetry


COPY pyproject.toml .
COPY poetry.lock .

RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY ./src /app/src
COPY ./scripts /app/scripts

COPY ./alembic.ini .
COPY ./alembic /app/alembic

COPY ./scripts/start.sh /app/start.sh
RUN chmod +x /app/start.sh

ENTRYPOINT ["/app/start.sh"]
