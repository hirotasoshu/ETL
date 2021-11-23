FROM elasticsearch:7.10.1 AS builder

LABEL maintainer="rasetsuq@yandex.ru"
LABEL org.opencontainers.image.description ELASTIC_ADMIN_SPRINT_DOCKERFILE

ARG DISCOVERY_TYPE
ENV "discovery.type"=${DISCOVERY_TYPE}

ADD preload.sh /

RUN chmod +x '/preload.sh' \
    && /usr/local/bin/docker-entrypoint.sh elasticsearch -d -E path.data=/tmp/data \
    && while [[ "$(curl -s -o /dev/null -w '%{http_code}' localhost:9200)" != "200" ]]; do sleep 1; done \
    && /preload.sh

FROM builder
COPY --from=builder /tmp/data/ /usr/share/elasticsearch/data/
