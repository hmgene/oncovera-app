#!/bin/bash

# 1. 프로젝트 디렉토리 구조 생성 (필요시)
echo "🚀 프로스테이트 캔서 멀티오믹스 프로파일러 환경을 초기화합니다..."
mkdir -p data

# 2. Clinical / Survival 마스터 테이블 생성
cat << 'EOF' > data/patient_clinical_survival.csv
patient_id,age,stage,nepc_score,current_drug,drug_effect_score,survival_months,status
PT_001,68,StageIV,0.85,Enzalutamide,0.12,14,1
PT_002,72,StageIII,0.15,Abiraterone,0.78,45,0
PT_003,61,StageIV,0.92,Docetaxel,0.05,8,1
EOF
echo "✅ data/patient_clinical_survival.csv 생성 완료."

# 3. Genomic Profile (Mutation, CNV, GWAS) 테이블 생성 (Vectorization용 고정 구조)
cat << 'EOF' > data/patient_genomic_profile.csv
patient_id,mut_TP53,mut_RB1,mut_PTEN,cnv_MYCN,cnv_AURKA,gwas_risk_score
PT_001,1,1,0,2.4,1.8,0.82
PT_002,0,0,0,1.0,0.9,0.34
PT_003,1,1,1,3.1,2.5,0.91
EOF
echo "✅ data/patient_genomic_profile.csv 생성 완료."

# 4. Visium Spatial / Single-cell 요약 데이터 테이블 생성
cat << 'EOF' > data/patient_spatial_single_cell.csv
patient_id,spot_id,x_coord,y_coord,cell_type,exp_ASCL1,exp_EZH2,exp_SYP
PT_001,spot_1,10,20,Neuroendocrine,4.5,3.8,5.1
PT_001,spot_2,11,21,Neuroendocrine,4.8,4.0,4.9
PT_001,spot_3,12,22,Epithelial,0.2,1.1,0.3
PT_002,spot_1,10,20,Epithelial,0.1,0.5,0.1
PT_002,spot_2,11,21,Epithelial,0.0,0.4,0.2
PT_002,spot_3,12,22,Adeno_Cancer,1.1,2.1,0.8
PT_003,spot_1,10,20,Neuroendocrine,5.2,4.5,5.8
PT_003,spot_2,11,21,Neuroendocrine,5.5,4.8,6.0
PT_003,spot_3,12,22,Neuroendocrine,5.0,4.2,5.5
EOF
echo "✅ data/patient_spatial_single_cell.csv 생성 완료."

# 5. GitHub Pages용 Frontend index.html 생성
# (PapaParse 라이브러리를 추가하여 로컬/원격 CSV를 직접 파싱하도록 강화했습니다.)
cat << 'EOF' > index.html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Precision Prostate Cancer Profiler</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <script src="https://cdn.plot.ly/plotly-2.24.1.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.4.1/papaparse.min.js"></script>
</head>
<body class="bg-slate-900 text-slate-100 p-6">

    <div class="max-w-7xl mx-auto">
        <header class="mb-8 border-b border-slate-700 pb-4">
            <h1 class="text-3xl font-bold text-emerald-400">Multi-Omics Real-time Profiler <span class="text-sm font-normal text-slate-400">v1.1 (Static Core)</span></h1>
            <p class="text-slate-400 mt-1">NEPC Transition & Drug Resistance Optimization Engine (AI Vectorizable Structure)</p>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Left: Clinical Panel -->
            <div class="bg-slate-800 p-6 rounded-xl border border-slate-700">
                <h2 class="text-xl font-semibold mb-4 text-slate-200">환자 프로필 선택</h2>
                <div class="mb-4">
                    <label class="block text-xs text-slate-400 mb-1">Select Patient ID</label>
                    <select id="patientSelect" class="w-full bg-slate-700 border border-slate-600 rounded p-2 text-white">
                        <!-- CSV 데이터를 로드하면 동적으로 채워집니다 -->
                        <option value="">데이터 로딩 중...</option>
                    </select>
                </div>

                <div class="space-y-4 mt-6">
                    <div class="p-4 bg-slate-900/50 rounded-lg">
                        <span class="text-xs text-slate-400 block">NEPC Score (Transition Risk)</span>
                        <span id="nepcScore" class="text-2xl font-black text-rose-500">-</span>
                    </div>
                    <div class="p-4 bg-slate-900/50 rounded-lg">
                        <span class="text-xs text-slate-400 block">Current Treatment</span>
                        <span id="currentDrug" class="text-lg font-bold text-amber-400">-</span>
                    </div>
                    <div class="p-4 bg-slate-900/50 rounded-lg">
                        <span class="text-xs text-slate-400 block">Predicted Survival</span>
                        <span id="survivalMonths" class="text-2xl font-black text-emerald-400">-</span>
                    </div>
                </div>
            </div>

            <!-- Right: Visium Spatial Panel -->
            <div class="bg-slate-800 p-6 rounded-xl border border-slate-700 lg:col-span-2">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-xl font-semibold text-slate-200">Visium Spatial Expression Scatter</h2>
                    <span class="text-xs bg-slate-700 px-2 py-1 rounded text-slate-300">Marker: ASCL1</span>
                </div>
                <div id="spatialPlot" class="w-full h-96 bg-slate-900 rounded-lg"></div>
            </div>
        </div>
    </div>

    <script>
        // 전역 상태 저장 객체
        let clinicalData = [];
        let spatialData = [];

        // 데이터 로드 엔진 (PapaParse 사용)
        async function initProfiler() {
            try {
                // CSV 파일 파싱
                const clinicalRes = await fetch('data/patient_clinical_survival.csv').then(r => r.text());
                const spatialRes = await fetch('data/patient_spatial_single_cell.csv').then(r => r.text());

                clinicalData = Papa.parse(clinicalRes, { header: true }).data.filter(row => row.patient_id);
                spatialData = Papa.parse(spatialRes, { header: true }).data.filter(row => row.patient_id);

                // 셀렉트 박스 업데이트
                const selector = document.getElementById('patientSelect');
                selector.innerHTML = '';
                clinicalData.forEach(p => {
                    const opt = document.createElement('option');
                    opt.value = p.patient_id;
                    opt.textContent = `${p.patient_id} (Score: ${p.nepc_score})`;
                    selector.appendChild(opt);
                });

                // 초기 데이터 렌더링
                if(clinicalData.length > 0) {
                    updateDashboard(clinicalData[0].patient_id);
                }

                selector.addEventListener('change', (e) => updateDashboard(e.target.value));

            } catch (error) {
                console.error("데이터 로드 실패. 로컬 서버(Live Server 등) 환경에서 구동해 주세요.", error);
            }
        }

        function updateDashboard(patientId) {
            // 1. 임상 정보 업데이트
            const patient = clinicalData.find(p => p.patient_id === patientId);
            if (patient) {
                document.getElementById('nepcScore').innerText = patient.nepc_score;
                document.getElementById('currentDrug').innerText = `${patient.current_drug} (Effect: ${patient.drug_effect_score})`;
                document.getElementById('survivalMonths').innerText = `${patient.survival_months} Months (${patient.status === '1' ? 'Deceased' : 'Censored'})`;
            }

            // 2. Spatial Plot 데이터 필터링 및 렌더링
            const spots = spatialData.filter(s => s.patient_id === patientId);
            
            const trace = {
                x: spots.map(s => parseFloat(s.x_coord)),
                y: spots.map(s => parseFloat(s.y_coord)),
                mode: 'markers',
                type: 'scatter',
                text: spots.map(s => `${s.cell_type} | SYP: ${s.exp_SYP}`),
                marker: {
                    size: 14,
                    color: spots.map(s => parseFloat(s.exp_ASCL1)),
                    colorscale: 'Jet',
                    showscale: true,
                    colorbar: { title: 'ASCL1 Exp', titlefont: {color: '#fff'}, tickfont: {color: '#fff'} }
                }
            };

            const layout = {
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {l: 40, r: 40, b: 40, t: 10},
                xaxis: { gridcolor: '#334155', tickfont: {color: '#94a3b8'} },
                yaxis: { gridcolor: '#334155', tickfont: {color: '#94a3b8'} }
            };

            Plotly.newPlot('spatialPlot', [trace], layout);
        }

        // 문서 로드 완료 시 구동
        document.addEventListener('DOMContentLoaded', initProfiler);
    </script>
</body>
</html>
EOF
echo "✅ index.html 생성 완료."

# 6. 실행 권한 부여 알림
echo "--------------------------------------------------"
echo "🎉 기본 빌드가 완료되었습니다!"
echo "💡 로컬 보안 정책(CORS) 때문에 index.html을 그냥 더블 클릭하면 CSV를 읽지 못합니다."
echo "💡 'npx serve' 또는 VS Code의 'Live Server'를 켜서 띄워보세요."
echo "💡 GitHub Pages에 push하면 서버 없이 즉시 서빙이 구동됩니다."
echo "--------------------------------------------------"
