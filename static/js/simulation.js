// シミュレーション用JavaScript

document.addEventListener('DOMContentLoaded', function() {
  // シミュレーションフォーム
  const simulationForm = document.getElementById('simulationForm');
  const runSimulationBtn = document.getElementById('runSimulationBtn');
  
  if (simulationForm && runSimulationBtn) {
    simulationForm.addEventListener('submit', function(event) {
      event.preventDefault();
      
      if (!this.checkValidity()) {
        event.stopPropagation();
        this.classList.add('was-validated');
        return;
      }
      
      // フォームデータ取得
      const formData = new FormData(this);
      
      // ボタンをロード状態に
      runSimulationBtn.disabled = true;
      runSimulationBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 実行中...';
      
      // AJAX リクエスト
      fetch('/simulation/run', {
        method: 'POST',
        body: formData
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('サーバーエラーが発生しました');
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          // 結果を表示
          displaySimulationResults(data);
          // モーダルを閉じる
          const modal = bootstrap.Modal.getInstance(document.getElementById('newSimulationModal'));
          if (modal) modal.hide();
          // フォームをリセット
          simulationForm.reset();
          // 成功メッセージ
          showSuccess('シミュレーションが正常に実行されました');
          // ページをリロード（新しいシミュレーションをリストに表示するため）
          setTimeout(() => {
            location.reload();
          }, 1500);
        } else {
          // エラーメッセージを表示
          if (data.errors) {
            Object.keys(data.errors).forEach(field => {
              const input = document.getElementById(field);
              if (input) {
                input.setCustomValidity(data.errors[field]);
                input.reportValidity();
              }
            });
          } else {
            showError('シミュレーション実行中にエラーが発生しました');
          }
        }
      })
      .catch(error => {
        console.error('Error:', error);
        showError('通信エラーが発生しました: ' + error.message);
      })
      .finally(() => {
        // ボタンを元の状態に戻す
        runSimulationBtn.disabled = false;
        runSimulationBtn.innerHTML = 'シミュレーション実行';
        simulationForm.classList.remove('was-validated');
      });
    });
  }
  
  // 既存のシミュレーション実行ボタン
  document.querySelectorAll('.run-simulation-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      const simulationId = this.getAttribute('data-id');
      
      // ボタンをロード状態に
      this.disabled = true;
      this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
      
      // AJAX リクエスト
      fetch(`/simulation/get/${simulationId}`)
      .then(response => {
        if (!response.ok) {
          throw new Error('サーバーエラーが発生しました');
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          // 結果を表示
          displaySimulationResults(data);
        } else {
          showError('シミュレーション実行中にエラーが発生しました');
        }
      })
      .catch(error => {
        console.error('Error:', error);
        showError('通信エラーが発生しました: ' + error.message);
      })
      .finally(() => {
        // ボタンを元の状態に戻す
        this.disabled = false;
        this.innerHTML = '<i class="fas fa-play"></i>';
      });
    });
  });
  
  // シミュレーション結果表示
  function displaySimulationResults(data) {
    // 結果コンテナを表示
    const resultsContainer = document.getElementById('simulationResults');
    if (resultsContainer) {
      resultsContainer.style.display = 'block';
      
      // シミュレーション名を表示
      const simulationName = document.getElementById('simulationResultName');
      if (simulationName) {
        simulationName.textContent = data.simulation_info.name;
      }
      
      // シミュレーションパラメータを表示
      const paramsList = document.getElementById('simulationParams');
      if (paramsList) {
        paramsList.innerHTML = '';
        
        const params = data.simulation_info.parameters;
        
        const totalEngineersItem = document.createElement('li');
        totalEngineersItem.className = 'list-group-item';
        const currentEngineers = data.current.total_engineers;
        const simEngineers = data.simulation_result.total_engineers;
        totalEngineersItem.innerHTML = `総エンジニア数: <strong>${currentEngineers}人 → ${simEngineers}人</strong> (${params.total_engineers_change >= 0 ? '+' : ''}${params.total_engineers_change}%)`;
        paramsList.appendChild(totalEngineersItem);
        
        const totalProductsItem = document.createElement('li');
        totalProductsItem.className = 'list-group-item';
        const currentProducts = data.current.total_products;
        const simProducts = data.simulation_result.total_products;
        totalProductsItem.innerHTML = `総製品数: <strong>${currentProducts}製品 → ${simProducts}製品</strong> (${params.total_products_change >= 0 ? '+' : ''}${params.total_products_change}%)`;
        paramsList.appendChild(totalProductsItem);
        
        // 各パラメータの元の値を計算（APIから直接取得できないため推測）
        const originalHoursPerInquiry = data.current.products[0]?.annual_inquiries > 0 ? 
            (data.current.products[0]?.required_engineers * data.current.overall_sufficiency / 100) / data.current.products[0]?.annual_inquiries : 1.0;
        const simulatedHoursPerInquiry = originalHoursPerInquiry * (1 + params.hours_per_inquiry_change / 100);
        
        const hoursPerInquiryItem = document.createElement('li');
        hoursPerInquiryItem.className = 'list-group-item';
        hoursPerInquiryItem.innerHTML = `問い合わせあたりの対応時間: <strong>${originalHoursPerInquiry.toFixed(2)}時間 → ${simulatedHoursPerInquiry.toFixed(2)}時間</strong> (${params.hours_per_inquiry_change >= 0 ? '+' : ''}${params.hours_per_inquiry_change}%)`;
        paramsList.appendChild(hoursPerInquiryItem);
        
        // エンジニアあたり製品数上限
        const currentMaxProducts = data.current.engineers.reduce((max, eng) => Math.max(max, eng.product_count), 0);
        const simMaxProducts = Math.ceil(currentMaxProducts * (1 + params.max_products_per_engineer_change / 100));
        
        const maxProductsItem = document.createElement('li');
        maxProductsItem.className = 'list-group-item';
        maxProductsItem.innerHTML = `エンジニアあたり製品数上限: <strong>${currentMaxProducts}製品 → ${simMaxProducts}製品</strong> (${params.max_products_per_engineer_change >= 0 ? '+' : ''}${params.max_products_per_engineer_change}%)`;
        paramsList.appendChild(maxProductsItem);
        
        // 年間問い合わせ件数の変化率
        const annualInquiriesItem = document.createElement('li');
        annualInquiriesItem.className = 'list-group-item';
        const totalInquiries = data.current.products.reduce((sum, p) => sum + p.annual_inquiries, 0);
        const simTotalInquiries = data.simulation_result.products.reduce((sum, p) => sum + p.annual_inquiries, 0);
        annualInquiriesItem.innerHTML = `年間問い合わせ件数: <strong>${totalInquiries}件 → ${simTotalInquiries}件</strong> (${params.annual_inquiries_change >= 0 ? '+' : ''}${params.annual_inquiries_change}%)`;
        paramsList.appendChild(annualInquiriesItem);

        // 問い合わせ対応割合
        // 実際の値の推測は難しいのでパーセンテージのみ表示
        const inquiryWorkRatioItem = document.createElement('li');
        inquiryWorkRatioItem.className = 'list-group-item';
        inquiryWorkRatioItem.innerHTML = `総稼働に対する問い合わせ対応割合の変化率: <strong>${params.inquiry_work_ratio_change >= 0 ? '+' : ''}${params.inquiry_work_ratio_change}%</strong>`;
        paramsList.appendChild(inquiryWorkRatioItem);
      }
      
      // KPI カードを更新
      updateKpiCard('currentEngineersCard', data.current.total_engineers, data.simulation_result.total_engineers);
      updateKpiCard('currentProductsCard', data.current.total_products, data.simulation_result.total_products);
      updateKpiCard('sufficiencyCard', data.current.overall_sufficiency, data.simulation_result.overall_sufficiency, '%');
      updateKpiCard('overtimeCard', data.current.avg_overtime, data.simulation_result.avg_overtime, '時間/日');
      
      // 充足率の比較チャート
      createSufficiencyComparisonChart(data);
      
      // スクロール
      resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }
  }
  
  // KPI カードを更新
  function updateKpiCard(cardId, currentValue, simulationValue, unit = '') {
    const card = document.getElementById(cardId);
    if (card) {
      const currentElement = card.querySelector('.current-value');
      const simulationElement = card.querySelector('.simulation-value');
      const changeElement = card.querySelector('.change-value');
      const changeIconElement = card.querySelector('.change-icon');
      
      if (currentElement) currentElement.textContent = currentValue.toFixed(1) + unit;
      if (simulationElement) simulationElement.textContent = simulationValue.toFixed(1) + unit;
      
      if (changeElement && changeIconElement) {
        const change = simulationValue - currentValue;
        const changePercent = (currentValue !== 0) ? (change / currentValue * 100) : 0;
        
        changeElement.textContent = change.toFixed(1) + unit + ` (${changePercent.toFixed(1)}%)`;
        
        if (change > 0) {
          changeElement.classList.add('text-success');
          changeElement.classList.remove('text-danger');
          changeIconElement.className = 'fas fa-arrow-up me-1 text-success';
        } else if (change < 0) {
          changeElement.classList.add('text-danger');
          changeElement.classList.remove('text-success');
          changeIconElement.className = 'fas fa-arrow-down me-1 text-danger';
        } else {
          changeElement.classList.remove('text-danger', 'text-success');
          changeIconElement.className = 'fas fa-minus me-1';
        }
      }
    }
  }
  
  // 充足率比較チャートの作成
  function createSufficiencyComparisonChart(data) {
    const chartCanvas = document.getElementById('sufficiencyComparisonChart');
    if (!chartCanvas) return;
    
    // 既存のチャートがあれば破棄
    if (chartCanvas.chart) {
      chartCanvas.chart.destroy();
    }
    
    // 製品名のリスト（全製品 - 並べ替えは年間問い合わせ数降順）
    const products = data.current.products
      .sort((a, b) => b.annual_inquiries - a.annual_inquiries);
    
    const labels = products.map(p => p.name);
    const currentSufficiency = products.map(p => p.sufficiency_rate);
    
    // シミュレーション後の充足率データを取得
    const simulationSufficiency = products.map(p => {
      const simProduct = data.simulation_result.products.find(sp => sp.id === p.id);
      return simProduct ? simProduct.sufficiency_rate : 0;
    });
    
    // 製品充足率の比較表を作成
    const chartContainer = document.querySelector('.chart-container-lg').parentElement;
    
    // 既存の表があれば削除
    const existingTable = document.getElementById('sufficiencyTable');
    if (existingTable) existingTable.remove();
    
    // 表を作成
    const tableDiv = document.createElement('div');
    tableDiv.className = 'table-responsive mt-4';
    
    const table = document.createElement('table');
    table.id = 'sufficiencyTable';
    table.className = 'table table-sm table-hover mt-3';
    
    // ヘッダー行
    const thead = document.createElement('thead');
    thead.innerHTML = `
      <tr>
        <th>製品名</th>
        <th>年間問い合わせ数</th>
        <th>現在の充足率</th>
        <th>シミュレーション後</th>
        <th>変化</th>
      </tr>
    `;
    table.appendChild(thead);
    
    // ボディ部分
    const tbody = document.createElement('tbody');
    products.forEach(product => {
      const simProduct = data.simulation_result.products.find(sp => sp.id === product.id);
      if (!simProduct) return;
      
      const row = document.createElement('tr');
      const change = simProduct.sufficiency_rate - product.sufficiency_rate;
      const changeClass = change > 0 ? 'text-success' : (change < 0 ? 'text-danger' : '');
      const changeIcon = change > 0 ? '▲' : (change < 0 ? '▼' : '–');
      
      row.innerHTML = `
        <td>${product.name}</td>
        <td>${product.annual_inquiries}</td>
        <td>${product.sufficiency_rate.toFixed(1)}%</td>
        <td>${simProduct.sufficiency_rate.toFixed(1)}%</td>
        <td class="${changeClass}">${changeIcon} ${Math.abs(change).toFixed(1)}%</td>
      `;
      tbody.appendChild(row);
    });
    table.appendChild(tbody);
    tableDiv.appendChild(table);
    
    // 表をDOMに追加
    chartContainer.appendChild(tableDiv);
    
    // レーダーチャート用に上位20製品を抽出
    const displayCount = 20;
    const displayProducts = products.slice(0, displayCount);
    const displayLabels = displayProducts.map(p => p.name);
    const displayCurrentSufficiency = displayProducts.map(p => p.sufficiency_rate);
    const displaySimulationSufficiency = displayProducts.map(p => {
      const simProduct = data.simulation_result.products.find(sp => sp.id === p.id);
      return simProduct ? simProduct.sufficiency_rate : 0;
    });
    
    chartCanvas.chart = new Chart(chartCanvas, {
      type: 'radar',
      data: {
        labels: displayLabels,
        datasets: [
          {
            label: '現在の充足率',
            data: displayCurrentSufficiency,
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 2,
            pointBackgroundColor: 'rgba(54, 162, 235, 1)',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
          },
          {
            label: 'シミュレーション後の充足率',
            data: displaySimulationSufficiency,
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 2,
            pointBackgroundColor: 'rgba(255, 99, 132, 1)',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: 'rgba(255, 99, 132, 1)'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scale: {
          min: 0,
          max: 100,
          ticks: {
            stepSize: 20
          }
        },
        scales: {
          r: {
            angleLines: {
              display: true
            },
            suggestedMin: 0,
            suggestedMax: 100
          }
        },
        plugins: {
          title: {
            display: true,
            text: '製品充足率比較（上位20製品 - レーダーチャート）',
            font: {
              size: 16
            }
          },
          legend: {
            position: 'top'
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const label = context.dataset.label || '';
                const value = context.raw;
                return `${label}: ${value.toFixed(1)}%`;
              }
            }
          }
        }
      }
    });
  }
  
  // 数値入力の検証
  const numberInputs = document.querySelectorAll('input[type="number"]');
  numberInputs.forEach(function(input) {
    input.addEventListener('input', function() {
      this.setCustomValidity('');
    });
  });
});
