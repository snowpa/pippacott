// dashboard.js
// This file contains additional JavaScript for the dashboard page

document.addEventListener('DOMContentLoaded', function() {
    // Additional dashboard functionality can be added here
    console.log('Dashboard loaded');
    
    // Function to refresh dashboard data (if needed)
    function refreshDashboardData() {
        fetch('/api/dashboard/data')
            .then(response => response.json())
            .then(data => {
                // Update dashboard data here if needed
                console.log('Dashboard data refreshed');
            })
            .catch(error => {
                console.error('Error refreshing dashboard data:', error);
            });
    }
    
    // Set up refresh interval (every 5 minutes)
    // Uncomment the following line to enable automatic refresh
    // setInterval(refreshDashboardData, 5 * 60 * 1000);
});
