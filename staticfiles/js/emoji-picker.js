function initEmojiPicker() {
    const picker = document.getElementById('emoji-picker');
    const textarea = document.getElementById('chat-message');
    if (!picker || !textarea) return;

    // Очищаем пикер (на случай повторной инициализации)
    picker.innerHTML = '';

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

    // Кнопка для открытия пикера (создаётся один раз)
    let emojiButton = document.querySelector('.emoji-button');
    if (!emojiButton) {
        emojiButton = document.createElement('button');
        emojiButton.innerHTML = '😊';
        emojiButton.type = 'button';
        emojiButton.className = 'emoji-button';
        // Вставляем после textarea
        textarea.parentNode.insertBefore(emojiButton, textarea.nextSibling);
    }

    emojiButton.addEventListener('click', (e) => {
        e.stopPropagation();
        picker.style.display = picker.style.display === 'grid' ? 'none' : 'grid';
    });

    // Закрывать при клике вне пикера
    document.addEventListener('click', (e) => {
        if (!picker.contains(e.target) && e.target !== emojiButton) {
            picker.style.display = 'none';
        }
    });
}