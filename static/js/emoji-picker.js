function initEmojiPicker() {
    const picker = document.getElementById('emoji-picker');
    const textarea = document.getElementById('chat-message');
    const emojiButton = document.createElement('button');
    emojiButton.innerHTML = '😊';
    emojiButton.type = 'button';
    emojiButton.style.background = 'none';
    emojiButton.style.fontSize = '1.5rem';
    emojiButton.style.width = '44px';
    emojiButton.style.height = '44px';
    emojiButton.style.borderRadius = '50%';
    emojiButton.style.border = 'none';
    emojiButton.style.cursor = 'pointer';
    emojiButton.addEventListener('click', () => {
        picker.style.display = picker.style.display === 'grid' ? 'none' : 'grid';
    });

    // Вставить кнопку рядом с полем ввода (после textarea)
    textarea.parentNode.insertBefore(emojiButton, textarea.nextSibling);

    // Простой набор эмодзи
    const emojis = ['😀', '😂', '😍', '😎', '😢', '😡', '👍', '👎', '❤️', '🔥', '✅', '❌'];
    emojis.forEach(e => {
        const span = document.createElement('span');
        span.textContent = e;
        span.addEventListener('click', () => {
            textarea.value += e;
            picker.style.display = 'none';
        });
        picker.appendChild(span);
    });
}