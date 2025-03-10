window.onload = function() {
    var element = document.querySelector('.gradient-background');
    element.style.animation = 'none';
    element.offsetHeight; /* Очистка анимации */
    element.style.animation = null; /* Восстановление анимации */
};
