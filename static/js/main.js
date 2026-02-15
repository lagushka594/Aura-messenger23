document.addEventListener('DOMContentLoaded', function() {
    // Инициализируем сокет статусов, если пользователь авторизован
    if (document.querySelector('.user-menu')) {
        initStatusSocket();
    }

    // Обработчик отправки сообщения
    const sendBtn = document.getElementById('send-message');
    if (sendBtn) {
        sendBtn.addEventListener('click', function() {
            const input = document.getElementById('chat-message');
            if (input.value.trim()) {
                sendMessage(input.value);
                input.value = '';
            }
        });
        // Отправка по Enter (Shift+Enter для новой строки)
        const input = document.getElementById('chat-message');
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendBtn.click();
            }
        });
    }
});