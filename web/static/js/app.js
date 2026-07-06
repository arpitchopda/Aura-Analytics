// AuraAnalytics Dashboard Controller

document.addEventListener("DOMContentLoaded", () => {
    // 1. Navigation & Tabs
    const navItems = document.querySelectorAll(".nav-item");
    const tabPanes = document.querySelectorAll(".tab-pane");
    const pageTitle = document.getElementById("page-title");
    const pageSubtitle = document.getElementById("page-subtitle");

    const tabDetails = {
        "overview": { title: "Executive Sales Overview", subtitle: "Interactive business metrics from the Customer Behavior database" },
        "eda-plots": { title: "Python EDA Visualizations", subtitle: "Static, high-quality analytical figures generated using Pandas & Seaborn" },
        "sql-terminal": { title: "SQL Query Terminal", subtitle: "Write and execute real-time SQLite queries against the transactional tables" },
        "about": { title: "Project Methodology", subtitle: "Deep dive into the architecture, tools, and technical insights of this pipeline" }
    };

    navItems.forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            const tabId = item.getAttribute("data-tab");

            // Update active state in sidebar
            navItems.forEach(nav => nav.classList.remove("active"));
            item.classList.add("active");

            // Show current tab panel
            tabPanes.forEach(pane => pane.classList.remove("active"));
            document.getElementById(`${tabId}-tab`).classList.add("active");

            // Update Page Headers
            if (tabDetails[tabId]) {
                pageTitle.textContent = tabDetails[tabId].title;
                pageSubtitle.textContent = tabDetails[tabId].subtitle;
            }
        });
    });

    // 2. Theme Toggle (Dark / Light Mode)
    const themeToggleBtn = document.getElementById("theme-toggle");
    
    // Check local storage for preference
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "light") {
        document.body.classList.add("light-theme");
        themeToggleBtn.querySelector("svg").innerHTML = `<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>`; // Moon icon
    }

    themeToggleBtn.addEventListener("click", () => {
        document.body.classList.toggle("light-theme");
        const isLight = document.body.classList.contains("light-theme");
        
        if (isLight) {
            localStorage.setItem("theme", "light");
            themeToggleBtn.querySelector("svg").innerHTML = `<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>`; // Moon
        } else {
            localStorage.setItem("theme", "dark");
            themeToggleBtn.querySelector("svg").innerHTML = `<circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.22" x2="5.64" y2="17.78"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>`; // Sun
        }
    });

    // 3. Load & Ingest Aggregated Data cache
    fetch("/dashboard_data.json")
        .then(response => {
            if (!response.ok) throw new Error("Dashboard data cache not compiled yet.");
            return response.json();
        })
        .then(data => {
            populateKPIs(data.kpis);
            renderCharts(data);
            populateVIPTable(data.vip_customers);
        })
        .catch(err => {
            console.error("Error loading dashboard data:", err);
            // Fallback empty UI text or alerts
        });

    function populateKPIs(kpis) {
        if (!kpis) return;
        document.getElementById("kpi-revenue").textContent = formatCurrency(kpis.total_revenue);
        document.getElementById("kpi-orders").textContent = formatNumber(kpis.total_orders);
        document.getElementById("kpi-customers").textContent = formatNumber(kpis.total_customers);
        document.getElementById("kpi-aov").textContent = formatCurrency(kpis.avg_order_value);
    }

    function populateVIPTable(vipList) {
        const tbody = document.querySelector("#vip-table-preview tbody");
        tbody.innerHTML = "";
        
        if (!vipList) return;
        
        vipList.forEach(cust => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${cust.customer_id}</strong></td>
                <td>${cust.location}</td>
                <td>${formatCurrency(cust.lifetime_spend)}</td>
                <td><span class="badge ${cust.subscription_status === 'Yes' ? 'sub' : 'non-sub'}">${cust.subscription_status === 'Yes' ? 'Subscriber' : 'Regular'}</span></td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Helpers
    function formatCurrency(val) {
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 }).format(val);
    }
    function formatNumber(val) {
        return new Intl.NumberFormat('en-US').format(val);
    }

    // 4. Chart.js Renderings
    let charts = {};

    function renderCharts(data) {
        const isLightTheme = () => document.body.classList.contains("light-theme");
        const getGridColor = () => isLightTheme() ? "rgba(0, 0, 0, 0.05)" : "rgba(255, 255, 255, 0.05)";
        const getTextColor = () => isLightTheme() ? "#606473" : "#a5a6b7";

        // Chart.js global defaults
        Chart.defaults.color = getTextColor();
        Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";

        // Watch theme toggler to repaint gridlines on charts
        themeToggleBtn.addEventListener("click", () => {
            setTimeout(() => {
                const gridColor = getGridColor();
                const textColor = getTextColor();
                Chart.defaults.color = textColor;
                
                Object.values(charts).forEach(chart => {
                    if (chart.options.scales) {
                        if (chart.options.scales.x) {
                            chart.options.scales.x.grid.color = gridColor;
                            chart.options.scales.x.ticks.color = textColor;
                        }
                        if (chart.options.scales.y) {
                            chart.options.scales.y.grid.color = gridColor;
                            chart.options.scales.y.ticks.color = textColor;
                        }
                    }
                    chart.update();
                });
            }, 100);
        });

        // Chart 1: Monthly sales trends
        const trendCtx = document.getElementById("monthlyTrendChart").getContext("2d");
        const months = data.monthly_trends.map(t => t.month);
        const revenues = data.monthly_trends.map(t => t.monthly_revenue);
        
        charts.trend = new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [{
                    label: 'Monthly Sales ($)',
                    data: revenues,
                    borderColor: '#29cca3',
                    backgroundColor: 'rgba(41, 204, 163, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: '#a15bf2',
                    pointBorderColor: '#ffffff',
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: getGridColor() }, ticks: { color: getTextColor() } },
                    y: { 
                        grid: { color: getGridColor() }, 
                        ticks: { 
                            color: getTextColor(),
                            callback: (value) => '$' + formatNumber(value)
                        } 
                    }
                }
            }
        });

        // Chart 2: Category sales horizontal bar
        const catCtx = document.getElementById("categorySalesChart").getContext("2d");
        const categories = data.categories.map(c => c.category);
        const catRevenues = data.categories.map(c => c.total_revenue);

        charts.category = new Chart(catCtx, {
            type: 'bar',
            data: {
                labels: categories,
                datasets: [{
                    data: catRevenues,
                    backgroundColor: ['#a15bf2', '#47a0ff', '#29cca3', '#ff6b8b', '#ffc107', '#795548'],
                    borderRadius: 6
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { 
                        grid: { color: getGridColor() }, 
                        ticks: { 
                            color: getTextColor(),
                            callback: (value) => '$' + formatNumber(value)
                        } 
                    },
                    y: { grid: { display: false }, ticks: { color: getTextColor() } }
                }
            }
        });

        // Chart 3: Demographics breakdown
        const demoCtx = document.getElementById("demographicsChart").getContext("2d");
        const ageGroups = data.demographics.map(d => d.age_group);
        const demoSpend = data.demographics.map(d => d.total_spend);

        charts.demo = new Chart(demoCtx, {
            type: 'bar',
            data: {
                labels: ageGroups,
                datasets: [{
                    data: demoSpend,
                    backgroundColor: ['#47a0ff', '#a15bf2', '#ff6b8b', '#29cca3'],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: getTextColor() } },
                    y: { 
                        grid: { color: getGridColor() }, 
                        ticks: { 
                            color: getTextColor(),
                            callback: (value) => '$' + formatNumber(value)
                        } 
                    }
                }
            }
        });

        // Chart 4: Payment methods donut
        const payCtx = document.getElementById("paymentMethodsChart").getContext("2d");
        const methods = data.payment_methods.map(p => p.payment_method);
        const methodShares = data.payment_methods.map(p => p.total_revenue);

        charts.pay = new Chart(payCtx, {
            type: 'doughnut',
            data: {
                labels: methods,
                datasets: [{
                    data: methodShares,
                    backgroundColor: ['#a15bf2', '#47a0ff', '#29cca3', '#ff6b8b'],
                    borderWidth: 2,
                    borderColor: 'rgba(0,0,0,0.1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { boxWidth: 12, padding: 12, color: getTextColor() }
                    }
                },
                cutout: '60%'
            }
        });
    }

    // 5. Interactive SQL Terminal Scripting
    const sqlEditor = document.getElementById("sql-editor");
    const runQueryBtn = document.getElementById("run-query-btn");
    const resultsStatus = document.getElementById("results-status");
    const resultsTableContainer = document.getElementById("results-table-container");
    const resultsHeaders = document.getElementById("results-headers");
    const resultsBody = document.getElementById("results-body");
    const templateButtons = document.querySelectorAll(".template-btn");

    const sqlTemplates = {
        "1": `-- Profitability of Product Categories\nSELECT \n    category,\n    SUM(quantity) AS total_items_sold,\n    ROUND(SUM(total_revenue), 2) AS total_revenue,\n    ROUND(AVG(review_rating), 2) AS average_rating\nFROM transactions\nGROUP BY category\nORDER BY total_revenue DESC;`,
        "2": `-- Customer Lifetime Value (CLV) by Subscription\nSELECT \n    c.subscription_status,\n    COUNT(DISTINCT c.customer_id) AS total_customers,\n    ROUND(SUM(t.total_revenue), 2) AS total_revenue,\n    ROUND(SUM(t.total_revenue) / COUNT(DISTINCT c.customer_id), 2) AS average_revenue_per_customer\nFROM customers c\nLEFT JOIN transactions t ON c.customer_id = t.customer_id\nGROUP BY c.subscription_status;`,
        "3": `-- Subscription Impact on Shopping Cart sizes and Ratings\nSELECT \n    c.subscription_status,\n    COUNT(t.invoice_no) AS total_transactions,\n    ROUND(AVG(t.quantity), 2) AS avg_items_per_order,\n    ROUND(AVG(t.total_revenue), 2) AS average_order_value,\n    ROUND(AVG(t.review_rating), 2) AS average_rating,\n    SUM(CASE WHEN t.discount_applied = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS discount_utilization_pct\nFROM customers c\nJOIN transactions t ON c.customer_id = t.customer_id\nGROUP BY c.subscription_status;`,
        "4": `-- Sales Revenue and Count by States/Locations\nSELECT \n    c.location,\n    COUNT(DISTINCT c.customer_id) AS customer_count,\n    COUNT(t.invoice_no) AS transaction_count,\n    ROUND(SUM(t.total_revenue), 2) AS total_revenue,\n    ROUND(SUM(t.total_revenue) / COUNT(DISTINCT c.customer_id), 2) AS spend_per_customer\nFROM customers c\nJOIN transactions t ON c.customer_id = t.customer_id\nGROUP BY c.location\nORDER BY total_revenue DESC;`,
        "5": `-- Monthly Sales Seasonality Spikes\nSELECT \n    STRFTIME('%Y-%m', invoice_date) AS month,\n    COUNT(DISTINCT invoice_no) AS total_orders,\n    ROUND(SUM(total_revenue), 2) AS monthly_revenue,\n    ROUND(AVG(total_revenue), 2) AS average_order_value\nFROM transactions\nGROUP BY month\nORDER BY month ASC;`,
        "6": `-- Payment Methods Transaction Shares\nSELECT \n    payment_method,\n    COUNT(invoice_no) AS transaction_count,\n    ROUND(SUM(total_revenue), 2) AS total_revenue,\n    ROUND(SUM(total_revenue) * 100.0 / (SELECT SUM(total_revenue) FROM transactions), 2) AS revenue_share_pct\nFROM transactions\nGROUP BY payment_method\nORDER BY total_revenue DESC;`,
        "7": `-- VIP Customer Standings (Top 10 Spenders)\nSELECT \n    c.customer_id,\n    c.age,\n    c.gender,\n    c.location,\n    c.subscription_status,\n    COUNT(t.invoice_no) AS total_orders,\n    ROUND(SUM(t.total_revenue), 2) AS lifetime_spend,\n    ROUND(AVG(t.review_rating), 2) AS avg_given_rating\nFROM customers c\nJOIN transactions t ON c.customer_id = t.customer_id\nGROUP BY c.customer_id\nORDER BY lifetime_spend DESC\nLIMIT 10;`,
        "8": `-- Customer Demographics Summary (Age Groups)\nSELECT \n    CASE \n        WHEN age < 25 THEN 'Under 25'\n        WHEN age BETWEEN 25 AND 40 THEN '25-40'\n        WHEN age BETWEEN 41 AND 55 THEN '41-55'\n        ELSE 'Over 55'\n    END AS age_group,\n    COUNT(DISTINCT c.customer_id) AS customer_count,\n    ROUND(SUM(t.total_revenue), 2) AS total_spend,\n    ROUND(SUM(t.total_revenue) / COUNT(DISTINCT c.customer_id), 2) AS avg_spend_per_customer\nFROM customers c\nJOIN transactions t ON c.customer_id = t.customer_id\nGROUP BY age_group\nORDER BY total_spend DESC;`
    };

    // Load template click handler
    templateButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const queryId = btn.getAttribute("data-query");
            if (sqlTemplates[queryId]) {
                sqlEditor.value = sqlTemplates[queryId];
            }
        });
    });

    // Run Query Call
    runQueryBtn.addEventListener("click", () => {
        const queryText = sqlEditor.value.trim();
        if (!queryText) {
            resultsStatus.textContent = "Please input a SQL query.";
            resultsStatus.className = "status-placeholder";
            resultsTableContainer.classList.add("hidden");
            return;
        }

        resultsStatus.innerHTML = `<span class="loading-spinner">Executing query...</span>`;
        resultsStatus.className = "status-placeholder";
        resultsTableContainer.classList.add("hidden");

        fetch("/api/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: queryText })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                // Show server-side SQL execution error
                resultsStatus.innerHTML = `<div class="error-message">SQL Error: ${data.error}</div>`;
                resultsStatus.className = "";
                resultsTableContainer.classList.add("hidden");
            } else if (data.data && data.data.length > 0) {
                renderQueryResultTable(data.data);
            } else {
                resultsStatus.textContent = "Query executed successfully. No records returned.";
                resultsStatus.className = "status-placeholder";
                resultsTableContainer.classList.add("hidden");
            }
        })
        .catch(err => {
            resultsStatus.innerHTML = `<div class="error-message">Network Error: Could not connect to API server. Make sure server.py is running.</div>`;
            resultsStatus.className = "";
            resultsTableContainer.classList.add("hidden");
        });
    });

    function renderQueryResultTable(records) {
        // Headers
        resultsHeaders.innerHTML = "";
        const columns = Object.keys(records[0]);
        columns.forEach(col => {
            const th = document.createElement("th");
            th.textContent = col;
            resultsHeaders.appendChild(th);
        });

        // Rows
        resultsBody.innerHTML = "";
        records.forEach(row => {
            const tr = document.createElement("tr");
            columns.forEach(col => {
                const td = document.createElement("td");
                const val = row[col];
                
                // Pretty formatting
                if (typeof val === 'number' && col.toLowerCase().includes('revenue') || col.toLowerCase().includes('spend') || col.toLowerCase().includes('value') || col.toLowerCase().includes('price')) {
                    td.textContent = formatCurrency(val);
                } else if (typeof val === 'number' && !col.toLowerCase().includes('age') && !col.toLowerCase().includes('rating') && !col.toLowerCase().includes('id')) {
                    td.textContent = formatNumber(val);
                } else {
                    td.textContent = val !== null ? val : "NULL";
                }
                
                tr.appendChild(td);
            });
            resultsBody.appendChild(tr);
        });

        resultsStatus.classList.add("hidden");
        resultsTableContainer.classList.remove("hidden");
    }
});
