from neo4j import GraphDatabase


class Neo4jClient:
    """
    Production-ready Neo4j client for multi-omics graph ingestion.
    Future-compatible with:
    - agentic graph reasoning
    - omics pipelines
    - LLM query layer
    """

    def __init__(self, uri, user, password):

        self.driver = GraphDatabase.driver(
            uri,
            auth=(user, password)
        )

    # ----------------------------
    # CORE EXECUTION
    # ----------------------------

    def run(self, query, params=None):

        params = params or {}

        with self.driver.session() as session:
            result = session.run(query, params)
            return [record.data() for record in result]

    # ----------------------------
    # WRITE HELPER
    # ----------------------------

    def write(self, query, params=None):

        params = params or {}

        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(query, params)
            )

    # ----------------------------
    # READ HELPER
    # ----------------------------

    def read(self, query, params=None):

        params = params or {}

        with self.driver.session() as session:
            result = session.execute_read(
                lambda tx: tx.run(query, params)
            )
            return [record.data() for record in result]

    # ----------------------------
    # HEALTH CHECK
    # ----------------------------

    def health(self):

        try:
            self.run("RETURN 1 AS ok")
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "detail": str(e)}

    # ----------------------------
    # CLOSE CONNECTION
    # ----------------------------

    def close(self):

        if self.driver:
            self.driver.close()
