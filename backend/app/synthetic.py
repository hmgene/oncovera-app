import numpy as np
from .models import PatientSample
import pandas as pd
import os


def make_synthetic_sample(seed: int | None = None) -> PatientSample:
    rng = np.random.default_rng(seed)
    return PatientSample(
        cnv_aberration_score=float(rng.uniform(0.5, 8.5)),
        methylation_score=float(rng.uniform(0.5, 8.0)),
        fragment_size_entropy=float(rng.uniform(0.5, 4.5)),
        tumor_fraction=float(rng.uniform(0.01, 0.35)),
        age=int(rng.integers(25, 85)),
        smoking_history=bool(rng.choice([0, 1], p=[0.55, 0.45])),
        prior_cancer=bool(rng.choice([0, 1], p=[0.75, 0.25])),
    )


def calculate_risk(sample: PatientSample) -> tuple[float, float, str]:
    weights = np.array([0.85, 0.95, 0.55, 1.2, 0.35, 0.4, 1.0])
    inputs = np.array(
        [
            sample.cnv_aberration_score,
            sample.methylation_score,
            sample.fragment_size_entropy,
            sample.tumor_fraction * 10.0,
            sample.age / 100.0,
            float(sample.smoking_history),
            float(sample.prior_cancer),
        ]
    )
    score = 1.0 / (1.0 + np.exp(-(inputs * weights).sum() + -3.25))
    malignancy_risk = float(np.clip(score, 0.0, 1.0))

    survival_risk = float(
        np.clip(
            1.0 - 0.45 * malignancy_risk
            - 0.15 * (sample.age - 50) / 50.0
            - 0.1 * float(sample.smoking_history)
            - 0.12 * float(sample.prior_cancer),
            0.0,
            1.0,
        )
    )

    if malignancy_risk >= 0.75:
        predicted_stage = "high"
    elif malignancy_risk >= 0.45:
        predicted_stage = "medium"
    else:
        predicted_stage = "low"

    return malignancy_risk, survival_risk, predicted_stage


def calculate_cancer_fraction_from_cnv(cnv_file_path: str | None = None) -> float:
    """
    Calculate cancer fraction (tumor fraction) from CNV data.

    Uses a simple amplitude-based estimation where cancer fraction is derived
    from the average absolute log2 ratio of CNV alterations.

    Args:
        cnv_file_path: Path to CNV results TSV file. If None, uses default path.

    Returns:
        Estimated cancer fraction (0.0 to 1.0)
    """
    if cnv_file_path is None:
        cnv_file_path = os.path.join(os.path.dirname(__file__), "data", "cnv_results.tsv")

    try:
        # Read CNV data
        df = pd.read_csv(cnv_file_path, sep='\t')

        # Check if required columns exist
        if 'log2_ratio' not in df.columns:
            raise ValueError("CNV file must contain 'log2_ratio' column")

        # Calculate average absolute log2 ratio
        abs_log2_ratios = df['log2_ratio'].abs()

        # Filter out very small changes (noise) - only consider |log2| > 0.1
        significant_cnvs = abs_log2_ratios[abs_log2_ratios > 0.1]

        if len(significant_cnvs) == 0:
            return 0.0

        # Calculate weighted average of significant CNVs
        avg_abs_log2 = significant_cnvs.mean()

        # Estimate cancer fraction using a sigmoid-like transformation
        # This converts log2 ratio amplitude to tumor fraction
        # Formula: fraction = amplitude / (amplitude + k) where k is a scaling factor
        k = 0.5  # Scaling factor - can be adjusted based on data characteristics
        cancer_fraction = avg_abs_log2 / (avg_abs_log2 + k)

        # Apply bounds
        cancer_fraction = np.clip(cancer_fraction, 0.0, 1.0)

        return float(cancer_fraction)

    except FileNotFoundError:
        raise FileNotFoundError(f"CNV file not found: {cnv_file_path}")
    except Exception as e:
        raise ValueError(f"Error processing CNV file: {str(e)}")


def get_cnv_statistics(cnv_file_path: str | None = None) -> dict:
    """
    Get statistics from CNV data for analysis.

    Args:
        cnv_file_path: Path to CNV results TSV file. If None, uses default path.

    Returns:
        Dictionary with CNV statistics
    """
    if cnv_file_path is None:
        cnv_file_path = os.path.join(os.path.dirname(__file__), "data", "cnv_results.tsv")

    try:
        df = pd.read_csv(cnv_file_path, sep='\t')

        stats = {
            'total_cnvs': len(df),
            'avg_log2_ratio': float(df['log2_ratio'].mean()),
            'std_log2_ratio': float(df['log2_ratio'].std()),
            'max_abs_log2_ratio': float(df['log2_ratio'].abs().max()),
            'significant_cnvs': int((df['log2_ratio'].abs() > 0.1).sum()),
            'fraction_altered': float((df['log2_ratio'].abs() > 0.1).mean())
        }

        return stats

    except Exception as e:
        raise ValueError(f"Error calculating CNV statistics: {str(e)}")
