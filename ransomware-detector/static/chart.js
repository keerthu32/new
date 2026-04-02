const btn = document.getElementById("scanBtn");
const statusEl = document.getElementById("status");
const riskEl = document.getElementById("risk");

const points = {
  labels: [],
  datasets: [{
    label: "Ransomware Risk",
    data: [],
    borderColor: "#2457ff",
    backgroundColor: "rgba(36,87,255,.15)",
    tension: 0.25,
    fill: true,
  }],
};

const chart = new Chart(document.getElementById("riskChart"), {
  type: "line",
  data: points,
  options: {
    scales: {
      y: {
        min: 0,
        max: 1,
      },
    },
  },
});

function setRiskClass(label) {
  riskEl.classList.remove("risk-low", "risk-medium", "risk-high");
  riskEl.classList.add(`risk-${label}`);
}

async function runScan() {
  statusEl.textContent = "Scanning local machine...";
  btn.disabled = true;
  try {
    const res = await fetch("/api/scan");
    const data = await res.json();

    document.getElementById("probability").textContent = data.risk_probability;
    document.getElementById("accuracy").textContent = data.model.accuracy;
    document.getElementById("files").textContent = data.scan.files_scanned;
    document.getElementById("entropyFiles").textContent = data.scan.high_entropy_files;
    document.getElementById("suspiciousExt").textContent = data.scan.suspicious_extensions;
    document.getElementById("notes").textContent = data.scan.suspicious_notes;
    document.getElementById("avgEntropy").textContent = data.scan.avg_entropy;
    document.getElementById("root").textContent = data.scan_root;

    riskEl.textContent = data.risk_label;
    setRiskClass(data.risk_label);

    points.labels.push(new Date(data.scanned_at_utc).toLocaleTimeString());
    points.datasets[0].data.push(data.risk_probability);
    if (points.labels.length > 20) {
      points.labels.shift();
      points.datasets[0].data.shift();
    }
    chart.update();

    statusEl.textContent = `Scan complete at ${new Date(data.scanned_at_utc).toLocaleString()}`;
  } catch (error) {
    statusEl.textContent = `Scan failed: ${error}`;
  } finally {
    btn.disabled = false;
  }
}

btn.addEventListener("click", runScan);
