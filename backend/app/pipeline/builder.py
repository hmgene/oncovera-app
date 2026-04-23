from models.bioentity import Gene, Promoter, Enhancer
from models.relations import Relation
from models.graph_state import GraphState


def build_graph(cnv_df, meth_df):

    graph = GraphState()

    # CNV → Gene
    for _, row in cnv_df.iterrows():

        gene = Gene(name=row["gene"], cnv=row["log2"])
        graph.add_node(gene)

    # Methylation → Promoter
    for _, row in meth_df.iterrows():

        promoter = Promoter(
            id=row["gene"] + "_promoter",
            methylation=row["beta"]
        )
        graph.add_node(promoter)

    # simple relation
    for gene in cnv_df["gene"]:

        graph.add_edge(
            Relation(
                src=gene,
                dst=gene + "_promoter",
                type="REGULATES",
                weight=1.0
            )
        )

    return graph
