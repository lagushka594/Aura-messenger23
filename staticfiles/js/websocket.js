let statusSocket = null;
let chatSocket = null;

function initStatusSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    statusSocket = new WebSocket(protocol + '//' + window.location.host + '/ws/status/');
    statusSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.type === 'friend_status') {
            updateFriendStatus(data.user_id, data.status);
        }
    };
    statusSocket.onclose = function(e) {
        console.error('Status socket closed unexpectedly');
        setTimeout(initStatusSocket, 5000);
    };
}

function initChatSocket(conversationId) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
        chatSocket.close();
    }
    chatSocket = new WebSocket(protocol + '//' + window.location.host + '/ws/chat/' + conversationId + '/');
    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.type === 'chat_message') {
            addMessageToChat(data);
        }
    };
    chatSocket.onclose = function(e) {
        console.error('Chat socket closed');
    };
}

function sendMessage(content) {
    if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
        chatSocket.send(JSON.stringify({
            'type': 'message',
            'content': content
        }));
    } else {
        console.error('Chat socket not open');
    }
}

// Функция для добавления сообщения в DOM
function addMessageToChat(data) {
    const messageList = document.getElementById('message-list');
    if (!messageList) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    messageDiv.id = 'msg-' + data.message_id;

    // Аватар (заглушка)
    const avatar = document.createElement('img');
    avatar.src = '/static/images/default-avatar.png'; // нужно будет заменить на реальный аватар
    avatar.className = 'avatar-tiny';
    messageDiv.appendChild(avatar);

    const senderSpan = document.createElement('span');
    senderSpan.className = 'sender';
    senderSpan.textContent = data.sender_name;
    messageDiv.appendChild(senderSpan);

    const timeSpan = document.createElement('span');
    timeSpan.className = 'time';
    timeSpan.textContent = new Date(data.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    messageDiv.appendChild(timeSpan);

    const contentDiv = document.createElement('div');
    contentDiv.className = 'content';
    contentDiv.textContent = data.content;
    messageDiv.appendChild(contentDiv);

    messageList.appendChild(messageDiv);
    messageList.scrollTop = messageList.scrollHeight;
}

// Функция обновления статуса друга
function updateFriendStatus(userId, status) {
    const statusSpans = document.querySelectorAll(`.status[data-user-id="${userId}"]`);
    statusSpans.forEach(span => {
        span.className = 'status ' + status;
    });
}