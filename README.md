# oncovera-app

OnCovera is a modular framework for multi-omics data visualization and analysis, supporting single-cell, spatial, and genomic modalities with future agentic AI integration.

## Project structure

- `backend/`: FastAPI service for synthetic cfDNA ONC prediction using CNV and methylation features.
- `frontend/`: React + Vite app for patient sample input and prediction visualization.

## Getting started

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

## API Usage

### Health Check
```bash
curl http://localhost:8000/health
```

### Get Synthetic Sample
```bash
curl http://localhost:8000/synthetic
```

### Make Prediction
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "cnv_aberration_score": 2.5,
    "methylation_score": 3.1,
    "fragment_size_entropy": 1.8,
    "tumor_fraction": 0.15,
    "age": 65,
    "smoking_history": true,
    "prior_cancer": false
  }'
```

### Calculate Cancer Fraction
```bash
curl http://localhost:8000/cancer-fraction
```
Returns estimated cancer fraction from CNV data using amplitude-based estimation.

### Get CNV Statistics
```bash
curl http://localhost:8000/cnv-statistics
```
Returns statistical summary of CNV data including total CNVs, average log2 ratios, and fraction of genome altered.

### Get CNV Data
```bash
curl http://localhost:8000/cnv-data
```
Returns raw CNV data for visualization and analysis.

## Features

- **Synthetic Data Generation**: CNV, methylation, fragment entropy, tumor fraction based sample generation
- **Risk Prediction**: Malignancy and survival risk prediction
- **CNV Visualization**: Interactive genomic CNV charts with cancer fraction estimation
- **Data Selection**: Filter CNV data by chromosome and view detailed statistics

## Frontend Visualization

The frontend includes an interactive CNV visualization tool with the following features:

- **CNV Data Table**: Tabular display of CNV alterations with color-coded rows
- **Color-coded Alterations**: Red rows for copy number gains, blue for losses, gray for neutral
- **Chromosome Filtering**: Select specific chromosomes or view all data
- **Cancer Fraction Display**: Shows estimated tumor fraction from CNV amplitude
- **CNV Statistics**: Summary statistics including total alterations and significant changes
- **Responsive Design**: Mobile-friendly table with horizontal scrolling

## Future Extensions

- Agentic AI pipeline integration
- Integration with real CNV/methylation cfDNA data
- Tumor staging, risk interpretation, clinical report generation
