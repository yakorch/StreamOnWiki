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
- Number of pages created for a specified domain;
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
The messages are listened from the Wikipedia created pages endpoint by the producer service. If the message has all required fields, it is sent to the Kafka topic `wiki-events`.
The messages from `wiki-events` are processed with [Spark Streaming](services/streaming/spark_streaming.py). They are then being sent to Cassandra tables.
REST API service interacts with Cassandra directly and implements `GET` requests only.

## Tools Justification
- **Kafka**: Kafka is chosen for its ability to provide fast, reliable, and durable process communication. This ensures that messages from the Wikipedia events producer are not lost even if the producer or the Spark Streaming service experience shutdowns. It is easy to maintain and integrates well with other tools.

- **Spark Streaming**: The high throughput of the Wikipedia events stream makes Spark Streaming a great choice: it excels at handling high-volume data streams without the need for immediate real-time processing. It supports for vectorized operations on DataFrames, allowing efficient processing of Kafka messages and seamless data storage in Cassandra. - The well-designed API of Spark Streaming further enhances its ease of use and integration.-

- **Cassandra**: Cassandra is utilized for its superior scalability and ability to handle large volumes of data efficiently. Its distributed architecture ensures high availability and fault tolerance through data replication. Cassandra's flexible schema design allows for optimizing table structures to ensure quick and efficient query responses.

- **FastAPI**: FastAPI is chosen for its high performance and speed in handling HTTP requests. It provides built-in support for request schema definitions and parameter validation.

## Data Modelling
Cassandra table schemas can be found [here](./services/wiki-ddl/ddl.cql). The first $3$ schemas are self-explanatory.
- `domain_pages` lists the number of pages updated for each domain. Column's `num_pages` type `COUNTER` makes updating the table entries easy.
- `active_users_by_date` stores the number of created pages for each user given a date (YYYY-MM-DD format.) `COUNTER` is used for similar purposes as in the previous table.
	When one wants to access the active users for a time period $\text{[start:end]}$, 
	the REST API server iterates over all the dates in-between, and accumulates the results of all the users.
	Note: this approach may not be the most efficient when the length of time interval becomes large, and also it requires to store a lot of data in Cassandra.
	Possible improvements:
	- forbid the requests when the interval length is greater than a month;
	- choose different approach for data modelling.

# Request Examples
After letting the app work for some time, we can verify the availability of REST API.
![updated domains][media/updated_domains.png]
We get the list of domains, which were updated during application uptime.
Let's explore domain `id.wikipedia.org`:
![number of created pages](media/num_created_pages.png)
We see that $6$ pages have been created on this domain.
___
Active users:
![active users](media/active_users.png)
Each active user has three fields: `user_id`, `user_name`, and `num_created_pages`. The result is sorted by `user_id`.

Let's explore the created pages by user account with ID $20$:
![user with ID of 20 activity](media/user_20_activity.png)
Now, we can more details, for example, for page with ID $187294$:
![page information](media/page_info.png)

All the endpoints are tested when the request parameters are missing from DB.



# Start/Stop the Services
Start all with:
```bash
docker compose up -d
```

Stop all:
```bash
docker compose down [--volumes]
docker rmi ...  # locally built images
```

