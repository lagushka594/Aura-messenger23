function initEmojiPicker() {
    const picker = document.getElementById('emoji-picker');
    const textarea = document.getElementById('chat-message');
    if (!picker || !textarea) return;

    // Расширенный набор эмодзи
    const emojis = [
        '😀', '😂', '😍', '😎', '😢', '😡', '👍', '👎', '❤️', '🔥', '✅', '❌',
        '😊', '🥳', '😇', '🤔', '😴', '🥺', '😱', '🤯', '🥶', '🤗', '🤭', '😏',
        '🎉', '🎊', '🎂', '🎈', '🎁', '🎀', '🎨', '🎭', '🎤', '🎧', '🎸', '🥁',
        '🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐨', '🐸', '🐒', '🐔',
        '🍏', '🍎', '🍐', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓', '🫐', '🍒', '🍑',
        '⚽', '🏀', '🏈', '⚾', '🎾', '🏐', '🏉', '🎱', '🏓', '🏸', '🥊', '🥋',
        '📱', '💻', '⌨️', '🖥️', '🖨️', '📷', '📹', '🎥', '📞', '📟', '📠', '🔋'
    ];

    // Создаём кнопку для открытия пикера
    const emojiButton = document.createElement('button');
    emojiButton.innerHTML = '😊';
    emojiButton.type = 'button';
    emojiButton.className = 'emoji-button';
    textarea.parentNode.insertBefore(emojiButton, textarea.nextSibling);

    emojiButton.addEventListener('click', () => {
        picker.style.display = picker.style.display === 'grid' ? 'none' : 'grid';
    });

    // Заполняем пикер
    emojis.forEach(e => {
        const span = document.createElement('span');
        span.textContent = e;
        span.addEventListener('click', () => {
            textarea.value += e;
            picker.style.display = 'none';
        });
        picker.appendChild(span);
    });

    // Закрывать при клике вне пикера
    document.addEventListener('click', (e) => {
        if (!picker.contains(e.target) && e.target !== emojiButton) {
            picker.style.display = 'none';
        }
    });
}