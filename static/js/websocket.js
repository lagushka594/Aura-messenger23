let chatSocket = null;

function initChatSocket(conversationId) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
        chatSocket.close();
    }
    chatSocket = new WebSocket(protocol + '//' + window.location.host + '/ws/chat/' + conversationId + '/');
    
    chatSocket.onopen = function(e) {
        console.log('WebSocket connected to chat', conversationId);
    };
    
    chatSocket.onmessage = function(e) {
        console.log('WebSocket message received:', e.data);
        const data = JSON.parse(e.data);
        if (data.type === 'chat_message') {
            addMessageToChat(data);
        }
    };
    
    chatSocket.onerror = function(e) {
        console.error('WebSocket error:', e);
    };
    
    chatSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly. Code:', e.code, 'Reason:', e.reason, 'Was clean:', e.wasClean);
        // Пытаемся переподключиться через 5 секунд
        setTimeout(() => initChatSocket(conversationId), 5000);
    };
}

function sendMessage(content) {
    if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
        const msg = {
            'type': 'message',
            'content': content
        };
        console.log('Sending message:', msg);
        chatSocket.send(JSON.stringify(msg));
    } else {
        console.error('Chat socket not open. State:', chatSocket ? chatSocket.readyState : 'null');
    }
}

function addMessageToChat(data) {
    console.log('Adding message to chat:', data);
    const messageList = document.getElementById('message-list');
    if (!messageList) {
        console.error('Message list element not found');
        return;
    }

    // Проверяем, не добавлено ли уже это сообщение
    if (document.getElementById('msg-' + data.id)) {
        console.log('Message already exists, skipping');
        return;
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${data.sender_id === window.currentUserId ? 'own' : ''}`;
    messageDiv.id = 'msg-' + data.id;

    const avatar = document.createElement('img');
    avatar.src = data.sender_avatar || '/static/images/default-avatar.png';
    avatar.className = 'avatar-tiny';
    messageDiv.appendChild(avatar);

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    const senderSpan = document.createElement('span');
    senderSpan.className = 'message-sender';
    senderSpan.textContent = data.sender_name;
    bubble.appendChild(senderSpan);

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    if (data.file_url) {
        const link = document.createElement('a');
        link.href = data.file_url;
        link.textContent = data.filename || 'Файл';
        link.target = '_blank';
        contentDiv.appendChild(link);
    } else {
        contentDiv.textContent = data.content;
    }
    bubble.appendChild(contentDiv);

    const timeSpan = document.createElement('span');
    timeSpan.className = 'message-time';
    const date = new Date(data.timestamp);
    timeSpan.textContent = date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    bubble.appendChild(timeSpan);

    messageDiv.appendChild(bubble);
    messageList.appendChild(messageDiv);
    messageList.scrollTop = messageList.scrollHeight;
    console.log('Message added, scrolling to bottom');
}