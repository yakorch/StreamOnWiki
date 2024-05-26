# StreamOnWiki
Implementation of the Wikipedia project proposed on Big Data Processing course at UCU.

# Requirements
- `Docker`
- $8$ GB of RAM.
# System Design
## Deliverables
The application monitors created pages on Wikipedia, and accumulates the following data:
- Domains where the pages were created, referred to as "updated domains";
- Pages by specified users;
- $\#$ of pages created for a specified domain;
- Page information for a specified page ID;
- Users who created at least $1$ page in the specified time range, referred to as "active users".

## Service Dependencies
The micro-service architecture was used for implementation. The dependencies are managed in [`compose.y[a]ml`](compose.yaml) with `depends_on` attribute and environment variables. Common configurations are created at the top to easily add more Cassandra nodes if necessary.

## Main Services
- Kafka;
- Wikipedia events producer;
- Cassandra Cluster consisting of $2$ nodes;
- Spark Cluster: $1$ master and $1$ worker;
- REST API.
## Pipeline
1. The messages are listened from the Wikipedia created pages endpoint by the producer service. If the message has all required fields, it is sent to the Kafka topic `wiki-events`.
2. The messages from `wiki-events` are processed with [Spark Streaming](services/streaming/spark_streaming.py). It 
3. 


## Start the Services

```
docker compose up -d
```


## Stop the Services

```
docker compose down [--volumes]
docker rmi ...  # locally built images
```