import React, { useEffect, useMemo, useState } from "react";
import CNVViewer from "./CNVViewer";

interface CNVData {
  chromosome: string;
  start: number;
  end: number;
  copy_number: number;
  log2_ratio: number;
  quality_score: number;
  gene_region: string;
}

const CNVChart: React.FC = () => {
  const [cnvData, setCnvData] = useState<CNVData[]>([]);
  const [chromSizes, setChromSizes] = useState<Record<string, number>>({});
  const [selectedChromosome, setSelectedChromosome] = useState("all");

  // fetch CNV data
  useEffect(() => {
    fetch("http://127.0.0.1:8000/cnv-data", { mode: "cors" })
      .then((res) => res.json())
      .then((data) => setCnvData(data.cnv_data || []))
      .catch(() => setCnvData([]));
  }, []);

  // load hg38 genome file
  useEffect(() => {
    fetch("/data/hg38.size")
      .then((res) => res.text())
      .then((text) => {
        const sizes: Record<string, number> = {};

        text.split("\n").forEach((line) => {
          const [chr, size] = line.trim().split(/\s+/);
          if (chr && size) sizes[chr] = Number(size);
        });

        setChromSizes(sizes);
      });
  }, []);

  // build genome offsets
  const genomeOffsets = useMemo(() => {
    let offset = 0;
    const result: Record<string, number> = {};

    Object.entries(chromSizes).forEach(([chr, size]) => {
      result[chr] = offset;
      offset += size;
    });

    return result;
  }, [chromSizes]);

  // filter chromosome
  const filteredData = useMemo(() => {
    if (selectedChromosome === "all") return cnvData;
    return cnvData.filter((d) => d.chromosome === selectedChromosome);
  }, [cnvData, selectedChromosome]);

  const chromosomes = [
    "all",
    ...Array.from(new Set(cnvData.map((d) => d.chromosome))),
  ];

  return (
    <div style={{ padding: 20 }}>
      <h2>CNV Genome Viewer (hg38)</h2>

      {/* controls */}
      <div style={{ marginBottom: 15 }}>
        <label>
          Chromosome:{" "}
          <select
            value={selectedChromosome}
            onChange={(e) => setSelectedChromosome(e.target.value)}
          >
            {chromosomes.map((c) => (
              <option key={c} value={c}>
                {c === "all" ? "Whole Genome" : c}
              </option>
            ))}
          </select>
        </label>
      </div>

      {/* viewer */}
      <CNVViewer
        data={filteredData}
        genomeOffsets={genomeOffsets}
      />
    </div>
  );
};

export default CNVChart;
