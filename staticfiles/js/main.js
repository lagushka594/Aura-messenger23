document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.user-menu')) {
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
});