// charts.js
// Common functionality for Chart.js

document.addEventListener('DOMContentLoaded', function() {
    // Default Chart.js configuration
    if (typeof Chart !== 'undefined') {
        Chart.defaults.font.family = "'Hiragino Kaku Gothic Pro', 'Meiryo', sans-serif";
        Chart.defaults.color = '#cccccc';
        Chart.defaults.scale.grid.color = '#333333';
        Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(0, 0, 0, 0.7)';
        Chart.defaults.plugins.legend.labels.color = '#cccccc';
    }
});
