// Remove the global chart variable
// let chart = null;

// 初始化页面
document.addEventListener('DOMContentLoaded', function() {
    // 设置默认logo
    if (document.querySelector('.logo') && !document.querySelector('.logo').src) {
        // 创建简单的SVG logo
        const svgLogo = `<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40" fill="none">
            <circle cx="20" cy="20" r="18" fill="#4a69bd"/>
            <path d="M14 20C14 17.7909 15.7909 16 18 16H22C24.2091 16 26 17.7909 26 20V24C26 26.2091 24.2091 28 22 28H18C15.7909 28 14 26.2091 14 24V20Z" fill="white"/>
            <circle cx="20" cy="14" r="3" fill="white"/>
        </svg>`;
        
        const logoImg = document.querySelector('.logo');
        logoImg.outerHTML = svgLogo;
    }
});

function createTable(data) {
    const table = document.createElement('table');
    table.className = 'data-table';
    
    // Create header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    Object.keys(data[0]).forEach(key => {
        const th = document.createElement('th');
        th.textContent = key;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Create body
    const tbody = document.createElement('tbody');
    data.forEach(row => {
        const tr = document.createElement('tr');
        Object.values(row).forEach(value => {
            const td = document.createElement('td');
            td.textContent = value;
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    
    return table;
}

function createChart(data) {
    const container = document.createElement('div');
    container.className = 'chart-container';
    const canvas = document.createElement('canvas');
    container.appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    const labels = data.map(row => row[Object.keys(row)[0]]);
    const values = data.map(row => row[Object.keys(row)[1]]);
    
    // Set canvas size to match container
    canvas.style.width = '100%';
    canvas.style.height = '300px';
    
    const newChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: Object.keys(data[0])[1],
                data: values,
                borderColor: '#4a69bd',
                backgroundColor: 'rgba(74, 105, 189, 0.1)',
                tension: 0.1,
                pointRadius: 3,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 20,
                    right: 20,
                    top: 20,
                    bottom: 20
                }
            },
            plugins: {
                legend: {
                    labels: {
                        font: {
                            size: 14
                        },
                        color: '#e6e6e6'
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        font: {
                            size: 12
                        },
                        color: '#a9a9a9',
                        maxRotation: 45,
                        minRotation: 45,
                        autoSkip: false
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        font: {
                            size: 12
                        },
                        color: '#a9a9a9'
                    },
                    grid: {
                        color: 'rgba(62, 64, 70, 0.5)'
                    }
                }
            }
        }
    });
    
    return container;
}

function createViewSwitcher(data) {
    const switcher = document.createElement('div');
    switcher.className = 'view-switcher';
    
    const tableBtn = document.createElement('button');
    tableBtn.textContent = '表格视图';
    tableBtn.className = 'active';
    tableBtn.onclick = () => {
        const content = switcher.nextElementSibling;
        // Clear existing content
        content.innerHTML = '';
        // Create new table
        content.appendChild(createTable(data));
        tableBtn.className = 'active';
        chartBtn.className = '';
    };
    
    const chartBtn = document.createElement('button');
    chartBtn.textContent = '趋势图';
    chartBtn.onclick = () => {
        const content = switcher.nextElementSibling;
        // Clear existing content
        content.innerHTML = '';
        // Create new chart
        content.appendChild(createChart(data));
        tableBtn.className = '';
        chartBtn.className = 'active';
    };
    
    switcher.appendChild(tableBtn);
    switcher.appendChild(chartBtn);
    return switcher;
}

function addMessage(role, content, data = null) {
    const messagesDiv = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (content) {
        const text = document.createElement('p');
        text.textContent = content;
        contentDiv.appendChild(text);
    }
    
    if (data) {
        const dataContainer = document.createElement('div');
        dataContainer.className = 'data-container';
        
        const switcher = createViewSwitcher(data);
        const content = document.createElement('div');
        content.appendChild(createTable(data));
        
        dataContainer.appendChild(switcher);
        dataContainer.appendChild(content);
        contentDiv.appendChild(dataContainer);
    }
    
    messageDiv.appendChild(contentDiv);
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

async function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message
    addMessage('user', message);
    
    // Show loading state
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message assistant';
    loadingDiv.innerHTML = `
        <div class="message-content loading">
            <span>思考中</span>
            <div class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    document.getElementById('chat-messages').appendChild(loadingDiv);
    
    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: message })
        });
        
        const data = await response.json();
        
        // Remove loading state
        loadingDiv.remove();
        
        if (data.error) {
            addMessage('assistant', data.error);
            return;
        }
        
        // Add assistant message with data
        addMessage('assistant', null, data.result);
        
        // Clear input
        input.value = '';
        input.style.height = 'auto';
        
    } catch (error) {
        console.error('Error:', error);
        loadingDiv.remove();
        addMessage('assistant', '发生错误，请稍后重试');
    }
}

// Auto-resize textarea
document.getElementById('user-input').addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
    if (this.scrollHeight > 120) {
        this.style.overflowY = 'auto';
    } else {
        this.style.overflowY = 'hidden';
    }
});

// Send message on Enter (without Shift)
document.getElementById('user-input').addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Send button click
document.getElementById('send-button').addEventListener('click', sendMessage);

// Tool buttons functionality
document.getElementById('deep-think-btn').addEventListener('click', function() {
    const input = document.getElementById('user-input');
    input.value = input.value.trim() ? input.value.trim() + ' [DeepThink]' : '[DeepThink]';
    input.focus();
});

document.getElementById('search-btn').addEventListener('click', function() {
    const input = document.getElementById('user-input');
    input.value = input.value.trim() ? input.value.trim() + ' [Search]' : '[Search]';
    input.focus();
}); 