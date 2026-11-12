import { Chart, LineController, LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js';
import { mortalitySeries, monitoringSeries } from './analytics.js';

Chart.register(LineController, LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Legend);
const palette = ['#087f83', '#4268a0', '#7a647e', '#b45309'];
const instances = new Map();

export function destroyChart(canvas) {
  instances.get(canvas)?.destroy();
  instances.delete(canvas);
}

export function destroyCharts() {
  for (const canvas of instances.keys()) destroyChart(canvas);
}

function draw(canvas, labels, series, yTitle) {
  destroyChart(canvas);
  instances.set(canvas, new Chart(canvas, {
    type: 'line',
    data: {
      labels,
      datasets: series.map((item, i) => ({
        label: item.label, data: item.values,
        borderColor: item.flags ? '#b45309' : palette[i % palette.length],
        backgroundColor: item.flags ? '#b45309' : palette[i % palette.length],
        borderWidth: item.limit ? 1.5 : 2.5,
        borderDash: item.limit ? [6, 5] : [],
        pointRadius: item.flags ? 7 : item.limit ? 0 : 3,
        pointStyle: item.flags ? 'triangle' : 'circle',
        pointHoverRadius: 7, showLine: !item.flags,
        tension: 0, spanGaps: false,
      })),
    },
    options: {
      responsive: true, maintainAspectRatio: false, animation: false,
      interaction: { mode: 'index', intersect: false },
      plugins: { legend: { position: 'bottom', labels: { usePointStyle: true, boxWidth: 10 } }, tooltip: { callbacks: { label: context => `${context.dataset.label}: ${String(context.raw)}` } } },
      scales: {
        x: { title: { display: true, text: 'Calendar quarter' }, grid: { display: false }, ticks: { maxTicksLimit: 12, maxRotation: 45 } },
        y: { title: { display: true, text: yTitle }, grid: { color: '#e6edf2' } },
      },
    },
  }));
}

export function drawMortality(canvas, rows) {
  const data = mortalitySeries(rows);
  draw(canvas, data.labels, [{ label: 'Suspected drug deaths', values: data.values }], 'Suspected deaths (count)');
}

export function drawMonitoring(canvas, rows, configuration) {
  const data = monitoringSeries(rows, configuration);
  draw(canvas, data.labels, data.series, configuration.method === 'CUSUM' ? 'CUSUM (stored scale)' : 'EWMA statistic (stored scale)');
}
