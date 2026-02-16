// Контекстное меню для сообщений и чата
(function() {
    // Вспомогательная функция для получения CSRF токена
    function getCookie(name) {
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
    }
    window.getCookie = getCookie;

    let messageMenu, chatMenu;

    function createMenus() {
        if (!document.getElementById('message-context-menu')) {
            messageMenu = document.createElement('div');
            messageMenu.id = 'message-context-menu';
            messageMenu.className = 'context-menu';
            messageMenu.innerHTML = `
                <ul>
                    <li data-action="reply">Ответить</li>
                    <li data-action="forward">Переслать</li>
                    <li data-action="pin">Закрепить</li>
                    <li data-action="edit">Редактировать</li>
                    <li data-action="delete">Удалить</li>
                    <li data-action="download-file">Скачать файл</li>
                </ul>
            `;
            document.body.appendChild(messageMenu);
        }

        if (!document.getElementById('chat-context-menu')) {
            chatMenu = document.createElement('div');
            chatMenu.id = 'chat-context-menu';
            chatMenu.className = 'context-menu';
            chatMenu.innerHTML = `
                <ul>
                    <li data-action="pin-chat">Закрепить чат</li>
                    <li data-action="delete-chat">Удалить чат</li>
                </ul>
            `;
            document.body.appendChild(chatMenu);
        }
    }

    let currentMessageId = null;
    let currentMessageSenderId = null;
    let currentFileUrl = null;
    let currentFilename = null;

    function handleMessageContextMenu(e) {
        const messageDiv = e.target.closest('.message');
        if (!messageDiv) return;

        e.preventDefault();
        currentMessageId = messageDiv.dataset.messageId;
        currentMessageSenderId = parseInt(messageDiv.dataset.senderId);

        // Проверяем, есть ли в сообщении файл
        const fileLink = messageDiv.querySelector('a[href]');
        const fileImg = messageDiv.querySelector('.chat-image');
        if (fileLink) {
            currentFileUrl = fileLink.href;
            currentFilename = fileLink.textContent;
        } else if (fileImg) {
            currentFileUrl = fileImg.src;
            currentFilename = 'image.jpg';
        } else {
            currentFileUrl = null;
            currentFilename = null;
        }

        // Позиционирование меню
        messageMenu.style.left = e.pageX + 'px';
        messageMenu.style.top = e.pageY + 'px';
        messageMenu.style.display = 'block';

        // Скрыть пункты, недоступные для не-владельца
        const isOwner = (currentMessageSenderId === window.currentUserId);
        messageMenu.querySelector('[data-action="edit"]').style.display = isOwner ? 'block' : 'none';
        messageMenu.querySelector('[data-action="delete"]').style.display = isOwner ? 'block' : 'none';
        messageMenu.querySelector('[data-action="pin"]').style.display = isOwner ? 'block' : 'none';
        messageMenu.querySelector('[data-action="download-file"]').style.display = currentFileUrl ? 'block' : 'none';
    }

    function handleChatContextMenu(e) {
        const chatHeader = e.target.closest('.chat-header');
        if (!chatHeader) return;

        e.preventDefault();
        chatMenu.style.left = e.pageX + 'px';
        chatMenu.style.top = e.pageY + 'px';
        chatMenu.style.display = 'block';
    }

    function handleMenuClick(e) {
        const target = e.target.closest('li');
        if (!target) return;

        const action = target.dataset.action;

        if (action.startsWith('pin-chat') || action.startsWith('delete-chat')) {
            // Меню чата
            switch (action) {
                case 'pin-chat':
                    if (window.conversationId) {
                        window.location.href = `/chat/pin/${window.conversationId}/`;
                    }
                    break;
                case 'delete-chat':
                    if (window.conversationId && confirm('Удалить этот чат?')) {
                        window.location.href = `/chat/delete_chat/${window.conversationId}/`;
                    }
                    break;
            }
            chatMenu.style.display = 'none';
            return;
        }

        // Меню сообщения
        if (!currentMessageId) return;

        switch (action) {
            case 'reply':
                window.location.href = `/chat/reply/${currentMessageId}/`;
                break;
            case 'forward':
                window.location.href = `/chat/forward/${currentMessageId}/`;
                break;
            case 'pin':
                fetch(`/chat/pin_message/${currentMessageId}/`, {
                    method: 'POST',
                    headers: {'X-CSRFToken': getCookie('csrftoken')}
                }).then(() => window.location.reload());
                break;
            case 'edit':
                window.location.href = `/chat/edit_message/${currentMessageId}/`;
                break;
            case 'delete':
                if (confirm('Удалить сообщение?')) {
                    fetch(`/chat/delete_message/${currentMessageId}/`, {
                        method: 'POST',
                        headers: {'X-CSRFToken': getCookie('csrftoken')}
                    }).then(response => response.json()).then(data => {
                        if (data.status === 'ok') {
                            document.getElementById('msg-' + currentMessageId).remove();
                        }
                    });
                }
                break;
            case 'download-file':
                if (currentFileUrl) {
                    const a = document.createElement('a');
                    a.href = currentFileUrl;
                    a.download = currentFilename || 'file';
                    a.click();
                }
                break;
        }
        messageMenu.style.display = 'none';
    }

    function closeMenus(e) {
        if (messageMenu && !messageMenu.contains(e.target)) {
            messageMenu.style.display = 'none';
        }
        if (chatMenu && !chatMenu.contains(e.target)) {
            chatMenu.style.display = 'none';
        }
    }

    // Инициализация
    document.addEventListener('DOMContentLoaded', function() {
        createMenus();

        document.addEventListener('contextmenu', function(e) {
            handleMessageContextMenu(e);
            handleChatContextMenu(e);
        });

        document.addEventListener('click', closeMenus);

        // Обработка кликов по пунктам меню через делегирование
        document.addEventListener('click', handleMenuClick);
    });
})();