
class AbstractCassandraClient:
    def __init__(self, host, port, keyspace):
        self.host = host
        self.port = port
        self.keyspace = keyspace
        self.session = None

        self.connect()

    def connect(self):
        from cassandra.cluster import Cluster

        cluster = Cluster([self.host], port=self.port)
        self.session = cluster.connect(self.keyspace)

    def execute(self, query):
        return self.session.execute(query)

    def prepare(self, query):
        return self.session.prepare(query)

    def execute_prepared(self, prepared_query, params):
        self.session.execute(prepared_query, params)

    def close(self):
        if self.session is None:
            return
        self.session.shutdown()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def clean_table(self, table_name):
        self.execute(f"TRUNCATE {table_name};")

    def __del__(self):
        self.close()
