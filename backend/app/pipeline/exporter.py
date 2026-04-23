def export_graph(graph, client):

    # nodes
    for node in graph.nodes:

        client.run(f"""
        MERGE (n:{node.type} {{id: $id}})
        SET n += $features
        """, {
            "id": node.id,
            "features": node.features
        })

    # edges
    for edge in graph.edges:

        client.run(f"""
        MATCH (a {{id: $src}})
        MATCH (b {{id: $dst}})
        MERGE (a)-[r:{edge.type}]->(b)
        SET r.weight = $w
        """, {
            "src": edge.src,
            "dst": edge.dst,
            "w": edge.weight
        })
