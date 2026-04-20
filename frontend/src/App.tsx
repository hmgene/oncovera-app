import React, { useEffect, useState } from 'react'
import './App.css'
import CNVChart from './CNVChart'

interface PatientSample {
  cnv_aberration_score: number
  methylation_score: number
  fragment_size_entropy: number
  tumor_fraction: number
  age: number
  smoking_history: boolean
  prior_cancer: boolean
}

interface PredictionResult {
  malignancy_risk: number
  survival_risk: number
  predicted_stage: string
  explanation: string
}

const defaultSample: PatientSample = {
  cnv_aberration_score: 3.5,
  methylation_score: 3.5,
  fragment_size_entropy: 2.5,
  tumor_fraction: 0.1,
  age: 55,
  smoking_history: false,
  prior_cancer: false,
}

function App() {
  const [sample, setSample] = useState<PatientSample>(defaultSample)
  const [prediction, setPrediction] = useState<PredictionResult | null>(null)
  const [message, setMessage] = useState('Ready to predict with synthetic ONC cfDNA data.')

  useEffect(() => {
    fetch('http://127.0.0.1:8000/synthetic', {
      mode: 'cors',
    })
      .then((res) => res.json())
      .then((data) => setSample(data))
      .catch((error) => {
        console.error('Synthetic data load error:', error)
        setMessage('Could not load synthetic sample automatically. Use manual inputs.')
      })
  }, [])

  const handleChange = (field: keyof PatientSample, value: string | boolean) => {
    setSample((prev) => ({ ...prev, [field]: typeof value === 'string' ? Number(value) : value }))
  }

  const handlePredict = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        mode: 'cors',
        body: JSON.stringify(sample),
      })
      const data: PredictionResult = await response.json()
      setPrediction(data)
      setMessage('Prediction complete.')
    } catch (error) {
      console.error('Prediction error:', error)
      setMessage('Prediction failed — check console for details.')
    }
  }

  return (
    <div className="app-container">
      <header>
        <h1>OnCovera Clinic</h1>
        <p>CNV + methylation 기반 cfDNA ONC 생존/악성도 예측 프레임.</p>
      </header>

      <section className="panel">
        <h2>Patient Sample</h2>
        <div className="field-grid">
          <label>
            CNV Score
            <input
              type="number"
              min="0"
              max="10"
              step="0.1"
              value={sample.cnv_aberration_score}
              onChange={(e) => handleChange('cnv_aberration_score', e.target.value)}
            />
          </label>
          <label>
            Methylation Score
            <input
              type="number"
              min="0"
              max="10"
              step="0.1"
              value={sample.methylation_score}
              onChange={(e) => handleChange('methylation_score', e.target.value)}
            />
          </label>
          <label>
            Fragment Entropy
            <input
              type="number"
              min="0"
              max="5"
              step="0.1"
              value={sample.fragment_size_entropy}
              onChange={(e) => handleChange('fragment_size_entropy', e.target.value)}
            />
          </label>
          <label>
            Tumor Fraction
            <input
              type="number"
              min="0"
              max="1"
              step="0.01"
              value={sample.tumor_fraction}
              onChange={(e) => handleChange('tumor_fraction', e.target.value)}
            />
          </label>
          <label>
            Age
            <input
              type="number"
              min="18"
              max="100"
              value={sample.age}
              onChange={(e) => handleChange('age', e.target.value)}
            />
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={sample.smoking_history}
              onChange={(e) => handleChange('smoking_history', e.target.checked)}
            />
            Smoking History
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={sample.prior_cancer}
              onChange={(e) => handleChange('prior_cancer', e.target.checked)}
            />
            Prior Cancer
          </label>
        </div>
        <button className="predict-button" onClick={handlePredict}>
          Predict
        </button>
        <p className="message">{message}</p>
      </section>

      {prediction && (
        <section className="panel result-panel">
          <h2>Prediction Result</h2>
          <div className="result-row">
            <span>Malignancy Risk</span>
            <strong>{(prediction.malignancy_risk * 100).toFixed(1)}%</strong>
          </div>
          <div className="result-row">
            <span>Survival Risk</span>
            <strong>{(prediction.survival_risk * 100).toFixed(1)}%</strong>
          </div>
          <div className="result-row">
            <span>Predicted Stage</span>
            <strong>{prediction.predicted_stage}</strong>
          </div>
          <p>{prediction.explanation}</p>
        </section>
      )}

      <section className="panel cnv-panel">
        <CNVChart />
      </section>
    </div>
  )
}

export default App
