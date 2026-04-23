import pandas as pd
import numpy as np

def load_cnv():

    genes = ["MYC", "TP53", "AR", "FOXA1"]

    return pd.DataFrame({
        "gene": genes,
        "log2": np.random.normal(0, 1, len(genes))
    })


def load_methylation():

    genes = ["MYC", "TP53", "AR", "FOXA1"]

    return pd.DataFrame({
        "gene": genes,
        "beta": np.random.rand(len(genes))
    })
