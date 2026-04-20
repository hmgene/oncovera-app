import React, { useEffect, useState } from 'react'

interface CNVData {
  chromosome: string
  start: number
  end: number
  copy_number: number
  log2_ratio: number
  quality_score: number
  gene_region: string
}

interface CancerFractionData {
  cancer_fraction: number
  method: string
  description: string
}

const CNVChart: React.FC = () => {
  const [cnvData, setCnvData] = useState<CNVData[]>([])
  const [cancerFraction, setCancerFraction] = useState<CancerFractionData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedChromosome, setSelectedChromosome] = useState<string>('all')

  useEffect(() => {
    fetchCNVData()
    fetchCancerFraction()
  }, [])

  const fetchCNVData = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/cnv-data', {
        mode: 'cors',
      })
      const data = await response.json()

      if (data.cnv_data) {
        setCnvData(data.cnv_data)
      } else {
        // Fallback to mock data if backend fails
        console.warn('Using mock CNV data due to backend error:', data.error)
        const mockCNVData: CNVData[] = [
          { chromosome: 'chr1', start: 1000000, end: 1500000, copy_number: 2.1, log2_ratio: 0.15, quality_score: 45.2, gene_region: 'intergenic' },
          { chromosome: 'chr1', start: 2500000, end: 2800000, copy_number: 1.8, log2_ratio: -0.25, quality_score: 38.9, gene_region: 'TP53' },
        ]
        setCnvData(mockCNVData)
      }
    } catch (err) {
      console.error('Failed to load CNV data:', err)
      setError('Failed to load CNV data')
      setCnvData([])
    } finally {
      setLoading(false)
    }
  }

  const fetchCancerFraction = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/cancer-fraction', {
        mode: 'cors',
      })
      const data = await response.json()
      setCancerFraction(data)
    } catch (err) {
      console.error('Failed to load cancer fraction:', err)
    }
  }

  const filteredData = selectedChromosome === 'all'
    ? cnvData
    : cnvData.filter(item => item.chromosome === selectedChromosome)

  const chromosomes = ['all', ...Array.from(new Set(cnvData.map(item => item.chromosome)))]

  if (loading) {
    return <div className="cnv-chart-container">Loading CNV data...</div>
  }

  if (error) {
    return <div className="cnv-chart-container error">Error: {error}</div>
  }

  return (
    <div className="cnv-chart-container">
      <h2>CNV Genomic Visualization</h2>

      {cancerFraction && !cancerFraction.error && (
        <div className="cancer-fraction-info">
          <h3>Cancer Fraction Estimate</h3>
          <p><strong>Fraction:</strong> {(cancerFraction.cancer_fraction * 100).toFixed(1)}%</p>
          <p><strong>Method:</strong> {cancerFraction.method}</p>
          <p><em>{cancerFraction.description}</em></p>
        </div>
      )}

      <div className="chart-controls">
        <label>
          Select Chromosome:
          <select
            value={selectedChromosome}
            onChange={(e) => setSelectedChromosome(e.target.value)}
          >
            {chromosomes.map(chr => (
              <option key={chr} value={chr}>
                {chr === 'all' ? 'All Chromosomes' : chr}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="cnv-table-container">
        <h3>CNV Data Table</h3>
        <div className="cnv-table-wrapper">
          <table className="cnv-table">
            <thead>
              <tr>
                <th>Chromosome</th>
                <th>Gene Region</th>
                <th>Log2 Ratio</th>
                <th>Copy Number</th>
                <th>Quality Score</th>
              </tr>
            </thead>
            <tbody>
              {filteredData.map((item, index) => (
                <tr key={index} className={
                  item.log2_ratio > 0.2 ? 'gain' :
                  item.log2_ratio < -0.2 ? 'loss' : 'neutral'
                }>
                  <td>{item.chromosome}</td>
                  <td>{item.gene_region}</td>
                  <td>{item.log2_ratio.toFixed(3)}</td>
                  <td>{item.copy_number.toFixed(2)}</td>
                  <td>{item.quality_score.toFixed(1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="cnv-stats">
        <h3>CNV Statistics</h3>
        <p><strong>Total CNVs:</strong> {filteredData.length}</p>
        <p><strong>Average Log2 Ratio:</strong> {(filteredData.reduce((sum, item) => sum + item.log2_ratio, 0) / filteredData.length || 0).toFixed(3)}</p>
        <p><strong>Significant Alterations:</strong> {filteredData.filter(item => Math.abs(item.log2_ratio) > 0.2).length}</p>
      </div>
    </div>
  )
}

export default CNVChart