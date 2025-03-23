document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // 自动调整文本框高度
    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        if (this.scrollHeight > 120) {
            this.style.overflowY = 'auto';
        } else {
            this.style.overflowY = 'hidden';
        }
    });

    // 发送消息
    function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        // 添加用户消息到聊天窗口
        addMessage('user', message);
        
        // 清空输入框并重置高度
        userInput.value = '';
        userInput.style.height = 'auto';
        
        // 显示加载状态
        const loadingId = showLoading();
        
        // 发送请求到后端
        fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: message }),
        })
        .then(response => response.json())
        .then(data => {
            // 移除加载状态
            removeLoading(loadingId);
            
            // 显示SQL和结果
            if (data.sql) {
                addMessage('assistant', `生成的SQL查询：\n\`\`\`sql\n${data.sql}\n\`\`\`\n\n${data.result}`);
            } else {
                addMessage('assistant', data.result || data.error || '处理请求时出错');
            }
        })
        .catch(error => {
            // 移除加载状态
            removeLoading(loadingId);
            addMessage('assistant', `发生错误: ${error.message}`);
        });
    }

    // 添加消息到聊天窗口
    function addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // 处理Markdown格式的代码块
        const formattedContent = content.replace(/```([\s\S]*?)```/g, function(match, code) {
            return `<div class="code-block">${code}</div>`;
        });
        
        messageContent.innerHTML = `<p>${formattedContent.replace(/\n/g, '<br>')}</p>`;
        messageDiv.appendChild(messageContent);
        
        chatMessages.appendChild(messageDiv);
        
        // 滚动到底部
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // 显示加载状态
    function showLoading() {
        const loadingId = 'loading-' + Date.now();
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message assistant';
        loadingDiv.id = loadingId;
        
        const loadingContent = document.createElement('div');
        loadingContent.className = 'message-content loading';
        loadingContent.innerHTML = `
            <span>思考中</span>
            <div class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        loadingDiv.appendChild(loadingContent);
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return loadingId;
    }

    // 移除加载状态
    function removeLoading(loadingId) {
        const loadingElement = document.getElementById(loadingId);
        if (loadingElement) {
            loadingElement.remove();
        }
    }

    // 点击发送按钮
    sendButton.addEventListener('click', sendMessage);

    // 按Enter键发送消息
    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // 初始聚焦到输入框
    userInput.focus();
}); 