// Контекстное меню для сообщений и чата
document.addEventListener('DOMContentLoaded', function() {
    // Меню для сообщений
    const messageMenu = document.createElement('div');
    messageMenu.id = 'message-context-menu';
    messageMenu.className = 'context-menu';
    messageMenu.innerHTML = `
        <ul>
            <li id="menu-reply">Ответить</li>
            <li id="menu-forward">Переслать</li>
            <li id="menu-pin">Закрепить</li>
            <li id="menu-edit">Редактировать</li>
            <li id="menu-delete">Удалить</li>
        </ul>
    `;
    document.body.appendChild(messageMenu);

    // Меню для чата (заголовок)
    const chatMenu = document.createElement('div');
    chatMenu.id = 'chat-context-menu';
    chatMenu.className = 'context-menu';
    chatMenu.innerHTML = `
        <ul>
            <li id="menu-pin-chat">Закрепить чат</li>
            <li id="menu-delete-chat">Удалить чат</li>
        </ul>
    `;
    document.body.appendChild(chatMenu);

    let currentMessageId = null;
    let currentMessageSenderId = null;
    let currentConversationId = null;

    // Закрытие меню при клике вне
    document.addEventListener('click', function(e) {
        if (!messageMenu.contains(e.target) && e.target !== messageMenu) {
            messageMenu.style.display = 'none';
        }
        if (!chatMenu.contains(e.target) && e.target !== chatMenu) {
            chatMenu.style.display = 'none';
        }
    });

    // Открытие меню для сообщений
    document.addEventListener('contextmenu', function(e) {
        const messageDiv = e.target.closest('.message');
        if (messageDiv) {
            e.preventDefault();
            currentMessageId = messageDiv.dataset.messageId;
            currentMessageSenderId = parseInt(messageDiv.dataset.senderId);
            currentConversationId = window.conversationId;

            messageMenu.style.left = e.pageX + 'px';
            messageMenu.style.top = e.pageY + 'px';
            messageMenu.style.display = 'block';

            const isOwner = (currentMessageSenderId === window.currentUserId);
            document.getElementById('menu-edit').style.display = isOwner ? 'block' : 'none';
            document.getElementById('menu-delete').style.display = isOwner ? 'block' : 'none';
            document.getElementById('menu-pin').style.display = isOwner ? 'block' : 'none';
        } else {
            const chatHeader = e.target.closest('.chat-header');
            if (chatHeader) {
                e.preventDefault();
                chatMenu.style.left = e.pageX + 'px';
                chatMenu.style.top = e.pageY + 'px';
                chatMenu.style.display = 'block';
            }
        }
    });

    // Обработчики пунктов меню сообщений
    document.getElementById('menu-reply').addEventListener('click', function() {
        if (currentMessageId) {
            window.location.href = `/chat/reply/${currentMessageId}/`;
        }
        messageMenu.style.display = 'none';
    });

    document.getElementById('menu-forward').addEventListener('click', function() {
        if (currentMessageId) {
            window.location.href = `/chat/forward/${currentMessageId}/`;
        }
        messageMenu.style.display = 'none';
    });

    document.getElementById('menu-pin').addEventListener('click', function() {
        if (currentMessageId) {
            fetch(`/chat/pin_message/${currentMessageId}/`, {
                method: 'POST',
                headers: {'X-CSRFToken': getCookie('csrftoken')}
            }).then(() => window.location.reload());
        }
        messageMenu.style.display = 'none';
    });

    document.getElementById('menu-edit').addEventListener('click', function() {
        if (currentMessageId) {
            window.location.href = `/chat/edit_message/${currentMessageId}/`;
        }
        messageMenu.style.display = 'none';
    });

    document.getElementById('menu-delete').addEventListener('click', function() {
        if (currentMessageId && confirm('Удалить сообщение?')) {
            fetch(`/chat/delete_message/${currentMessageId}/`, {
                method: 'POST',
                headers: {'X-CSRFToken': getCookie('csrftoken')}
            }).then(response => response.json()).then(data => {
                if (data.status === 'ok') {
                    document.getElementById('msg-' + currentMessageId).remove();
                }
            });
        }
        messageMenu.style.display = 'none';
    });

    // Обработчики меню чата
    document.getElementById('menu-pin-chat').addEventListener('click', function() {
        if (window.conversationId) {
            window.location.href = `/chat/pin/${window.conversationId}/`;
        }
        chatMenu.style.display = 'none';
    });

    document.getElementById('menu-delete-chat').addEventListener('click', function() {
        if (window.conversationId && confirm('Удалить этот чат?')) {
            window.location.href = `/chat/delete_chat/${window.conversationId}/`;
        }
        chatMenu.style.display = 'none';
    });

    // Вспомогательная функция для получения CSRF токена
    if (typeof getCookie === 'undefined') {
        window.getCookie = function(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        };
    }
});