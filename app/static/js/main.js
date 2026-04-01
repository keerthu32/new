const API_ENDPOINT = '/api/twin/state';

const state = {
  current: 0,
  temperature: 0,
  degradation: 0,
  failureRisk: 0,
  batteryLevel: 100,
  ts: Date.now(),
};

function clamp(v, min, max) {
  return Math.min(max, Math.max(min, v));
}

function fallbackState(prev) {
  const t = Date.now() / 1000;
  const current = 8 + Math.sin(t * 0.9) * 3 + Math.random() * 0.7;
  const temperature = 34 + Math.sin(t * 0.45) * 8 + Math.random() * 1.1;
  const degradation = clamp(prev.degradation + 0.2, 0, 100);
  const failureRisk = clamp((temperature - 35) * 2 + degradation * 0.3, 0, 100);
  const batteryLevel = clamp(100 - degradation, 5, 100);

  return {
    current,
    temperature,
    degradation,
    failureRisk,
    batteryLevel,
    ts: Date.now(),
    source: 'simulated',
  };
}

async function fetchTwinState(prev) {
  try {
    const res = await fetch(API_ENDPOINT, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return {
      current: Number(data.current) || 0,
      temperature: Number(data.temperature) || 0,
      degradation: Number(data.degradation) || 0,
      failureRisk: Number(data.failure_risk ?? data.failureRisk) || 0,
      batteryLevel: Number(data.battery_level ?? data.batteryLevel) || 100,
      ts: Date.now(),
      source: 'api',
    };
  } catch (_) {
    return fallbackState(prev);
  }
}

function updateMetrics(next) {
  const byId = (id) => document.getElementById(id);
  byId('m-current').textContent = `${next.current.toFixed(2)} A`;
  byId('m-temp').textContent = `${next.temperature.toFixed(1)} °C`;
  byId('m-degradation').textContent = `${next.degradation.toFixed(1)} %`;

  const riskEl = byId('m-risk');
  riskEl.textContent = `${next.failureRisk.toFixed(1)} %`;
  riskEl.className = 'metric-value';
  riskEl.classList.add(next.failureRisk > 65 ? 'danger' : next.failureRisk > 35 ? 'warn' : 'ok');

  const sourceEl = byId('m-source');
  sourceEl.textContent = next.source === 'api' ? 'Live API' : 'Simulated fallback';

  const battery = byId('battery-level');
  battery.style.width = `${clamp(next.batteryLevel, 0, 100)}%`;
  battery.style.background = next.batteryLevel > 40
    ? 'linear-gradient(90deg, var(--c-green), var(--c-cyan))'
    : next.batteryLevel > 20
      ? 'linear-gradient(90deg, var(--c-amber), var(--c-cyan))'
      : 'linear-gradient(90deg, var(--c-red), var(--c-amber))';
}

function initHistoryChart() {
  const el = document.getElementById('trend-chart');
  if (!el || !window.Chart) return null;

  return new Chart(el, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        { label: 'Current (A)', data: [], borderColor: '#00e5ff', tension: 0.3 },
        { label: 'Temp (°C)', data: [], borderColor: '#ff2845', tension: 0.3 },
      ],
    },
    options: {
      animation: false,
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { ticks: { color: '#9ed7e3' }, grid: { color: 'rgba(0,229,255,0.09)' } },
        y: { ticks: { color: '#9ed7e3' }, grid: { color: 'rgba(0,229,255,0.09)' } },
      },
      plugins: {
        legend: { labels: { color: '#d9f1ff' } },
      },
    },
  });
}

function pushPoint(chart, next) {
  if (!chart) return;
  const label = new Date(next.ts).toLocaleTimeString();
  chart.data.labels.push(label);
  chart.data.datasets[0].data.push(Number(next.current.toFixed(2)));
  chart.data.datasets[1].data.push(Number(next.temperature.toFixed(2)));

  const max = 18;
  while (chart.data.labels.length > max) {
    chart.data.labels.shift();
    chart.data.datasets.forEach((s) => s.data.shift());
  }

  chart.update();
}

function initThreeTwin() {
  const host = document.getElementById('three-twin');
  if (!host || !window.THREE) return null;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(55, host.clientWidth / host.clientHeight, 0.1, 100);
  camera.position.set(0, 2.4, 6.5);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(host.clientWidth, host.clientHeight);
  host.appendChild(renderer.domElement);

  const ambient = new THREE.AmbientLight(0x7fdfff, 0.7);
  const key = new THREE.PointLight(0x00e5ff, 1.2, 30);
  key.position.set(3, 4, 5);
  scene.add(ambient, key);

  const board = new THREE.Mesh(
    new THREE.BoxGeometry(6.8, 0.25, 4.6),
    new THREE.MeshStandardMaterial({ color: 0x0b1a2f, emissive: 0x07243d, emissiveIntensity: 0.35 })
  );
  scene.add(board);

  const nodes = [];
  const wires = [];
  const nodeGeometry = new THREE.SphereGeometry(0.14, 18, 18);

  for (let i = 0; i < 10; i++) {
    const node = new THREE.Mesh(
      nodeGeometry,
      new THREE.MeshStandardMaterial({ color: 0x00e5ff, emissive: 0x00b0ff, emissiveIntensity: 0.25 })
    );
    node.position.set(-2.8 + (i % 5) * 1.4, 0.2, -1.4 + Math.floor(i / 5) * 2.8);
    nodes.push(node);
    scene.add(node);
  }

  for (let i = 0; i < nodes.length - 1; i++) {
    const a = nodes[i].position;
    const b = nodes[i + 1].position;
    const path = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(a.x, a.y + 0.02, a.z),
      new THREE.Vector3(b.x, b.y + 0.02, b.z),
    ]);
    const mat = new THREE.LineBasicMaterial({ color: 0x00e5ff, transparent: true, opacity: 0.45 });
    const line = new THREE.Line(path, mat);
    wires.push(line);
    scene.add(line);
  }

  const particles = [];
  const pGeo = new THREE.SphereGeometry(0.06, 12, 12);
  for (let i = 0; i < wires.length; i++) {
    const p = new THREE.Mesh(
      pGeo,
      new THREE.MeshStandardMaterial({ color: 0x00ff9d, emissive: 0x00ff9d, emissiveIntensity: 0.8 })
    );
    p.userData.t = Math.random();
    particles.push(p);
    scene.add(p);
  }

  function onResize() {
    const w = host.clientWidth;
    const h = host.clientHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  }

  window.addEventListener('resize', onResize);

  const twin = {
    setFromState(next) {
      const speed = clamp(next.current / 20, 0.2, 2.4);
      const heat = clamp(next.temperature / 100, 0.2, 1);
      const risk = clamp(next.failureRisk / 100, 0, 1);

      nodes.forEach((n) => {
        n.material.emissiveIntensity = 0.22 + heat * 0.85;
        n.material.color.set(risk > 0.65 ? 0xff2845 : 0x00e5ff);
      });

      wires.forEach((w) => {
        w.material.opacity = 0.25 + speed * 0.2;
        w.material.color.set(risk > 0.65 ? 0xff2845 : 0x00e5ff);
      });

      twin.particleSpeed = speed * 0.006;
      board.material.emissiveIntensity = 0.2 + heat * 0.45;
    },
    particleSpeed: 0.01,
  };

  function animate() {
    requestAnimationFrame(animate);
    const t = performance.now() * 0.001;
    board.rotation.y = Math.sin(t * 0.15) * 0.08;

    particles.forEach((p, i) => {
      const a = nodes[i].position;
      const b = nodes[i + 1].position;
      p.userData.t = (p.userData.t + twin.particleSpeed) % 1;
      p.position.lerpVectors(a, b, p.userData.t);
      p.position.y += 0.12;
    });

    renderer.render(scene, camera);
  }
  animate();

  return twin;
}

async function initDashboard() {
  const chart = initHistoryChart();
  const twin = initThreeTwin();

  async function tick() {
    const next = await fetchTwinState(state);
    Object.assign(state, next);
    updateMetrics(next);
    pushPoint(chart, next);
    twin?.setFromState(next);
  }

  await tick();
  setInterval(tick, 500);
}

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('dashboard-root')) {
    initDashboard();
  }
});
