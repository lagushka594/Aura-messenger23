// Инициализация WebSocket статусов, если пользователь авторизован
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.user-menu') || document.querySelector('.sidebar')) {
        initStatusSocket();
    }

    const sendBtn = document.getElementById('send-message');
    if (sendBtn) {
        sendBtn.addEventListener('click', function() {
            const input = document.getElementById('chat-message');
            if (input.value.trim()) {
                sendMessage(input.value);
                input.value = '';
            }
        });
        const input = document.getElementById('chat-message');
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendBtn.click();
            }
        });
    }

    // Инициализация эмодзи-пикера
    if (document.getElementById('emoji-picker')) {
        initEmojiPicker();
    }

    // Инициализация drag-and-drop для загрузки файлов
    const conversationIdElement = document.querySelector('script[data-conversation-id]');
    if (conversationIdElement) {
        const conversationId = conversationIdElement.dataset.conversationId;
        initFileDragAndDrop(conversationId);
    }
});

// Функция для drag-and-drop
function initFileDragAndDrop(conversationId) {
    const dropZone = document.querySelector('.chat-area');
    if (!dropZone) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropZone.classList.add('drag-over');
    }

    function unhighlight() {
        dropZone.classList.remove('drag-over');
    }

    dropZone.addEventListener('drop', handleDrop, false);

    async function handleDrop(e) {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const formData = new FormData();
            formData.append('file', files[0]);
            try {
                const response = await fetch(`/chat/upload/${conversationId}/`, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });
                if (!response.ok) throw new Error('Upload failed');
                const data = await response.json();
                console.log('File uploaded:', data);
            } catch (error) {
                console.error('Upload error:', error);
                alert('Не удалось загрузить файл');
            }
        }
    }

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
}