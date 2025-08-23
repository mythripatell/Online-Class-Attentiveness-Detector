// dashboard.js

const ctxTrend = document.getElementById('trendChart').getContext('2d');
const ctxLive = document.getElementById('liveChart').getContext('2d');

// Static charts (fake data)
new Chart(ctxTrend, {
  type: 'line',
  data: {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
    datasets: [{
      label: 'Average Attention (%)',
      data: [78, 82, 80, 85, 79],
      borderColor: 'rgba(0, 217, 255, 1)',
      backgroundColor: 'rgba(0, 217, 255, 0.2)',
      fill: true,
      tension: 0.4,
      pointBackgroundColor: '#0ff',
      pointRadius: 5
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: {
        labels: { color: '#fff' }
      }
    },
    scales: {
      x: { ticks: { color: '#eee' } },
      y: { ticks: { color: '#eee' } }
    }
  }
});

new Chart(ctxLive, {
  type: 'doughnut',
  data: {
    labels: ['Attentive', 'Distracted'],
    datasets: [{
      data: [68, 32],
      backgroundColor: ['#00ff88', '#ff3366'],
      borderColor: '#000',
      borderWidth: 3
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom',
        labels: { color: '#fff' }
      }
    },
    cutout: '68%'
  }
});

// Fetch inattention logs and populate table
fetch('/inattention_data')
  .then(response => response.json())
  .then(data => {
    const tbody = document.getElementById('logTableBody');
    data.reverse().forEach(entry => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${entry.timestamp}</td>
        <td>${entry.yaw}</td>
        <td>${entry.pitch}</td>
        <td>${entry.ear}</td>
      `;
      tbody.appendChild(row);
    });
  });
