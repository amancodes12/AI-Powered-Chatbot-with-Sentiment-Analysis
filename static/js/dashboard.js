/**
 * Dashboard.js - Handles chart rendering and data visualization
 * Creates interactive charts using Chart.js for sentiment analytics
 */

$(document).ready(function() {
    
    // Chart color scheme
    const colors = {
        positive: 'rgba(25, 135, 84, 0.8)',    // Green
        negative: 'rgba(220, 53, 69, 0.8)',    // Red
        neutral: 'rgba(108, 117, 125, 0.8)',   // Gray
        positiveBorder: 'rgba(25, 135, 84, 1)',
        negativeBorder: 'rgba(220, 53, 69, 1)',
        neutralBorder: 'rgba(108, 117, 125, 1)'
    };

    // Chart default configuration
    Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
    Chart.defaults.font.size = 13;

    /**
     * Initialize Sentiment Distribution Pie Chart
     */
    async function initSentimentPieChart() {
        try {
            const response = await fetch('/api/analytics/sentiment');
            const result = await response.json();

            if (!result.success) {
                console.error('Failed to load sentiment data');
                return;
            }

            const data = result.data;

            // Get canvas element
            const ctx = document.getElementById('sentimentPieChart');
            
            if (!ctx) {
                console.error('Pie chart canvas not found');
                return;
            }

            // Create pie chart
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Messages',
                        data: data.values,
                        backgroundColor: [
                            colors.positive,
                            colors.negative,
                            colors.neutral
                        ],
                        borderColor: [
                            colors.positiveBorder,
                            colors.negativeBorder,
                            colors.neutralBorder
                        ],
                        borderWidth: 2,
                        hoverOffset: 10
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                font: {
                                    size: 14
                                },
                                generateLabels: function(chart) {
                                    const data = chart.data;
                                    if (data.labels.length && data.datasets.length) {
                                        return data.labels.map((label, i) => {
                                            const value = data.datasets[0].data[i];
                                            const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
                                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                            
                                            return {
                                                text: `${label}: ${value} (${percentage}%)`,
                                                fillStyle: data.datasets[0].backgroundColor[i],
                                                hidden: false,
                                                index: i
                                            };
                                        });
                                    }
                                    return [];
                                }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                    return `${label}: ${value} messages (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });

        } catch (error) {
            console.error('Error initializing pie chart:', error);
        }
    }

    /**
     * Initialize Sentiment Timeline Line Chart
     */
    async function initSentimentLineChart() {
        try {
            const response = await fetch('/api/analytics/timeline');
            const result = await response.json();

            if (!result.success) {
                console.error('Failed to load timeline data');
                return;
            }

            const data = result.data;

            // Get canvas element
            const ctx = document.getElementById('sentimentLineChart');
            
            if (!ctx) {
                console.error('Line chart canvas not found');
                return;
            }

            // Format dates for display (MM/DD)
            const formattedDates = data.dates.map(date => {
                const d = new Date(date);
                return `${d.getMonth() + 1}/${d.getDate()}`;
            });

            // Create line chart
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: formattedDates,
                    datasets: [
                        {
                            label: 'Positive',
                            data: data.positive,
                            borderColor: colors.positiveBorder,
                            backgroundColor: colors.positive,
                            tension: 0.3,
                            fill: true,
                            pointRadius: 4,
                            pointHoverRadius: 6
                        },
                        {
                            label: 'Negative',
                            data: data.negative,
                            borderColor: colors.negativeBorder,
                            backgroundColor: colors.negative,
                            tension: 0.3,
                            fill: true,
                            pointRadius: 4,
                            pointHoverRadius: 6
                        },
                        {
                            label: 'Neutral',
                            data: data.neutral,
                            borderColor: colors.neutralBorder,
                            backgroundColor: colors.neutral,
                            tension: 0.3,
                            fill: true,
                            pointRadius: 4,
                            pointHoverRadius: 6
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    interaction: {
                        mode: 'index',
                        intersect: false
                    },
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                font: {
                                    size: 14
                                },
                                usePointStyle: true
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.dataset.label || '';
                                    const value = context.parsed.y || 0;
                                    return `${label}: ${value} messages`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1,
                                precision: 0
                            },
                            title: {
                                display: true,
                                text: 'Number of Messages',
                                font: {
                                    size: 13
                                }
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Date',
                                font: {
                                    size: 13
                                }
                            }
                        }
                    }
                }
            });

        } catch (error) {
            console.error('Error initializing line chart:', error);
        }
    }

    /**
     * Initialize all charts
     */
    function initCharts() {
        initSentimentPieChart();
        initSentimentLineChart();
    }

    // Initialize charts when document is ready
    initCharts();

    /**
     * Refresh charts (can be called manually or on interval)
     */
    window.refreshCharts = function() {
        // Clear existing charts
        const pieChart = Chart.getChart('sentimentPieChart');
        const lineChart = Chart.getChart('sentimentLineChart');
        
        if (pieChart) pieChart.destroy();
        if (lineChart) lineChart.destroy();
        
        // Reinitialize
        initCharts();
    };

    // Optional: Auto-refresh every 60 seconds
    // setInterval(refreshCharts, 60000);
});