let ecgChart;
const maxPoints = 50;
let dataPoints = [];
let labels = [];

function initChart() {
    const ctx = document.getElementById('ecgChart').getContext('2d');
    ecgChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'ECG Signal (mV)',
                data: dataPoints,
                borderColor: '#00f2fe',
                borderWidth: 2,
                pointRadius: 0,
                fill: true,
                backgroundColor: 'rgba(0, 242, 254, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { min: -0.5, max: 1.5, grid: { color: 'rgba(255,255,255,0.05)' } },
                x: { display: false }
            },
            animation: false,
            plugins: { legend: { display: false } }
        }
    });
}

async function updateDashboard() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();
        
        if (data.length > 0) {
            const latest = data[data.length - 1];
            
            // Update UI metrics
            document.getElementById('battery-val').innerText = `${Math.round(latest.battery)}%`;
            document.getElementById('battery-val').style.color = latest.battery < 20 ? '#ff4b2b' : '#00f2fe';
            
            document.getElementById('ai-prediction').innerText = latest.ai_prediction;
            document.getElementById('ai-confidence').innerText = `Confidence: ${(latest.ai_confidence * 100).toFixed(1)}%`;
            
            const statusBadge = document.getElementById('main-status');
            if (latest.ai_prediction !== 'NORMAL') {
                statusBadge.className = 'status-badge status-alert';
                statusBadge.innerText = latest.ai_prediction;
                document.getElementById('ai-prediction').style.color = '#ff4b2b';
            } else {
                statusBadge.className = 'status-badge status-normal';
                statusBadge.innerText = 'System Nominal';
                document.getElementById('ai-prediction').style.color = '#00ff7f';
            }

            // Update Chart
            const chartData = data.map(d => d.ecg);
            ecgChart.data.labels = data.map(d => '');
            ecgChart.data.datasets[0].data = chartData;
            
            // Dynamic color for ECG if failing
            if (latest.status.includes('ATTACK')) {
                ecgChart.data.datasets[0].borderColor = '#ff4b2b';
                ecgChart.data.datasets[0].backgroundColor = 'rgba(255, 75, 43, 0.1)';
            } else {
                ecgChart.data.datasets[0].borderColor = '#00f2fe';
                ecgChart.data.datasets[0].backgroundColor = 'rgba(0, 242, 254, 0.1)';
            }
            
            ecgChart.update();
        }
    } catch (e) {
        console.error("Fetch error:", e);
    }
}

async function updateBlockchain() {
    const response = await fetch('/api/blockchain');
    const chain = await response.json();
    const container = document.getElementById('blockchain-feed');
    container.innerHTML = '';
    
    chain.reverse().forEach(block => {
        const div = document.createElement('div');
        div.className = 'block-entry';
        div.innerHTML = `
            <strong>Block #${block.index}</strong><br>
            <span style="font-size: 9px; color: #888;">${block.hash.substring(0, 16)}...</span><br>
            ${block.data}
        `;
        container.appendChild(div);
    });
}

async function triggerAttack(type) {
    await fetch('/api/attack', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({type: type})
    });
}

async function triggerFailure() {
    await fetch('/api/failure', {method: 'POST'});
}

async function sendAuthCommand(cmd) {
    const token = document.getElementById('auth-token').value;
    const response = await fetch('/api/command', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({command: cmd, token: token})
    });
    const result = await response.json();
    alert(result.message);
    updateBlockchain();
}

// Initial Run
initChart();
setInterval(updateDashboard, 100);
setInterval(updateBlockchain, 2000);
