"""Graph exploration API endpoints."""

from fastapi import APIRouter, Depends, Query

from api.dependencies import get_db
from api.schemas import GraphResponse, GraphNodeResponse, GraphEdgeResponse
from src.graph.connection import Neo4jConnection

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("/card/{card_name}", response_model=GraphResponse)
async def get_card_graph(
    card_name: str,
    depth: int = Query(1, ge=1, le=3),
    db: Neo4jConnection = Depends(get_db)
):
    """Get graph centered on a card."""
    query = """
    MATCH (c:Card {name: $name})
    OPTIONAL MATCH (c)-[r1:HAS_MECHANIC]->(m:Mechanic)
    OPTIONAL MATCH (c)-[r2:FILLS_ROLE]->(role:Functional_Role)
    OPTIONAL MATCH (c)-[r3:COMBOS_WITH]->(combo:Card)
    OPTIONAL MATCH (c)-[r4:SIMILAR_TO]->(similar:Card)

    WITH c,
         collect(DISTINCT {node: m, rel: r1, type: 'HAS_MECHANIC'}) AS mechanics,
         collect(DISTINCT {node: role, rel: r2, type: 'FILLS_ROLE'}) AS roles,
         collect(DISTINCT {node: combo, rel: r3, type: 'COMBOS_WITH'}) AS combos,
         collect(DISTINCT {node: similar, rel: r4, type: 'SIMILAR_TO'}) AS similars

    RETURN c AS center,
           mechanics, roles, combos, similars
    """

    results = db.execute_query(query, {"name": card_name})

    if not results:
        return GraphResponse(nodes=[], edges=[])

    r = results[0]
    center = r["center"]

    nodes = [
        GraphNodeResponse(
            id=card_name,
            label=card_name,
            type="Card",
            properties={"cmc": center.get("cmc") if center else None}
        )
    ]
    edges = []

    # Process mechanics
    for item in r.get("mechanics", []):
        if item.get("node"):
            node = item["node"]
            nodes.append(GraphNodeResponse(
                id=f"mech_{node['name']}",
                label=node["name"],
                type="Mechanic",
                properties={}
            ))
            edges.append(GraphEdgeResponse(
                source=card_name,
                target=f"mech_{node['name']}",
                type="HAS_MECHANIC",
                properties={}
            ))

    # Process roles
    for item in r.get("roles", []):
        if item.get("node"):
            node = item["node"]
            nodes.append(GraphNodeResponse(
                id=f"role_{node['name']}",
                label=node["name"],
                type="Role",
                properties={}
            ))
            edges.append(GraphEdgeResponse(
                source=card_name,
                target=f"role_{node['name']}",
                type="FILLS_ROLE",
                properties={}
            ))

    # Process combos
    for item in r.get("combos", []):
        if item.get("node"):
            node = item["node"]
            nodes.append(GraphNodeResponse(
                id=node["name"],
                label=node["name"],
                type="Card",
                properties={}
            ))
            edges.append(GraphEdgeResponse(
                source=card_name,
                target=node["name"],
                type="COMBOS_WITH",
                properties={}
            ))

    # Process similar cards (limit to top 5)
    for item in r.get("similars", [])[:5]:
        if item.get("node"):
            node = item["node"]
            rel = item.get("rel", {})
            nodes.append(GraphNodeResponse(
                id=node["name"],
                label=node["name"],
                type="Card",
                properties={}
            ))
            edges.append(GraphEdgeResponse(
                source=card_name,
                target=node["name"],
                type="SIMILAR_TO",
                properties={"score": rel.get("score", 0) if rel else 0}
            ))

    return GraphResponse(nodes=nodes, edges=edges)


@router.get("/community/{community_id}", response_model=GraphResponse)
async def get_community_graph(
    community_id: int,
    limit: int = Query(50, ge=1, le=200),
    db: Neo4jConnection = Depends(get_db)
):
    """Get cards in a community/archetype cluster."""
    query = """
    MATCH (c:Card)
    WHERE c.community_id = $community_id
    RETURN c.name AS name,
           c.mana_cost AS mana_cost,
           c.type_line AS type_line,
           c.pagerank_score AS pagerank
    ORDER BY c.pagerank_score DESC
    LIMIT $limit
    """

    results = db.execute_query(query, {
        "community_id": community_id,
        "limit": limit
    })

    nodes = [
        GraphNodeResponse(
            id=r["name"],
            label=r["name"],
            type="Card",
            properties={
                "mana_cost": r.get("mana_cost"),
                "pagerank": r.get("pagerank")
            }
        )
        for r in results
    ]

    return GraphResponse(nodes=nodes, edges=[])


@router.get("/similar/{card_name}")
async def get_similar_cards(
    card_name: str,
    limit: int = Query(10, ge=1, le=50),
    db: Neo4jConnection = Depends(get_db)
):
    """Get cards similar to the given card."""
    query = """
    MATCH (c:Card {name: $name})-[s:SIMILAR_TO]->(other:Card)
    RETURN other.name AS name,
           other.mana_cost AS mana_cost,
           other.type_line AS type_line,
           s.score AS similarity_score
    ORDER BY s.score DESC
    LIMIT $limit
    """

    results = db.execute_query(query, {
        "name": card_name,
        "limit": limit
    })

    return results
