FROM postgres:17
RUN apt-get update && apt-get install -y --no-install-recommends locales \
 && sed -i 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen \
 && locale-gen \
 && rm -rf /var/lib/apt/lists/*
ENV LANG=ru_RU.UTF-8 LC_ALL=ru_RU.UTF-8

COPY initdb/ /docker-entrypoint-initdb.d/
RUN set -eux; \
    sed -i 's/\r$//' /docker-entrypoint-initdb.d/*.sh; \
    chmod 0644 /docker-entrypoint-initdb.d/*.sh
