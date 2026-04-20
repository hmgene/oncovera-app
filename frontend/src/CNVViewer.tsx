import React, { useMemo } from "react";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

interface CNVData {
  chromosome: string;
  start: number;
  end: number;
  copy_number: number;
  log2_ratio: number;
  quality_score: number;
  gene_region: string;
}

interface Props {
  data: CNVData[];
  genomeOffsets: Record<string, number>;
}

const getColor = (v: number) => {
  if (v > 0.2) return "#d62728";
  if (v < -0.2) return "#1f77b4";
  return "#7f7f7f";
};

const CNVViewer: React.FC<Props> = ({ data, genomeOffsets }) => {
  // genome positions
  const chartData = useMemo(() => {
    return data.map((d) => ({
      ...d,
      genomePos:
        (genomeOffsets[d.chromosome] || 0) +
        (d.start + d.end) / 2,
    }));
  }, [data, genomeOffsets]);

  // chromosome boundaries
  const boundaries = useMemo(() => {
    return Object.entries(genomeOffsets).map(([chr, offset]) => ({
      chr,
      offset,
    }));
  }, [genomeOffsets]);

  // axis labels
  const chrTicks = useMemo(() => {
    return Object.entries(genomeOffsets).map(([chr, offset]) => ({
      value: offset,
      label: chr,
    }));
  }, [genomeOffsets]);

  return (
    <div style={{ width: "100%", height: 380 }}>
      <ResponsiveContainer>
        <ScatterChart>
          <CartesianGrid stroke="#eee" />

          {/* chromosome boundary lines */}
          {boundaries.map((b) => (
            <ReferenceLine
              key={b.chr}
              x={b.offset}
              stroke="#ccc"
              strokeDasharray="3 3"
            />
          ))}

          {/* X axis */}
          <XAxis
            type="number"
            dataKey="genomePos"
            ticks={chrTicks.map((t) => t.value)}
            tickFormatter={(v) => {
              const m = chrTicks.find((t) => t.value === v);
              return m ? m.label : "";
            }}
          />

          {/* Y axis */}
          <YAxis type="number" dataKey="log2_ratio" domain={[-2, 2]} />

          {/* tooltip */}
          <Tooltip />

          {/* CNV points */}
          <Scatter
            data={chartData}
            shape={(props: any) => {
              const { cx, cy, payload } = props;
              return (
                <circle
                  cx={cx}
                  cy={cy}
                  r={4}
                  fill={getColor(payload.log2_ratio)}
                />
              );
            }}
          />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CNVViewer;
