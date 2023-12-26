const items = document.getElementsByClassName('likes-section')

for (let item of items) {
    const [counter, button, disbutton] = item.children;
    disbutton.addEventListener('click', () => {
        counter.innerHTML = Number(counter.innerHTML) + 1
    })
    button.addEventListener('click', () => {
        alert('Hi');
    })
}