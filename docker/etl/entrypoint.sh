#!/usr/bin/env sh

set -o errexit
set -o nounset

readonly cmd="$*"

postgres_redis_elastic_ready () {
  # Check that postgres is up and running on port `5432`:
  dockerize -wait "tcp://${POSTGRES_HOST:-172.28.0.2}:${POSTGRES_PORT:-5432}" -wait "tcp://${REDIS_HOST:-redis}:${REDIS_PORT:-6379}" -wait "http://${ELASTICSEARCH_HOST:-elasticsarch}:${ELASTICSEARCH_PORT:-9200}"  -timeout 10s
}

# We need this line to make sure that this container is started
# after the one with postgres, redis and elastic
until postgres_redis_elastic_ready; do
  >&2 echo 'Postgres or elastic or redis is unavailable - sleeping'
done

# It is also possible to wait for other services as well: redis, elastic, mongo
>&2 echo 'Postgres, elastic and redis is up - continuing...'

# Evaluating passed command (do not touch):
# shellcheck disable=SC2086
exec $cmd
