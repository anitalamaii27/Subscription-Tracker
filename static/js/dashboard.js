// Get chart data from HTML data attributes
const subscriptionChartEl = document.getElementById("subscriptionChart");
const monthlyChartEl = document.getElementById("monthlyChart");

const labels = JSON.parse(subscriptionChartEl.dataset.labels);
const amounts = JSON.parse(subscriptionChartEl.dataset.amounts);

const months = JSON.parse(monthlyChartEl.dataset.months);
const monthlyTotals = JSON.parse(monthlyChartEl.dataset.monthlyTotals);

// -------------------- Subscription Amounts Chart --------------------
const ctx = subscriptionChartEl.getContext('2d');

const chartData = {
    labels: labels,
    datasets: [{
        label: 'Subscription Amounts',
        data: amounts,
        backgroundColor: 'rgba(29, 185, 84, 0.5)',
        borderColor: 'rgba(29, 185, 84, 1)',
        borderWidth: 1
    }]
};

const myChart = new Chart(ctx, {
    type: 'bar',
    data: chartData,
    options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } }
    }
});

// -------------------- Monthly Totals Over Year Chart --------------------
const ctx2 = monthlyChartEl.getContext('2d');

const monthlyData = {
    labels: months,
    datasets: [{
        label: 'Monthly Total ($)',
        data: monthlyTotals,
        backgroundColor: 'rgba(29, 185, 84, 0.3)',
        borderColor: 'rgba(29, 185, 84, 1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4
    }]
};

const monthlyChart = new Chart(ctx2, {
    type: 'line',
    data: monthlyData,
    options: {
        responsive: true,
        plugins: { legend: { display: true } },
        scales: { y: { beginAtZero: true } }
    }
});
