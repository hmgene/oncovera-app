from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models import PatientSample, PredictionResult
from .synthetic import make_synthetic_sample, calculate_risk, calculate_cancer_fraction_from_cnv, get_cnv_statistics
import pandas as pd
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="OnCovera API",
    description="Synthetic cell-free DNA ONC prediction service for CNV and methylation data.",
    version="0.1.0",
)

origins = ["*"]  # 임시: 모든 origin 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,  # "*" 사용 시 False로 설정
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "OnCovera backend is running."}

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")

@app.get("/patients")
def get_patients():
    patients = []
    for patient_id in os.listdir(DATA_DIR):
        patient_dir = os.path.join(DATA_DIR, patient_id)
        if not os.path.isdir(patient_dir):
            continue

        cnv_file = os.path.join(patient_dir, "cnv", "cnv_results.tsv")
        print(cnv_file)

        if os.path.isfile(cnv_file):
            patients.append(patient_id)

    return {"patients": patients}


@app.get("/synthetic", response_model=PatientSample)
def synthetic_sample():
    return make_synthetic_sample()

@app.post("/predict", response_model=PredictionResult)
def predict(sample: PatientSample):
    malignancy_risk, survival_risk, predicted_stage = calculate_risk(sample)
    explanation = (
        "Model uses synthetic CNV, methylation, tumor fraction, age, smoking history, "
        "and prior cancer to compute malignancy and survival risk scores."
    )
    return {
        "malignancy_risk": malignancy_risk,
        "survival_risk": survival_risk,
        "predicted_stage": predicted_stage,
        "explanation": explanation,
    }


@app.get("/cancer-fraction")
def get_cancer_fraction():
    """
    Calculate cancer fraction (tumor fraction) from CNV data.
    Uses amplitude-based estimation from log2 ratios.
    """
    try:
        cancer_fraction = calculate_cancer_fraction_from_cnv()
        return {
            "cancer_fraction": cancer_fraction,
            "method": "amplitude_based",
            "description": "Estimated from average absolute log2 ratio of significant CNVs"
        }
    except Exception as e:
        return {
            "error": str(e),
            "cancer_fraction": None
        }


@app.get("/cnv-statistics")
def get_cnv_stats():
    """
    Get statistics from CNV data analysis.
    """
    try:
        stats = get_cnv_statistics()
        return {
            "statistics": stats,
            "description": "CNV data summary statistics"
        }
    except Exception as e:
        return {
            "error": str(e),
            "statistics": None
        }



@app.get("/cnv-data")
def get_cnv_data():
    """
    Get raw CNV data for visualization.
    """
    try:
        cnv_file_path = os.path.join(os.path.dirname(__file__), "data", "cnv_results.tsv")
        logger.info(f"Attempting to load CNV data from: {cnv_file_path}")

        # Check if file exists
        if not os.path.exists(cnv_file_path):
            logger.error(f"CNV file not found: {cnv_file_path}")
            return {
                "error": f"CNV file not found: {cnv_file_path}",
                "cnv_data": None
            }

        # Read the file
        logger.info("Reading CNV file with pandas")
        df = pd.read_csv(cnv_file_path, sep='\t')
        logger.info(f"Successfully read {len(df)} rows from CNV file")

        # Validate required columns
        required_columns = ['chromosome', 'start', 'end', 'copy_number', 'log2_ratio', 'quality_score', 'gene_region']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return {
                "error": f"Missing required columns: {missing_columns}",
                "cnv_data": None
            }

        # Convert to list of dictionaries for JSON response
        cnv_data = df.to_dict('records')
        logger.info(f"Converted to {len(cnv_data)} records for JSON response")

        return {
            "cnv_data": cnv_data,
            "total_records": len(cnv_data),
            "description": "Raw CNV data from cfDNA analysis"
        }
    except pd.errors.EmptyDataError:
        logger.error("CNV file is empty")
        return {
            "error": "CNV file is empty",
            "cnv_data": None
        }
    except pd.errors.ParserError as e:
        logger.error(f"Error parsing CNV file: {str(e)}")
        return {
            "error": f"Error parsing CNV file: {str(e)}",
            "cnv_data": None
        }
    except Exception as e:
        logger.error(f"Unexpected error loading CNV data: {str(e)}")
        return {
            "error": f"Unexpected error loading CNV data: {str(e)}",
            "cnv_data": None
        }
