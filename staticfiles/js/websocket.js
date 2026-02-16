let chatSocket = null;
let statusSocket = null;

function initStatusSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    statusSocket = new WebSocket(protocol + '//' + window.location.host + '/ws/status/');
    
    statusSocket.onopen = function(e) {
        console.log('Status socket connected');
    };
    
    statusSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.type === 'friend_status') {
            updateFriendStatus(data.user_id, data.status);
        }
    };
    
    statusSocket.onerror = function(e) {
        console.error('Status socket error:', e);
    };
    
    statusSocket.onclose = function(e) {
        console.warn('Status socket closed. Reconnecting in 5s...');
        setTimeout(initStatusSocket, 5000);
    };
}

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
        } else if (data.type === 'edit_message') {
            editMessageInChat(data);
        } else if (data.type === 'delete_message') {
            deleteMessageFromChat(data);
        } else if (data.type === 'pin_message') {
            pinMessageInChat(data);
        } else if (data.type === 'unpin_message') {
            unpinMessageInChat();
        }
    };
    
    chatSocket.onerror = function(e) {
        console.error('WebSocket error:', e);
    };
    
    chatSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly. Code:', e.code, 'Reason:', e.reason);
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

    if (document.getElementById('msg-' + data.id)) {
        console.log('Message already exists, skipping');
        return;
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${data.sender_id === window.currentUserId ? 'own' : ''}`;
    messageDiv.id = 'msg-' + data.id;
    messageDiv.setAttribute('data-message-id', data.id);
    messageDiv.setAttribute('data-sender-id', data.sender_id);

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
    if (data.sticker_url) {
        const img = document.createElement('img');
        img.src = data.sticker_url;
        img.alt = 'sticker';
        img.style.maxWidth = '128px';
        img.style.maxHeight = '128px';
        contentDiv.appendChild(img);
    } else if (data.file_url) {
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

function editMessageInChat(data) {
    const msgDiv = document.getElementById('msg-' + data.id);
    if (msgDiv) {
        const contentDiv = msgDiv.querySelector('.message-content');
        contentDiv.innerHTML = data.content + ' <span class="edited">(изменено)</span>';
    }
}

function deleteMessageFromChat(data) {
    const msgDiv = document.getElementById('msg-' + data.id);
    if (msgDiv) msgDiv.remove();
}

function pinMessageInChat(data) {
    // Можно подсветить закреплённое сообщение
    console.log('Message pinned:', data.message_id);
    // Убираем старую подсветку, если есть
    document.querySelectorAll('.pinned-message').forEach(el => el.classList.remove('pinned-message'));
    const msgDiv = document.getElementById('msg-' + data.message_id);
    if (msgDiv) {
        msgDiv.classList.add('pinned-message');
        // Показать баннер с закреплённым сообщением
        const banner = document.getElementById('pinned-banner');
        if (banner) {
            banner.innerHTML = `📌 Закреплено: ${data.content}`;
            banner.style.display = 'block';
        }
    }
}

function unpinMessageInChat() {
    document.querySelectorAll('.pinned-message').forEach(el => el.classList.remove('pinned-message'));
    const banner = document.getElementById('pinned-banner');
    if (banner) banner.style.display = 'none';
}

function updateFriendStatus(userId, status) {
    const statusSpans = document.querySelectorAll(`.status[data-user-id="${userId}"]`);
    statusSpans.forEach(span => {
        span.className = 'status ' + status;
    });
}