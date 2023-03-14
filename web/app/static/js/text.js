const buttons = document.querySelectorAll('.button-form');
buttons.forEach(btn => {
    btn.addEventListener('mouseenter', function(e){
        let x = e.clientX - e.target.offsetLeft;
        let y = e.clientY - e.target.offsetTop;

        let ripples = document.createElement('spen');
        ripples.classList.add('btn-form');
        ripples.style.left = x + 'px';
        ripples.style.top = y + 'px';
        this.appendChild(ripples);

        setTimeout(() => {
            ripples.remove()
        },700);
    });
})