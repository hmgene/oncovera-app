from pipeline.omics_loader import load_cnv, load_methylation
from pipeline.builder import build_graph
from pipeline.exporter import export_graph
from pipeline.neo4j_client import Neo4jClient


def run_ingestion():

    cnv = load_cnv()
    meth = load_methylation()

    graph = build_graph(cnv, meth)

    # ✅ client 생성 필수
    client = Neo4jClient(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="password"
    )

    export_graph(graph, client)

    return {
        "nodes": len(graph.nodes),
        "edges": len(graph.edges)
    }
