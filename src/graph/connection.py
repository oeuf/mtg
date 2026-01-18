"""Manage Neo4j database connection."""

from neo4j import GraphDatabase


class Neo4jConnection:
    """Manage Neo4j database connection."""

    def __init__(self, uri: str, user: str, password: str):
        """Initialize connection to Neo4j."""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        print(f"✓ Connected to Neo4j at {uri}")

    def close(self):
        """Close database connection."""
        self.driver.close()
        print("✓ Connection closed")

    def execute_query(self, query: str, parameters: dict = None):
        """Execute a Cypher query."""
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def create_constraints(self):
        """Create uniqueness constraints and indexes."""

        constraints = [
            # Uniqueness constraints
            "CREATE CONSTRAINT card_name IF NOT EXISTS FOR (c:Card) REQUIRE c.name IS UNIQUE",
            "CREATE CONSTRAINT commander_name IF NOT EXISTS FOR (c:Commander) REQUIRE c.name IS UNIQUE",
            "CREATE CONSTRAINT mechanic_name IF NOT EXISTS FOR (m:Mechanic) REQUIRE m.name IS UNIQUE",
            "CREATE CONSTRAINT role_name IF NOT EXISTS FOR (r:Functional_Role) REQUIRE r.name IS UNIQUE",
            "CREATE CONSTRAINT token_name IF NOT EXISTS FOR (t:Token) REQUIRE t.name IS UNIQUE",

            # Indexes for performance
            "CREATE INDEX card_cmc IF NOT EXISTS FOR (c:Card) ON (c.cmc)",
            "CREATE INDEX card_color_identity IF NOT EXISTS FOR (c:Card) ON (c.color_identity)",
            "CREATE INDEX card_is_legendary IF NOT EXISTS FOR (c:Card) ON (c.is_legendary)",
        ]

        print("Creating constraints and indexes...")
        for constraint in constraints:
            try:
                self.execute_query(constraint)
            except Exception as e:
                # Constraint might already exist
                pass

        print("✓ Constraints and indexes created")
