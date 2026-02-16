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

function updateFriendStatus(userId, status) {
    const statusSpans = document.querySelectorAll(`.status[data-user-id="${userId}"]`);
    statusSpans.forEach(span => {
        span.className = 'status ' + status;
    });
}