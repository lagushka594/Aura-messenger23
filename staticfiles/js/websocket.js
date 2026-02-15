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

function addMessageToChat(data) {
    const messageList = document.getElementById('message-list');
    if (!messageList) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    messageDiv.id = 'msg-' + data.message_id;

    const avatar = document.createElement('img');
    avatar.src = '/static/images/default-avatar.png';
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
    contentDiv.textContent = data.content;
    bubble.appendChild(contentDiv);

    const timeSpan = document.createElement('span');
    timeSpan.className = 'message-time';
    timeSpan.textContent = new Date(data.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    bubble.appendChild(timeSpan);

    messageDiv.appendChild(bubble);
    messageList.appendChild(messageDiv);
    messageList.scrollTop = messageList.scrollHeight;
}

function updateFriendStatus(userId, status) {
    const statusSpans = document.querySelectorAll(`.status[data-user-id="${userId}"]`);
    statusSpans.forEach(span => {
        span.className = 'status ' + status;
    });
}