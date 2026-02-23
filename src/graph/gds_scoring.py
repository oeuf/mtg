"""Neo4j Graph Data Science scoring operations."""

import logging
from typing import Dict

from src.graph.connection import Neo4jConnection


class GDSScoring:
    """Compute graph-based scores using Neo4j GDS."""

    GRAPH_NAME = "synergy-graph"

    def __init__(self, conn: Neo4jConnection):
        self.conn = conn

    def drop_projection(self, graph_name: str = None):
        """Drop existing graph projection if it exists."""
        name = graph_name or self.GRAPH_NAME
        query = f"""
        CALL gds.graph.drop('{name}', false)
        YIELD graphName
        RETURN graphName
        """
        try:
            self.conn.execute_query(query)
            logging.info("Dropped existing projection '%s'", name)
        except Exception as e:
            logging.warning("Could not drop projection '%s' (may not exist): %s", name, e)

    def create_projection(self) -> Dict:
        """Create in-memory graph projection for GDS algorithms."""
        self.drop_projection()

        query = """
        CALL gds.graph.project(
            'synergy-graph',
            ['Card', 'Commander', 'Mechanic', 'Functional_Role', 'Theme', 'Subtype'],
            {
                HAS_MECHANIC: {orientation: 'UNDIRECTED'},
                FILLS_ROLE: {orientation: 'UNDIRECTED'},
                COMBOS_WITH: {orientation: 'UNDIRECTED'},
                SYNERGIZES_WITH_MECHANIC: {orientation: 'UNDIRECTED'},
                SUPPORTS_THEME: {orientation: 'UNDIRECTED'},
                HAS_SUBTYPE: {orientation: 'UNDIRECTED'}
            }
        )
        YIELD graphName, nodeCount, relationshipCount
        RETURN graphName, nodeCount, relationshipCount
        """

        result = self.conn.execute_query(query)
        if result:
            print(f"✓ Created projection '{self.GRAPH_NAME}'")
            print(f"  Nodes: {result[0]['nodeCount']}")
            print(f"  Relationships: {result[0]['relationshipCount']}")
        return result[0] if result else {}

    def compute_similarity(self, topK: int = 10, similarity_cutoff: float = 0.5) -> Dict:
        """Compute node similarity and write SIMILAR_TO relationships."""
        print(f"Computing node similarity (topK={topK}, cutoff={similarity_cutoff})...")

        query = """
        CALL gds.nodeSimilarity.write('synergy-graph', {
            writeRelationshipType: 'SIMILAR_TO',
            writeProperty: 'score',
            topK: $topK,
            similarityCutoff: $cutoff
        })
        YIELD nodesCompared, relationshipsWritten
        RETURN nodesCompared, relationshipsWritten
        """

        result = self.conn.execute_query(query, {
            "topK": topK,
            "cutoff": similarity_cutoff
        })

        if result:
            print(f"✓ Computed similarity for {result[0]['nodesCompared']} nodes")
            print(f"✓ Created {result[0]['relationshipsWritten']} SIMILAR_TO relationships")

        return result[0] if result else {}

    def create_card_feature_projection(self) -> Dict:
        """Create Card-Feature bipartite projection for similarity."""
        self.drop_projection("card-feature-graph")

        query = """
        CALL gds.graph.project(
            'card-feature-graph',
            {
                Card: {
                    properties: [
                        'cmc_normalized', 'mana_efficiency', 'is_colorless',
                        'color_count', 'is_creature', 'is_instant_sorcery',
                        'is_artifact', 'is_land', 'is_fast_mana_int'
                    ]
                },
                Mechanic: {},
                Functional_Role: {},
                Theme: {},
                Subtype: {},
                Zone: {},
                Phase: {}
            },
            {
                HAS_MECHANIC: {
                    type: 'HAS_MECHANIC',
                    orientation: 'UNDIRECTED'
                },
                FILLS_ROLE: {
                    type: 'FILLS_ROLE',
                    orientation: 'UNDIRECTED'
                },
                SUPPORTS_THEME: {
                    type: 'SUPPORTS_THEME',
                    orientation: 'UNDIRECTED'
                },
                HAS_SUBTYPE: {
                    type: 'HAS_SUBTYPE',
                    orientation: 'UNDIRECTED'
                },
                INTERACTS_WITH_ZONE: {
                    type: 'INTERACTS_WITH_ZONE',
                    orientation: 'UNDIRECTED'
                },
                TRIGGERS_IN_PHASE: {
                    type: 'TRIGGERS_IN_PHASE',
                    orientation: 'UNDIRECTED'
                }
            }
        )
        YIELD graphName, nodeCount, relationshipCount
        RETURN graphName, nodeCount, relationshipCount
        """

        result = self.conn.execute_query(query)
        if result:
            print(f"✓ Created Card-Feature projection: '{result[0]['graphName']}'")
            print(f"  Nodes: {result[0]['nodeCount']}")
            print(f"  Relationships: {result[0]['relationshipCount']}")

        return result[0] if result else {}

    def create_card_synergy_projection(self) -> Dict:
        """Create Card-Card projection for link prediction."""
        self.drop_projection("card-synergy-graph")

        query = """
        CALL gds.graph.project(
            'card-synergy-graph',
            'Card',
            {
                SYNERGIZES_WITH: {
                    orientation: 'UNDIRECTED',
                    properties: {
                        score: {property: 'synergy_score', defaultValue: 0.5}
                    }
                },
                COMBOS_WITH: {
                    orientation: 'UNDIRECTED'
                },
                COMMONLY_PAIRED_WITH: {
                    orientation: 'UNDIRECTED'
                }
            }
        )
        YIELD graphName, nodeCount, relationshipCount
        RETURN graphName, nodeCount, relationshipCount
        """

        result = self.conn.execute_query(query)
        if result:
            print(f"✓ Created Card-Synergy projection: '{result[0]['graphName']}'")
            print(f"  Nodes: {result[0]['nodeCount']}")
            print(f"  Relationships: {result[0]['relationshipCount']}")

        return result[0] if result else {}

    def compute_adamic_adar(self, projection_name: str = "card-synergy-graph") -> Dict:
        """Compute Adamic-Adar link prediction scores."""
        print(f"Computing Adamic-Adar scores on '{projection_name}'...")

        query = """
        CALL gds.alpha.linkprediction.adamicAdar.stream($projection)
        YIELD node1, node2, score
        RETURN gds.util.asNode(node1).name AS card1,
               gds.util.asNode(node2).name AS card2,
               score
        ORDER BY score DESC
        LIMIT 100
        """

        result = self.conn.execute_query(query, {"projection": projection_name})

        if result:
            print(f"✓ Computed Adamic-Adar for {len(result)} card pairs")
            print(f"  Top score: {result[0]['score']:.3f} ({result[0]['card1']} <-> {result[0]['card2']})")

        return {"pairs_scored": len(result), "top_pairs": result[:10] if result else []}

    def compute_common_neighbors(self, projection_name: str = "card-synergy-graph") -> Dict:
        """Compute Common Neighbors link prediction scores."""
        print(f"Computing Common Neighbors on '{projection_name}'...")

        query = """
        CALL gds.alpha.linkprediction.commonNeighbors.stream($projection)
        YIELD node1, node2, score
        RETURN gds.util.asNode(node1).name AS card1,
               gds.util.asNode(node2).name AS card2,
               score
        ORDER BY score DESC
        LIMIT 100
        """

        result = self.conn.execute_query(query, {"projection": projection_name})

        if result:
            print(f"✓ Computed Common Neighbors for {len(result)} card pairs")
            print(f"  Top score: {result[0]['score']:.0f} ({result[0]['card1']} <-> {result[0]['card2']})")

        return {"pairs_scored": len(result), "top_pairs": result[:10] if result else []}

    def compute_leiden_communities(self, projection_name: str = "card-synergy-graph") -> Dict:
        """Run Leiden community detection to find archetypes."""
        print(f"Running Leiden community detection on '{projection_name}'...")

        query = """
        CALL gds.leiden.write(
            $projection,
            {
                writeProperty: 'community'
            }
        )
        YIELD communityCount, modularity, computeMillis
        RETURN communityCount, modularity, computeMillis
        """

        result = self.conn.execute_query(query, {"projection": projection_name})

        if result:
            print(f"✓ Detected {result[0]['communityCount']} communities")
            print(f"  Modularity: {result[0]['modularity']:.3f}")
            print(f"  Time: {result[0]['computeMillis']}ms")

        return result[0] if result else {}

    def boost_intra_community_synergy(self, boost_factor: float = 1.2) -> Dict:
        """Boost synergy scores for cards in same community."""
        print(f"Boosting intra-community synergies by {boost_factor}x...")

        query = """
        MATCH (c1:Card)-[s:SYNERGIZES_WITH]-(c2:Card)
        WHERE c1.community IS NOT NULL
          AND c1.community = c2.community
        SET s.synergy_score = s.synergy_score * $boost,
            s.same_community = true
        RETURN count(s) AS boosted
        """

        result = self.conn.execute_query(query, {"boost": boost_factor})

        if result:
            print(f"✓ Boosted {result[0]['boosted']} intra-community synergies")

        return result[0] if result else {}

    def clear_embedding_similar(self) -> int:
        """Delete all EMBEDDING_SIMILAR relationships."""
        print("Deleting stale EMBEDDING_SIMILAR relationships...")
        query = "MATCH ()-[r:EMBEDDING_SIMILAR]->() DELETE r RETURN count(r) AS deleted"
        result = self.conn.execute_query(query)
        deleted = result[0]["deleted"] if result else 0
        print(f"✓ Deleted {deleted} EMBEDDING_SIMILAR relationships")
        return deleted

    def compute_fastrp_embeddings(self, projection_name: str = "card-feature-graph",
                                  embedding_dim: int = 128) -> Dict:
        """Compute FastRP embeddings for cards using numeric node features."""
        print(f"Computing {embedding_dim}-dim FastRP embeddings on '{projection_name}'...")

        query = """
        CALL gds.fastRP.write(
            $projection,
            {
                embeddingDimension: $dim,
                writeProperty: 'embedding',
                iterationWeights: [0.0, 1.0, 1.0],
                nodeSelfInfluence: 0.3,
                nodeLabels: ['Card'],
                featureProperties: [
                    'cmc_normalized',
                    'mana_efficiency',
                    'is_colorless',
                    'color_count',
                    'is_creature',
                    'is_instant_sorcery',
                    'is_artifact',
                    'is_land',
                    'is_fast_mana_int'
                ],
                propertyRatio: 0.3
            }
        )
        YIELD nodePropertiesWritten, computeMillis
        RETURN nodePropertiesWritten, computeMillis
        """

        result = self.conn.execute_query(query, {
            "projection": projection_name,
            "dim": embedding_dim
        })

        if result:
            print(f"✓ Computed embeddings for {result[0]['nodePropertiesWritten']} nodes")
            print(f"  Time: {result[0]['computeMillis']}ms")

        return result[0] if result else {}

    def compute_knn_similarity(self, topK: int = 20) -> Dict:
        """Compute kNN similarity using embeddings on Card nodes."""
        print(f"Computing kNN similarity (k={topK}) using embeddings...")

        # First create a temporary projection with just Card nodes and embeddings
        self.drop_projection("card-embedding-graph")

        query_project = """
        CALL gds.graph.project(
            'card-embedding-graph',
            {
                Card: {properties: 'embedding'}
            },
            '*'
        )
        YIELD graphName, nodeCount
        RETURN graphName, nodeCount
        """

        proj_result = self.conn.execute_query(query_project)
        if proj_result:
            print(f"  Created temp projection: {proj_result[0]['nodeCount']} nodes")

        query_knn = """
        CALL gds.knn.write(
            'card-embedding-graph',
            {
                nodeProperties: ['embedding'],
                topK: $topK,
                writeRelationshipType: 'EMBEDDING_SIMILAR',
                writeProperty: 'score'
            }
        )
        YIELD nodesCompared, relationshipsWritten, computeMillis
        RETURN nodesCompared, relationshipsWritten, computeMillis
        """

        result = self.conn.execute_query(query_knn, {"topK": topK})

        if result:
            print(f"✓ Compared {result[0]['nodesCompared']} nodes")
            print(f"✓ Created {result[0]['relationshipsWritten']} EMBEDDING_SIMILAR relationships")
            print(f"  Time: {result[0]['computeMillis']}ms")

        # Drop temp projection
        self.drop_projection("card-embedding-graph")

        return result[0] if result else {}
