document.addEventListener('DOMContentLoaded', function() {
  // 全体の充足率グラフ
  const overallSufficiencyCtx = document.getElementById('overallSufficiencyChart');
  if (overallSufficiencyCtx) {
    const sufficiency = parseFloat(overallSufficiencyCtx.dataset.sufficiency || '0');

    new Chart(overallSufficiencyCtx, {
      type: 'doughnut',
      data: {
        labels: ['充足', '不足'],
        datasets: [{
          data: [sufficiency, Math.max(0, 100 - sufficiency)],
          backgroundColor: [
            'rgba(75, 192, 192, 0.5)',
            'rgba(255, 99, 132, 0.5)'
          ],
          borderColor: [
            'rgba(75, 192, 192, 1)',
            'rgba(255, 99, 132, 1)'
          ],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          }
        }
      }
    });
  }

  // 製品ごとの担当エンジニア数グラフ
  const productEngineersCtx = document.getElementById('productEngineersChart');
  if (productEngineersCtx) {
    const productsData = JSON.parse(productEngineersCtx.dataset.products || '[]');

    new Chart(productEngineersCtx, {
      type: 'bar',
      data: {
        labels: productsData.map(product => product.name),
        datasets: [{
          label: '担当エンジニア数',
          data: productsData.map(product => product.engineer_count),
          backgroundColor: 'rgba(54, 162, 235, 0.5)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'エンジニア数'
            }
          }
        },
        plugins: {
          legend: {
            display: true
          }
        }
      }
    });
  }

  // 製品ごとの充足率グラフ
  const productSufficiencyCtx = document.getElementById('productSufficiencyChart');
  if (productSufficiencyCtx) {
    const productsData = JSON.parse(productSufficiencyCtx.dataset.products || '[]');

    new Chart(productSufficiencyCtx, {
      type: 'bar',
      data: {
        labels: productsData.map(product => product.name),
        datasets: [{
          label: '充足率',
          data: productsData.map(product => product.sufficiency_rate),
          backgroundColor: 'rgba(75, 192, 192, 0.5)',
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            title: {
              display: true,
              text: '充足率 (%)'
            }
          }
        },
        plugins: {
          legend: {
            display: true
          }
        }
      }
    });
  }

  // エンジニアごとの予測残業時間グラフ
  const engineerOvertimeCtx = document.getElementById('engineerOvertimeChart');
  if (engineerOvertimeCtx) {
    const engineersData = JSON.parse(engineerOvertimeCtx.dataset.engineers || '[]');

    new Chart(engineerOvertimeCtx, {
      type: 'bar',
      data: {
        labels: engineersData.map(engineer => engineer.name),
        datasets: [{
          label: '予測残業時間',
          data: engineersData.map(engineer => engineer.daily_overtime),
          backgroundColor: 'rgba(255, 99, 132, 0.5)',
          borderColor: 'rgba(255, 99, 132, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: '時間/日'
            }
          }
        },
        plugins: {
          legend: {
            display: true
          }
        }
      }
    });
  }

  // エンジニアごとの負荷率グラフ
  const engineerWorkloadCtx = document.getElementById('engineerWorkloadChart');
  if (engineerWorkloadCtx) {
    const engineersData = JSON.parse(engineerWorkloadCtx.dataset.engineers || '[]');

    new Chart(engineerWorkloadCtx, {
      type: 'bar',
      data: {
        labels: engineersData.map(engineer => engineer.name),
        datasets: [{
          label: '負荷率',
          data: engineersData.map(engineer => engineer.workload_percent),
          backgroundColor: 'rgba(255, 205, 86, 0.5)',
          borderColor: 'rgba(255, 205, 86, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: '負荷率 (%)'
            }
          }
        },
        plugins: {
          legend: {
            display: true
          }
        }
      }
    });
  }
});