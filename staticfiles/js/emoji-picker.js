function initEmojiPicker() {
    const picker = document.getElementById('emoji-picker');
    const textarea = document.getElementById('chat-message');
    if (!picker || !textarea) return;

    picker.innerHTML = '';

    const emojis = [
        '😀', '😂', '😍', '😎', '😢', '😡', '👍', '👎', '❤️', '🔥', '✅', '❌',
        '😊', '🥳', '😇', '🤔', '😴', '🥺', '😱', '🤯', '🥶', '🤗', '🤭', '😏',
        '🎉', '🎊', '🎂', '🎈', '🎁', '🎀', '🎨', '🎭', '🎤', '🎧', '🎸', '🥁',
        '🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐨', '🐸', '🐒', '🐔',
        '🍏', '🍎', '🍐', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓', '🫐', '🍒', '🍑',
        '⚽', '🏀', '🏈', '⚾', '🎾', '🏐', '🏉', '🎱', '🏓', '🏸', '🥊', '🥋',
        '📱', '💻', '⌨️', '🖥️', '🖨️', '📷', '📹', '🎥', '📞', '📟', '📠', '🔋'
    ];

    emojis.forEach(e => {
        const span = document.createElement('span');
        span.textContent = e;
        span.addEventListener('click', () => {
            textarea.value += e;
            picker.style.display = 'none';
        });
        picker.appendChild(span);
    });

    let emojiButton = document.querySelector('.emoji-button');
    if (!emojiButton) {
        emojiButton = document.createElement('button');
        emojiButton.innerHTML = '😊';
        emojiButton.type = 'button';
        emojiButton.className = 'emoji-button';
        textarea.parentNode.insertBefore(emojiButton, textarea.nextSibling);
    }

    emojiButton.addEventListener('click', (e) => {
        e.stopPropagation();
        picker.style.display = picker.style.display === 'grid' ? 'none' : 'grid';
    });

    document.addEventListener('click', (e) => {
        if (!picker.contains(e.target) && e.target !== emojiButton) {
            picker.style.display = 'none';
        }
    });
}