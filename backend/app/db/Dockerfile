FROM postgres:15

RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    postgresql-server-dev-15 \
    && git clone https://github.com/pgvector/pgvector.git \
    && cd pgvector \
    && make \
    && make install \
    && cd .. \
    && rm -rf pgvector \
    && apt-get remove -y git build-essential postgresql-server-dev-15 \
    && apt-get autoremove -y \
    && apt-get clean

COPY init.sql /docker-entrypoint-initdb.d/