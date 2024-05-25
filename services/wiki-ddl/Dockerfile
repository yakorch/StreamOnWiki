FROM python:3.9-alpine

# Install the Cassandra CQL shell
RUN apk add --no-cache bash curl \
    && pip install cqlsh

ENTRYPOINT cqlsh -f /code/ddl.cql $(echo $CASSANDRA_SEEDS | cut -d, -f1) 9042