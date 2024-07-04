FROM registry.access.redhat.com/ubi9/ubi:9.4 as builder

RUN dnf install --nodocs -y \
        python3.11 \
        python3.11-pip && \
    dnf clean all -y

RUN pip3.11 install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-root

FROM registry.access.redhat.com/ubi9/ubi:9.4 as runtime

WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

RUN dnf install --nodocs -y \
    python3.11 && \
    dnf clean all -y

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY LICENSE /licenses/LICENSE

COPY slack_server_mock/ ./slack_server_mock

# For RHEL/Centos 8+ scl_enable isn't sourced automatically in s2i-core
# so virtualenv needs to be activated this way
ENV BASH_ENV="${VIRTUAL_ENV}/bin/activate" \
    ENV="${VIRTUAL_ENV}/bin/activate" \
    PROMPT_COMMAND=". ${VIRTUAL_ENV}/bin/activate"

USER 1001

ENTRYPOINT ["python", "-m", "slack_server_mock"]
